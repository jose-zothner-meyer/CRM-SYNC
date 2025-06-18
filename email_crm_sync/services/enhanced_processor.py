"""
Enhanced Email Processor that uses only working Zoho API search methods.

This version:
1. Uses only word search (which works)
2. Implements intelligent fallback strategies
3. Guarantees note creation on every email
4. Optimized for reliability over precision matching
"""

import logging
from typing import Dict, Optional, List
from email_crm_sync.utils.email_utils import extract_email

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedEmailProcessor:
    """Enhanced processor that works around Zoho API limitations"""
    
    def __init__(self, gmail, openai, zoho):
        self.gmail = gmail
        self.openai = openai
        self.zoho = zoho
        self.processed_label_id = self.gmail.create_label_if_not_exists("Processed")
        
        # Cache for accounts to reduce API calls
        self._accounts_cache = None
        self._cache_populated = False

    def process_emails(self):
        """Main processing loop for new emails"""
        emails = self.gmail.get_starred_emails()  # or get_new_emails() for all new emails
        
        logger.info("Found %d emails to process", len(emails))
        
        for msg in emails:
            try:
                self._process_single_email(msg['id'])
            except Exception as e:
                logger.error("Error processing email %s: %s", msg['id'], e)

    def _process_single_email(self, msg_id: str):
        """Process a single email with enhanced reliability"""
        
        # Get email details
        detail = self.gmail.get_message_detail(msg_id)
        email_content = self.gmail.extract_enhanced_email_content(detail)
        
        gmail_message_id = email_content['gmail_message_id']
        logger.info("Processing email: %.50s... (Gmail ID: %s)", email_content['subject'], gmail_message_id)
        
        # Check if email already processed
        if hasattr(self.zoho, 'check_email_already_processed'):
            if self.zoho.check_email_already_processed(gmail_message_id):
                logger.info("✅ Email already processed, skipping: %s", gmail_message_id)
                return
        
        # Extract development information AND summary using OpenAI (single API call)
        openai_result = self.openai.extract_development_info_and_summary(
            email_content['subject'], 
            email_content['body']
        )
        
        # Split the result
        development_info = {k: v for k, v in openai_result.items() if k != 'summary'}
        email_summary = openai_result.get('summary', f"Email: {email_content['subject']}")
        
        # Find matching development using ONLY working search methods
        match_result = self._find_matching_development_smart(email_content, development_info)
        
        # Create note with appropriate strategy
        note_result = self._create_note_with_strategy(
            match_result, 
            email_content, 
            email_summary, 
            gmail_message_id
        )
        
        if note_result['success']:
            # Process and upload attachments
            self._process_email_attachments(email_content, note_result['development_id'])
            
            # Mark email as processed
            self.gmail.add_processed_label(msg_id, self.processed_label_id)
            logger.info("✅ Email processed successfully: %s", note_result['message'])
        else:
            logger.error("❌ Failed to process email: %s", note_result.get('error', 'Unknown error'))

    def _find_matching_development_smart(self, email_content: Dict, development_info: Dict) -> Dict:
        """
        Smart development matching using only working search methods.
        
        Returns:
            Dict with 'found', 'development_id', 'method', and 'confidence' keys
        """
        
        # Strategy 1: Search by sender email parts
        sender_emails = email_content.get('email_addresses', {}).get('from', [])
        for sender_email in sender_emails:
            if sender_email and '@' in sender_email:
                # Try domain search
                domain = sender_email.split('@')[1]
                results = self._word_search_safe(domain)
                if results:
                    return {
                        'found': True,
                        'development_id': results[0]['id'],
                        'development_name': results[0].get('Account_Name', 'Unknown'),
                        'method': f'Email domain: {domain}',
                        'confidence': 'high'
                    }
                
                # Try username search
                username = sender_email.split('@')[0]
                if len(username) > 3:  # Avoid too generic searches
                    results = self._word_search_safe(username)
                    if results:
                        return {
                            'found': True,
                            'development_id': results[0]['id'],
                            'development_name': results[0].get('Account_Name', 'Unknown'),
                            'method': f'Email username: {username}',
                            'confidence': 'medium'
                        }
        
        # Strategy 2: Search by property address parts
        if development_info.get('property_address'):
            address = development_info['property_address']
            match_result = self._search_by_address_parts(address)
            if match_result['found']:
                return match_result
        
        # Strategy 3: Search by company/client name
        if development_info.get('client_name'):
            match_result = self._search_by_company_parts(development_info['client_name'])
            if match_result['found']:
                return match_result
        
        # Strategy 4: Search by development name
        if development_info.get('development_name'):
            match_result = self._search_by_company_parts(development_info['development_name'])
            if match_result['found']:
                return match_result
        
        # Strategy 5: Search email subject for meaningful terms
        subject = email_content.get('subject', '')
        if subject:
            match_result = self._search_subject_keywords(subject)
            if match_result['found']:
                return match_result
        
        return {'found': False, 'method': 'no_match', 'confidence': 'none'}

    def _word_search_safe(self, term: str, max_results: int = 5) -> List[Dict]:
        """Safe word search that handles errors gracefully"""
        try:
            if not term or len(term) < 2:
                return []
            
            if hasattr(self.zoho, 'search_by_word'):
                results = self.zoho.search_by_word(term)
                return results[:max_results] if results else []
            else:
                logger.warning("search_by_word method not available in Zoho client")
                return []
                
        except Exception as e:
            logger.warning("Word search failed for '%s': %s", term, str(e))
            return []

    def _search_by_address_parts(self, address: str) -> Dict:
        """Search for address by breaking it into meaningful parts"""
        if not address:
            return {'found': False}
        
        # Extract meaningful address parts
        address_parts = self._extract_address_keywords(address)
        
        for i, part in enumerate(address_parts[:3]):  # Try first 3 parts
            results = self._word_search_safe(part)
            if results:
                return {
                    'found': True,
                    'development_id': results[0]['id'],
                    'development_name': results[0].get('Account_Name', 'Unknown'),
                    'method': f'Address part: {part}',
                    'confidence': 'high' if i == 0 else 'medium'
                }
        
        return {'found': False}

    def _search_by_company_parts(self, company_name: str) -> Dict:
        """Search for company by breaking name into parts"""
        if not company_name:
            return {'found': False}
        
        # Extract meaningful company name parts
        company_parts = self._extract_company_keywords(company_name)
        
        for i, part in enumerate(company_parts[:2]):  # Try first 2 parts
            results = self._word_search_safe(part)
            if results:
                return {
                    'found': True,
                    'development_id': results[0]['id'],
                    'development_name': results[0].get('Account_Name', 'Unknown'),
                    'method': f'Company part: {part}',
                    'confidence': 'high' if i == 0 else 'medium'
                }
        
        return {'found': False}

    def _search_subject_keywords(self, subject: str) -> Dict:
        """Extract and search keywords from email subject"""
        if not subject:
            return {'found': False}
        
        # Extract meaningful keywords from subject
        keywords = self._extract_subject_keywords(subject)
        
        for keyword in keywords[:3]:  # Try first 3 keywords
            results = self._word_search_safe(keyword)
            if results:
                return {
                    'found': True,
                    'development_id': results[0]['id'],
                    'development_name': results[0].get('Account_Name', 'Unknown'),
                    'method': f'Subject keyword: {keyword}',
                    'confidence': 'low'
                }
        
        return {'found': False}

    def _extract_address_keywords(self, address: str) -> List[str]:
        """Extract meaningful keywords from address"""
        # Remove common address words
        common_words = {
            'road', 'street', 'avenue', 'lane', 'drive', 'close', 'gardens', 
            'estate', 'of', 'the', 'and', 'house', 'flat', 'apartment'
        }
        
        # Clean and split address
        words = address.lower().replace(',', ' ').replace('-', ' ').split()
        
        # Extract meaningful parts
        keywords = []
        for word in words:
            if len(word) > 2 and word not in common_words and not word.isdigit():
                keywords.append(word.title())
        
        return keywords

    def _extract_company_keywords(self, company_name: str) -> List[str]:
        """Extract meaningful keywords from company name"""
        # Remove common business words
        common_business_words = {
            'ltd', 'limited', 'plc', 'llc', 'inc', 'corp', 'corporation', 
            'company', 'co', 'group', 'holdings', 'development', 'developments'
        }
        
        # Clean and split company name
        words = company_name.lower().replace(',', ' ').replace('-', ' ').split()
        
        # Extract meaningful parts
        keywords = []
        for word in words:
            if len(word) > 2 and word not in common_business_words:
                keywords.append(word.title())
        
        return keywords

    def _extract_subject_keywords(self, subject: str) -> List[str]:
        """Extract meaningful keywords from email subject"""
        # Remove common email words
        common_email_words = {
            're', 'fwd', 'fw', 'reply', 'regarding', 'about', 'email', 'message',
            'urgent', 'important', 'please', 'thanks', 'thank', 'you', 'update'
        }
        
        # Clean and split subject
        words = subject.lower().replace('re:', '').replace('fwd:', '').replace(',', ' ').split()
        
        # Extract meaningful parts
        keywords = []
        for word in words:
            if len(word) > 3 and word not in common_email_words and not word.isdigit():
                keywords.append(word.title())
        
        return keywords

    def _create_note_with_strategy(self, match_result: Dict, email_content: Dict, 
                                  email_summary: str, gmail_message_id: str) -> Dict:
        """Create note using the best available strategy"""
        
        subject = email_content['subject']
        
        # Ensure note title doesn't exceed 120 characters
        max_title_length = 110  # Leave some buffer
        
        if match_result['found']:
            # Strategy 1: Create note on matched development
            development_id = match_result['development_id']
            development_name = match_result.get('development_name', 'Unknown')
            method = match_result['method']
            
            note_title = f"Email: {subject}"
            if len(note_title) > max_title_length:
                note_title = f"Email: {subject[:max_title_length-8]}..."
                
            note_content = f"""Email Summary:
{email_summary}

Matching Method: {method}
Gmail Message ID: {gmail_message_id}
Processed: {self._get_timestamp()}
"""
            
            result = self._create_note_safe(development_id, note_title, note_content)
            if result['success']:
                return {
                    'success': True,
                    'development_id': development_id,
                    'message': f"Note created on matched development: {development_name} (via {method})",
                    'note_id': result.get('note_id')
                }
        
        # Strategy 2: Fallback - create note on first available account
        return self._create_fallback_note(email_content, email_summary, gmail_message_id, 
                                        match_result.get('method', 'no_match'))

    def _create_note_safe(self, development_id: str, title: str, content: str) -> Dict:
        """Safely create a note with error handling"""
        try:
            if hasattr(self.zoho, 'create_note_with_email_tracking'):
                result = self.zoho.create_note_with_email_tracking(
                    development_id=development_id,
                    email_summary=content,
                    gmail_message_id=title,  # Using title as identifier
                    email_subject=title
                )
            else:
                result = self.zoho.add_note_to_development(development_id, title, content)
            
            if self._is_success_response(result):
                return {'success': True, 'note_id': self._extract_note_id(result)}
            else:
                return {'success': False, 'error': f"API returned failure: {result}"}
                
        except Exception as e:
            return {'success': False, 'error': f"Exception: {str(e)}"}

    def _create_fallback_note(self, email_content: Dict, email_summary: str, 
                            gmail_message_id: str, attempted_method: str) -> Dict:
        """Create note on first available account as fallback"""
        try:
            # Get first available account
            if not self._cache_populated:
                self._populate_accounts_cache()
            
            if not self._accounts_cache:
                return {
                    'success': False, 
                    'error': 'No accounts available for fallback note creation'
                }
            
            account = self._accounts_cache[0]
            account_id = account['id']
            account_name = account.get('Account_Name', 'Unknown')
            
            subject = email_content['subject']
            note_title = f"Email (Unmatched): {subject}"
            
            # Ensure note title doesn't exceed 120 characters
            max_title_length = 110  # Leave some buffer
            if len(note_title) > max_title_length:
                note_title = f"Email (Unmatched): {subject[:max_title_length-18]}..."
            
            note_content = f"""Email Summary:
{email_summary}

⚠️ FALLBACK NOTE: Could not find specific matching development
Attempted Method: {attempted_method}
Gmail Message ID: {gmail_message_id}
Processed: {self._get_timestamp()}

This email was processed but no specific development match was found.
Please review and reassign if needed.
"""
            
            result = self._create_note_safe(account_id, note_title, note_content)
            if result['success']:
                return {
                    'success': True,
                    'development_id': account_id,
                    'message': f"Fallback note created on account: {account_name}",
                    'note_id': result.get('note_id')
                }
            else:
                return {
                    'success': False,
                    'error': f"Fallback note creation failed: {result.get('error')}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Fallback note creation error: {str(e)}"
            }

    def _populate_accounts_cache(self):
        """Populate the accounts cache for fallback operations"""
        try:
            if hasattr(self.zoho, 'get_all_records'):
                accounts = self.zoho.get_all_records(limit=10)
            else:
                # Use direct API call
                response = self.zoho.session.get(
                    f"{self.zoho.base_url}/{self.zoho.developments_module}",
                    params={'fields': 'id,Account_Name', 'per_page': 10},
                    timeout=30
                )
                if response.status_code == 200:
                    data = response.json()
                    accounts = data.get('data', [])
                else:
                    accounts = []
            
            self._accounts_cache = accounts if accounts else []
            self._cache_populated = True
            
            logger.info("Populated accounts cache with %d accounts", len(self._accounts_cache))
            
        except Exception as e:
            logger.error("Error populating accounts cache: %s", str(e))
            self._accounts_cache = []
            self._cache_populated = True

    def _is_success_response(self, response: Dict) -> bool:
        """Check if Zoho API response indicates success"""
        if isinstance(response, dict):
            if 'data' in response and len(response['data']) > 0:
                return response['data'][0].get('status') == 'success'
            elif 'success' in response:
                return response['success']
        return False

    def _extract_note_id(self, response: Dict) -> Optional[str]:
        """Extract note ID from Zoho API response"""
        try:
            if 'data' in response and len(response['data']) > 0:
                return response['data'][0].get('details', {}).get('id')
            return None
        except (KeyError, IndexError, TypeError):
            return None

    def _get_timestamp(self) -> str:
        """Get current timestamp for notes"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def _process_email_attachments(self, email_content: Dict, development_id: str):
        """Process and upload email attachments to the development record"""
        attachments = email_content.get('attachments', [])
        
        if not attachments:
            logger.info("No attachments found in email")
            return
        
        logger.info("Processing %d attachments for development %s", len(attachments), development_id)
        
        try:
            # Download attachments from Gmail
            gmail_message = {'id': email_content['gmail_message_id']}
            downloaded_files = self.gmail.process_attachments_for_crm(gmail_message)
            
            # Upload each attachment to Zoho CRM
            for file_path in downloaded_files:
                try:
                    result = self.zoho.upload_attachment(file_path, development_id)
                    
                    if result.get('success'):
                        logger.info("✅ Uploaded attachment: %s", file_path.split('/')[-1])
                    else:
                        logger.error("❌ Failed to upload attachment %s: %s", 
                                   file_path.split('/')[-1], result.get('error'))
                        
                except Exception as e:
                    logger.error("Error uploading attachment %s: %s", file_path, str(e))
            
            # Clean up temporary files
            self._cleanup_temp_files(downloaded_files)
            
        except Exception as e:
            logger.error("Error processing email attachments: %s", str(e))

    def _cleanup_temp_files(self, file_paths: List[str]):
        """Clean up temporary attachment files"""
        import os
        
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.debug("Cleaned up temp file: %s", file_path)
            except Exception as e:
                logger.warning("Could not clean up temp file %s: %s", file_path, str(e))

    def process_specific_email(self, msg_id: str):
        """Process a specific email by ID"""
        try:
            self._process_single_email(msg_id)
        except Exception as e:
            logger.error("Error processing specific email %s: %s", msg_id, e)
