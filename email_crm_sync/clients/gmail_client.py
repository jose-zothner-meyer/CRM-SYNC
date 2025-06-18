from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
import os
import pickle
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class GmailClient:
    def __init__(self, credentials_path: str):
        """
        Initialize Gmail client with OAuth2 flow.
        
        Follows Gmail API best practices from:
        https://developers.google.com/gmail/api/auth/scopes
        
        Args:
            credentials_path: Path to the client credentials JSON file
        """
        self.credentials_path = credentials_path
        
        # Official Gmail API scopes - using minimal required permissions
        # https://developers.google.com/gmail/api/auth/scopes
        self.scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',  # Read-only access to emails
            'https://www.googleapis.com/auth/gmail.modify'     # Modify labels (for marking processed)
        ]
        self.creds = self._get_credentials()
        self.service = build('gmail', 'v1', credentials=self.creds)
        logger.info("Gmail client initialized successfully")
    
    def _get_credentials(self):
        """Handle the OAuth2 flow and return valid credentials."""
        creds = None
        # Store token in the same directory as credentials
        credentials_dir = os.path.dirname(self.credentials_path)
        token_path = os.path.join(credentials_dir, 'gmail_token.pickle')
        
        # Load existing token if available
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    logger.info("Refreshed Gmail credentials")
                except Exception as e:
                    logger.warning(f"Failed to refresh credentials: {e}, starting new OAuth flow")
                    creds = None
            
            if not creds:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.scopes)
                creds = flow.run_local_server(port=0)
                logger.info("Completed Gmail OAuth2 flow")
            
            # Save the credentials for the next run
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
                logger.info("Saved Gmail credentials for future use")
        
        return creds

    def get_new_emails(self, query: str = "is:unread") -> List[Dict]:
        """Get new/unread emails based on query"""
        response = self.service.users().messages().list(
            userId='me', q=f"{query} -label:Processed").execute()
        return response.get('messages', [])

    def get_starred_emails(self) -> List[Dict]:
        """Get starred emails that haven't been processed"""
        response = self.service.users().messages().list(
            userId='me', labelIds=['STARRED'], q='-label:Processed').execute()
        return response.get('messages', [])

    def get_message_detail(self, msg_id: str) -> Dict:
        """Get detailed message information"""
        return self.service.users().messages().get(
            userId='me', id=msg_id, format='full').execute()

    def extract_email_content(self, message: Dict) -> Dict:
        """Extract readable content from Gmail message"""
        headers = message['payload']['headers']
        
        # Extract basic headers
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
        
        # Extract body content
        body = self._extract_body(message['payload'])
        
        return {
            'id': message['id'],
            'subject': subject,
            'sender': sender,
            'date': date,
            'body': body,
            'snippet': message.get('snippet', '')
        }

    def _extract_body(self, payload: Dict) -> str:
        """Extract body text from message payload"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif part['mimeType'] == 'text/html' and not body:
                    # Use HTML as fallback if no plain text
                    if 'data' in part['body']:
                        body += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        else:
            if payload['mimeType'] == 'text/plain' and 'data' in payload['body']:
                body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        return body

    def add_processed_label(self, msg_id: str, label_id: str = 'Label_Processed'):
        """Add processed label to email"""
        try:
            self.service.users().messages().modify(
                userId='me', id=msg_id, body={'addLabelIds': [label_id]}).execute()
        except Exception as e:  # noqa: BLE001
            print(f"Warning: Could not add label to message {msg_id}: {e}")

    def create_label_if_not_exists(self, label_name: str = "Processed") -> str:
        """Create the Processed label if it doesn't exist"""
        try:
            labels = self.service.users().labels().list(userId='me').execute()
            for label in labels.get('labels', []):
                if label['name'] == label_name:
                    return label['id']
            
            # Create the label
            label_object = {
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            created_label = self.service.users().labels().create(
                userId='me', body=label_object).execute()
            return created_label['id']
        except Exception as e:  # noqa: BLE001
            print(f"Warning: Could not create/find label: {e}")
            return "Label_Processed"  # Fallback

    def get_message_id(self, message: Dict) -> str:
        """
        Extract the Gmail message ID for tracking and duplicate prevention.
        
        Args:
            message: Gmail message object
            
        Returns:
            Gmail message ID string
        """
        return message.get('id', '')
    
    def get_attachments(self, message: Dict) -> List[Dict]:
        """
        Extract attachment information from Gmail message.
        
        Args:
            message: Gmail message object
            
        Returns:
            List of attachment dictionaries with metadata
        """
        attachments = []
        
        def process_part(part):
            if part.get('filename') and part.get('body', {}).get('attachmentId'):
                attachment_info = {
                    'filename': part['filename'],
                    'attachment_id': part['body']['attachmentId'],
                    'mime_type': part.get('mimeType', 'application/octet-stream'),
                    'size': part.get('body', {}).get('size', 0)
                }
                attachments.append(attachment_info)
            
            # Recursively process parts if they exist
            if 'parts' in part:
                for subpart in part['parts']:
                    process_part(subpart)
        
        # Process the message payload
        if 'payload' in message:
            process_part(message['payload'])
        
        return attachments
    
    def download_attachment(self, msg_id: str, attachment_id: str, filename: str, download_path: str) -> str:
        """
        Download an attachment from Gmail and save to local file.
        
        Args:
            msg_id: Gmail message ID
            attachment_id: Gmail attachment ID
            filename: Original filename of the attachment
            download_path: Directory to save the attachment
            
        Returns:
            Full path to the downloaded file
        """
        try:
            import os
            
            # Get attachment data
            attachment = self.service.users().messages().attachments().get(
                userId='me', messageId=msg_id, id=attachment_id).execute()
            
            # Decode attachment data
            file_data = base64.urlsafe_b64decode(attachment['data'])
            
            # Create download directory if it doesn't exist
            os.makedirs(download_path, exist_ok=True)
            
            # Generate safe filename
            safe_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_', '-')).rstrip()
            file_path = os.path.join(download_path, safe_filename)
            
            # Write file
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            return file_path
            
        except Exception as e:
            print(f"Error downloading attachment {filename}: {e}")
            return ""
    
    def extract_email_addresses(self, message: Dict) -> Dict[str, List[str]]:
        """
        Extract all email addresses from Gmail message headers.
        
        Args:
            message: Gmail message object
            
        Returns:
            Dictionary with 'from', 'to', 'cc', 'bcc' email lists
        """
        headers = message.get('payload', {}).get('headers', [])
        email_addresses = {
            'from': [],
            'to': [],
            'cc': [],
            'bcc': []
        }
        
        for header in headers:
            header_name = header['name'].lower()
            header_value = header['value']
            
            if header_name == 'from':
                email_addresses['from'] = self._parse_email_addresses(header_value)
            elif header_name == 'to':
                email_addresses['to'] = self._parse_email_addresses(header_value)
            elif header_name == 'cc':
                email_addresses['cc'] = self._parse_email_addresses(header_value)
            elif header_name == 'bcc':
                email_addresses['bcc'] = self._parse_email_addresses(header_value)
        
        return email_addresses
    
    def _parse_email_addresses(self, header_value: str) -> List[str]:
        """
        Parse email addresses from header value string.
        
        Args:
            header_value: Raw header value containing email addresses
            
        Returns:
            List of email addresses
        """
        import re
        
        # Regular expression to match email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, header_value)
    
    def extract_enhanced_email_content(self, message: Dict) -> Dict:
        """
        Enhanced email content extraction with additional metadata for CRM sync.
        
        Args:
            message: Gmail message object
            
        Returns:
            Enhanced email content dictionary with CRM-relevant information
        """
        # Get basic email content
        basic_content = self.extract_email_content(message)
        
        # Add enhanced metadata
        enhanced_content = {
            **basic_content,
            'gmail_message_id': self.get_message_id(message),
            'thread_id': message.get('threadId', ''),
            'label_ids': message.get('labelIds', []),
            'attachments': self.get_attachments(message),
            'email_addresses': self.extract_email_addresses(message),
            'internal_date': message.get('internalDate', ''),
            'size_estimate': message.get('sizeEstimate', 0)
        }
        
        return enhanced_content
    
    def process_attachments_for_crm(self, message: Dict, download_dir: str = "./temp_attachments") -> List[str]:
        """
        Download all attachments from an email for CRM upload.
        
        Args:
            message: Gmail message object
            download_dir: Directory to temporarily store attachments
            
        Returns:
            List of local file paths for the downloaded attachments
        """
        msg_id = self.get_message_id(message)
        attachments = self.get_attachments(message)
        downloaded_files = []
        
        for attachment in attachments:
            try:
                file_path = self.download_attachment(
                    msg_id=msg_id,
                    attachment_id=attachment['attachment_id'],
                    filename=attachment['filename'],
                    download_path=download_dir
                )
                
                if file_path:
                    downloaded_files.append(file_path)
                    print(f"Downloaded attachment: {attachment['filename']}")
                    
            except Exception as e:
                print(f"Failed to download attachment {attachment['filename']}: {e}")
        
        return downloaded_files
    
    def get_message_headers(self, message: Dict) -> Dict[str, str]:
        """
        Extract all headers from Gmail message as a dictionary.
        
        Args:
            message: Gmail message object
            
        Returns:
            Dictionary of header name -> header value
        """
        headers = message.get('payload', {}).get('headers', [])
        header_dict = {}
        
        for header in headers:
            header_dict[header['name']] = header['value']
        
        return header_dict
    
    def is_reply_or_forward(self, message: Dict) -> Dict[str, bool]:
        """
        Determine if the email is a reply or forward.
        
        Args:
            message: Gmail message object
            
        Returns:
            Dictionary with 'is_reply' and 'is_forward' boolean flags
        """
        headers = self.get_message_headers(message)
        subject = headers.get('Subject', '').lower()
        
        is_reply = (
            subject.startswith('re:') or 
            'In-Reply-To' in headers or 
            'References' in headers
        )
        
        is_forward = (
            subject.startswith('fwd:') or 
            subject.startswith('fw:') or
            'forwarded' in subject
        )
        
        return {
            'is_reply': is_reply,
            'is_forward': is_forward
        }
