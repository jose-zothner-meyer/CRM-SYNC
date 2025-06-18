import openai  # type: ignore
from typing import Dict, Optional, List
import json
import logging
import re

logger = logging.getLogger(__name__)

class EnhancedOpenAIProcessor:
    """
    Enhanced OpenAI client for property development email processing.
    
    Provides:
    - Intelligent email classification
    - Comprehensive data extraction
    - Urgency and sentiment analysis
    - Smart semantic matching
    - Robust error handling
    """
    
    def __init__(self, api_key: str, model_settings: Optional[dict] = None):
        """
        Initialize OpenAI client with configurable model settings.
        :param api_key: OpenAI API key
        :param model_settings: dict with keys: chat_model, semantic_model, max_tokens, temperature
        """
        self.client = openai.OpenAI(api_key=api_key)  # type: ignore
        # Load model settings from provided dict or from env defaults
        if model_settings:
            cfg = model_settings
        else:
            import os
            cfg = {
                'chat_model': os.getenv('OPENAI_CHAT_MODEL', 'gpt-4o-mini'),
                'semantic_model': os.getenv('OPENAI_SEMANTIC_MODEL', 'gpt-4'),
                'max_tokens': int(os.getenv('OPENAI_MAX_TOKENS', '800')),
                'temperature': float(os.getenv('OPENAI_TEMPERATURE', '0.1'))
            }
        # Assign settings
        self.chat_model = cfg.get('chat_model', 'gpt-4o-mini')
        self.semantic_model = cfg.get('semantic_model', 'gpt-4')
        self.max_tokens = cfg.get('max_tokens', 800)
        self.temperature = cfg.get('temperature', 0.1)
        
        # Email type classifications
        self.email_types = [
            'inquiry','update','complaint','payment','documentation',
            'meeting','site_visit','legal','technical','marketing','other'
        ]
        # Urgency levels
        self.urgency_levels = ['low','medium','high','critical']
        # Sentiment categories
        self.sentiment_categories = ['positive','neutral','negative','mixed']

    def process_email_comprehensive(self, subject: str, body: str, sender_email: Optional[str] = None) -> Dict:
        """
        Comprehensive email processing with classification, extraction, and analysis.
        
        Returns a complete analysis including:
        - Email classification and type
        - Extracted property/development data
        - Urgency and sentiment analysis
        - Professional summary
        - Keywords for matching
        - Action items and next steps
        """
        
        system_prompt = """You are an AI assistant specialized in property development email processing. 
You work for a property development company and analyze incoming emails to extract relevant information.

Your task is to analyze emails and return a comprehensive JSON response with the following structure:

{
    "email_type": "one of: inquiry, update, complaint, payment, documentation, meeting, site_visit, legal, technical, marketing, other",
    "urgency": "one of: low, medium, high, critical",
    "sentiment": "one of: positive, neutral, negative, mixed",
    "property_address": "full property address if mentioned, null if not found",
    "development_name": "project/development name if mentioned, null if not found",
    "client_name": "client or contact person name, null if not found",
    "company_name": "company or organization name, null if not found",
    "phone_number": "phone number if found, null if not found",
    "email_address": "email address if different from sender, null if not found",
    "keywords": ["list", "of", "important", "keywords", "for", "matching"],
    "action_items": ["list", "of", "action", "items", "or", "requests"],
    "next_steps": "what needs to happen next based on email content",
    "summary": "concise professional summary (150-200 words max)",
    "confidence_score": "float between 0.0-1.0 indicating extraction confidence"
}

Guidelines:
- Email type should reflect the primary purpose of the email
- Urgency should be based on language used and deadlines mentioned
- Sentiment should reflect the overall tone of the sender
- Extract exact addresses and development names when possible
- Keywords should include location names, project names, company names
- Be conservative with extractions - use null if uncertain
- Summary should be professional and capture key points and context
- Confidence score should reflect how certain you are about the extractions"""

        user_prompt = f"""Analyze this property development email:

SUBJECT: {subject}

SENDER: {sender_email or 'Not provided'}

BODY:
{body}

Provide the comprehensive analysis in the exact JSON format specified."""

        try:
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[{'role':'system','content':system_prompt}, {'role':'user','content':user_prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Validate and sanitize the result
            return self._validate_and_sanitize_result(result, subject, body)
            
        except json.JSONDecodeError as e:
            logger.error("JSON decode error in email processing: %s", str(e))
            return self._create_fallback_result(subject, body)
        except (openai.OpenAIError, ValueError) as e:
            logger.error("Error in comprehensive email processing: %s", str(e))
            return self._create_fallback_result(subject, body)

    def extract_development_info_and_summary(self, subject: str, body: str) -> Dict:
        """
        Legacy method for backward compatibility.
        Uses the comprehensive processor but returns only the expected fields.
        """
        comprehensive_result = self.process_email_comprehensive(subject, body)
        
        return {
            "property_address": comprehensive_result.get("property_address"),
            "development_name": comprehensive_result.get("development_name"),
            "client_name": comprehensive_result.get("client_name"),
            "phone_number": comprehensive_result.get("phone_number"),
            "email_address": comprehensive_result.get("email_address"),
            "summary": comprehensive_result.get("summary")
        }

    def semantic_match_developments(self, email_analysis: Dict, developments: List[Dict], 
                                  top_n: int = 3) -> List[Dict]:
        """
        Use AI to semantically match email content with developments.
        
        Returns a ranked list of potential matches with confidence scores.
        """
        if not developments:
            return []
        
        # Prepare development information for matching
        dev_descriptions = []
        for dev in developments:
            desc = self._format_development_for_matching(dev)
            dev_descriptions.append(f"ID: {dev.get('id')}\n{desc}")
        
        # Create matching context
        email_context = self._format_email_for_matching(email_analysis)
        
        system_prompt = """You are an expert at matching property development emails to the correct development records.

Your task is to analyze the email content and rank the provided developments by how well they match.

Consider these factors:
1. Property address/location matches
2. Development/project name matches  
3. Client/contact name matches
4. Company name matches
5. Context and topic relevance

Return a JSON array of matches, ranked by confidence (highest first):
[
    {
        "development_id": "exact_id_from_list",
        "confidence_score": 0.95,
        "match_reasons": ["address match", "client name match"],
        "match_strength": "strong"
    }
]

Use match_strength values: "strong", "medium", "weak", "none"
Only include developments with confidence_score > 0.3
Limit to top 3 matches maximum."""

        user_prompt = f"""Email Analysis:
{email_context}

Available Developments:
{chr(10).join(dev_descriptions)}

Find the best matching developments and rank them by relevance."""

        try:
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            matches = json.loads(response.choices[0].message.content)
            
            # Validate matches
            valid_matches = []
            dev_ids = {dev.get('id') for dev in developments}
            
            for match in matches[:top_n]:
                if (isinstance(match, dict) and 
                    match.get('development_id') in dev_ids and
                    0.3 <= match.get('confidence_score', 0) <= 1.0):
                    valid_matches.append(match)
            
            return valid_matches
            
        except (json.JSONDecodeError, openai.OpenAIError, ValueError) as e:
            logger.error("Error in semantic matching: %s", str(e))
            return []

    def generate_smart_keywords(self, subject: str, body: str) -> List[str]:
        """
        Generate intelligent keywords for development matching.
        
        Returns keywords that are most likely to find relevant developments.
        """
        system_prompt = """You are an expert at extracting search keywords from property development emails.

Generate 5-10 keywords that would be most effective for finding the relevant development record in a CRM system.

Focus on:
- Property/location names (streets, areas, postcodes)
- Development/project names
- Company names
- Client surnames
- Unique identifiers

Return as JSON array: ["keyword1", "keyword2", ...]

Avoid generic words like: property, development, email, update, meeting, etc.
Prioritize specific, unique terms that would distinguish this email/project."""

        user_prompt = f"""Extract search keywords from this email:

SUBJECT: {subject}

BODY: {body}"""

        try:
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            keywords = json.loads(response.choices[0].message.content)
            
            # Validate and clean keywords
            if isinstance(keywords, list):
                clean_keywords = []
                for kw in keywords:
                    if isinstance(kw, str) and 2 < len(kw) < 50:
                        clean_keywords.append(kw.strip())
                return clean_keywords[:10]  # Limit to 10 keywords
            
        except (json.JSONDecodeError, openai.OpenAIError, ValueError) as e:
            logger.error("Error generating keywords: %s", str(e))
        
        # Fallback: simple keyword extraction
        return self._extract_fallback_keywords(subject, body)

    def summarize_email(self, subject: str, body: str) -> str:
        """Create a professional summary of the email for CRM notes"""
        comprehensive_result = self.process_email_comprehensive(subject, body)
        return comprehensive_result.get("summary", f"Email: {subject}")

    def extract_development_info(self, subject: str, body: str) -> Dict:
        """Legacy method for backward compatibility"""
        result = self.extract_development_info_and_summary(subject, body)
        if 'summary' in result:
            del result['summary']
        return result

    def find_matching_criteria(self, email_content: Dict, developments: list) -> Optional[str]:
        """Legacy method for backward compatibility"""
        # Use the new semantic matching but return only the top match ID
        email_analysis = {
            'summary': email_content.get('body', ''),
            'keywords': [email_content.get('subject', '')],
            'property_address': None,
            'development_name': None,
            'client_name': None
        }
        
        matches = self.semantic_match_developments(email_analysis, developments, top_n=1)
        
        if matches and matches[0].get('confidence_score', 0) > 0.5:
            return matches[0]['development_id']
        
        return None

    def _validate_and_sanitize_result(self, result: Dict, subject: str, body: str) -> Dict:  # pylint: disable=unused-argument
        """Validate and sanitize the comprehensive processing result"""
        
        # Ensure all required fields exist
        defaults = {
            "email_type": "other",
            "urgency": "medium",
            "sentiment": "neutral",
            "property_address": None,
            "development_name": None,
            "client_name": None,
            "company_name": None,
            "phone_number": None,
            "email_address": None,
            "keywords": [],
            "action_items": [],
            "next_steps": "Review and respond as appropriate",
            "summary": f"Email regarding: {subject}",
            "confidence_score": 0.5
        }
        
        # Apply defaults for missing fields
        for key, default_value in defaults.items():
            if key not in result:
                result[key] = default_value
        
        # Validate enums
        if result["email_type"] not in self.email_types:
            result["email_type"] = "other"
        
        if result["urgency"] not in self.urgency_levels:
            result["urgency"] = "medium"
        
        if result["sentiment"] not in self.sentiment_categories:
            result["sentiment"] = "neutral"
        
        # Validate confidence score
        try:
            confidence = float(result["confidence_score"])
            result["confidence_score"] = max(0.0, min(1.0, confidence))
        except (ValueError, TypeError):
            result["confidence_score"] = 0.5
        
        # Ensure lists are actually lists
        for list_field in ["keywords", "action_items"]:
            if not isinstance(result[list_field], list):
                result[list_field] = []
        
        # Clean phone number
        if result["phone_number"]:
            result["phone_number"] = self._clean_phone_number(result["phone_number"])
        
        # Validate email address
        if result["email_address"]:
            result["email_address"] = self._validate_email_address(result["email_address"])
        
        return result

    def _create_fallback_result(self, subject: str, body: str) -> Dict:
        """Create a fallback result when AI processing fails"""
        
        # Simple keyword extraction
        keywords = self._extract_fallback_keywords(subject, body)
        
        # Simple urgency detection
        urgency = self._detect_simple_urgency(subject, body)
        
        return {
            "email_type": "other",
            "urgency": urgency,
            "sentiment": "neutral",
            "property_address": None,
            "development_name": None,
            "client_name": None,
            "company_name": None,
            "phone_number": None,
            "email_address": None,
            "keywords": keywords,
            "action_items": [],
            "next_steps": "Review email manually for processing",
            "summary": f"Email: {subject}\n\nAutomated processing was unable to extract detailed information. Manual review recommended.",
            "confidence_score": 0.3
        }

    def _format_development_for_matching(self, dev: Dict) -> str:
        """Format development info for AI matching"""
        parts = []
        
        if dev.get('Deal_Name') or dev.get('Account_Name'):
            parts.append(f"Name: {dev.get('Deal_Name') or dev.get('Account_Name')}")
        
        if dev.get('Property_Address'):
            parts.append(f"Address: {dev.get('Property_Address')}")
        
        if dev.get('Contact_Name'):
            parts.append(f"Contact: {dev.get('Contact_Name')}")
        
        if dev.get('Account_Name') and dev.get('Deal_Name'):
            parts.append(f"Company: {dev.get('Account_Name')}")
        
        return "\n".join(parts) if parts else "Limited information available"

    def _format_email_for_matching(self, email_analysis: Dict) -> str:
        """Format email analysis for AI matching"""
        parts = [f"Subject: {email_analysis.get('summary', 'No summary')}"]
        
        if email_analysis.get('property_address'):
            parts.append(f"Property: {email_analysis['property_address']}")
        
        if email_analysis.get('development_name'):
            parts.append(f"Development: {email_analysis['development_name']}")
        
        if email_analysis.get('client_name'):
            parts.append(f"Client: {email_analysis['client_name']}")
        
        if email_analysis.get('company_name'):
            parts.append(f"Company: {email_analysis['company_name']}")
        
        if email_analysis.get('keywords'):
            parts.append(f"Keywords: {', '.join(email_analysis['keywords'][:5])}")
        
        return "\n".join(parts)

    def _extract_fallback_keywords(self, subject: str, body: str) -> List[str]:
        """Simple keyword extraction fallback"""
        text = f"{subject} {body}".lower()
        
        # Remove common words
        common_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'about', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'between', 'among', 'then', 'once', 
            'out', 'off', 'over', 'under', 'again', 'further', 'up', 'down',
            'email', 'please', 'thank', 'thanks', 'regards', 'best', 'dear', 
            'hello', 'hi'
        }
        
        # Extract words that might be useful
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
        keywords = []
        
        for word in words:
            if (word.lower() not in common_words and 
                len(word) > 2 and 
                not word.isdigit() and
                word.lower() not in keywords):
                keywords.append(word.title())
        
        return keywords[:8]  # Return up to 8 keywords

    def _detect_simple_urgency(self, subject: str, body: str) -> str:
        """Simple urgency detection based on keywords"""
        text = f"{subject} {body}".lower()
        
        critical_words = ['urgent', 'emergency', 'asap', 'immediately', 'critical', 'crisis']
        high_words = ['important', 'priority', 'deadline', 'soon', 'quickly']
        
        if any(word in text for word in critical_words):
            return "critical"
        elif any(word in text for word in high_words):
            return "high"
        else:
            return "medium"

    def _clean_phone_number(self, phone: str) -> Optional[str]:
        """Clean and validate phone number"""
        if not phone:
            return None
        
        # Remove non-digit characters except + at the start
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Basic validation - should be 10-15 digits
        if re.match(r'^\+?\d{10,15}$', cleaned):
            return cleaned
        
        return None

    def _validate_email_address(self, email: str) -> Optional[str]:
        """Validate email address format"""
        if not email:
            return None
        
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, email.strip()):
            return email.strip().lower()
        
        return None


# Maintain backward compatibility
class OpenAISummarizer(EnhancedOpenAIProcessor):
    """Backward compatibility class"""
