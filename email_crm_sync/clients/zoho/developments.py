"""
Zoho CRM Developments management module.

This module handles development-specific operations including
finding developments by email, address, and other criteria.
"""

import requests
import logging
from typing import Dict, Any, Optional, List
from ...exceptions import ZohoApiError

logger = logging.getLogger(__name__)


class Developments:
    """
    Handles development-specific operations for Zoho CRM.
    
    This class provides methods specific to development records,
    including specialized search and matching operations.
    """
    
    def __init__(self, client):
        """
        Initialize the Developments handler.
        
        Args:
            client: The main Zoho client instance
        """
        self.client = client
        self.base_url = client.base_url
        self.headers = client.headers
        self.session = client.session
        self.timeout = client.timeout
    
    def find_by_email(self, email: str, module: Optional[str] = None) -> Optional[Dict]:
        """
        Find development records associated with an email address.
        
        Args:
            email: Email address to search for
            module: Module name (defaults to client's developments_module)
            
        Returns:
            Dictionary containing the found development record, or None
        """
        try:
            module_name = module or self.client.developments_module
            
            logger.info("Finding development by email: %s in module: %s", email, module_name)
            
            # Use the search component for email-based search
            search_results = self.client.search.by_email(email, module_name)
            
            if search_results:
                logger.info("Found %d developments for email: %s", len(search_results), email)
                # Return the first match for now, could be enhanced to handle multiple matches
                return search_results[0]
            else:
                logger.info("No developments found for email: %s", email)
                return None
                
        except Exception as e:
            logger.error("Error finding development by email: %s", str(e))
            return None
    
    def find_by_address(self, address: str, module: Optional[str] = None) -> Optional[str]:
        """
        Find development records by address using enhanced search.
        
        Args:
            address: Address to search for
            module: Module name (defaults to client's developments_module)
            
        Returns:
            Development ID if found, None otherwise
        """
        try:
            module_name = module or self.client.developments_module
            
            logger.info("Finding development by address: %s in module: %s", address, module_name)
            
            # Use COQL query for better address matching
            address_query = f"""
                SELECT id, Name, Property_Address
                FROM {module_name}
                WHERE Property_Address LIKE '%{address}%'
                OR Name LIKE '%{address}%'
                LIMIT 5
            """
            
            try:
                results = self.client.search.coql_query(address_query)
                
                if results.get("data"):
                    best_match = results["data"][0]
                    development_id = best_match.get("id")
                    
                    logger.info("Found development by address: %s -> %s", 
                              address, development_id)
                    return development_id
                else:
                    logger.info("No development found for address: %s", address)
                    return None
                    
            except ZohoApiError as coql_error:
                error_msg = str(coql_error).lower()
                
                # Handle specific COQL errors based on API documentation
                if "syntax_error" in error_msg:
                    logger.warning("COQL syntax error for address query: %s", str(coql_error))
                elif "invalid_query" in error_msg:
                    logger.warning("Invalid COQL query for address search: %s", str(coql_error))
                elif "limit_exceeded" in error_msg:
                    logger.warning("COQL limit exceeded for address query: %s", str(coql_error))
                elif "oauth_scope_mismatch" in error_msg:
                    logger.error("OAuth scope mismatch for COQL query: %s", str(coql_error))
                    raise  # Re-raise scope errors as they need attention
                else:
                    logger.warning("COQL search failed for address, trying word search: %s", str(coql_error))
                
                # Fallback to word search for non-critical errors
                try:
                    search_results = self.client.search.by_word(address, module_name)
                    
                    if search_results:
                        development_id = search_results[0].get("id")
                        logger.info("Found development via word search fallback: %s -> %s", 
                                  address, development_id)
                        return development_id
                    else:
                        logger.info("No development found for address (fallback): %s", address)
                        return None
                except Exception as fallback_error:
                    logger.error("Both COQL and word search failed for address: %s", str(fallback_error))
                    return None
            except Exception as coql_error:
                logger.warning("Unexpected COQL error, trying word search: %s", str(coql_error))
                
                # Fallback to word search
                try:
                    search_results = self.client.search.by_word(address, module_name)
                    
                    if search_results:
                        development_id = search_results[0].get("id")
                        logger.info("Found development via word search: %s -> %s", 
                                  address, development_id)
                        return development_id
                    else:
                        logger.info("No development found for address: %s", address)
                        return None
                except Exception as fallback_error:
                    logger.error("Both COQL and word search failed: %s", str(fallback_error))
                    return None
                    
        except Exception as e:
            logger.error("Error finding development by address: %s", str(e))
            return None
    
    def find_by_address_enhanced(self, address: str, module: Optional[str] = None) -> Optional[Dict]:
        """
        Enhanced address search that returns full record details.
        
        Args:
            address: Address to search for
            module: Module name (defaults to client's developments_module)
            
        Returns:
            Dictionary containing the found development record, or None
        """
        try:
            module_name = module or self.client.developments_module
            
            logger.info("Enhanced address search: %s in module: %s", address, module_name)
            
            # Try multiple search strategies
            search_strategies = [
                # Strategy 1: Direct address field search
                lambda: self._search_by_address_field(address, module_name),
                # Strategy 2: Name field search
                lambda: self._search_by_name_field(address, module_name),
                # Strategy 3: General word search
                lambda: self.client.search.by_word(address, module_name)
            ]
            
            for strategy in search_strategies:
                try:
                    results = strategy()
                    if results:
                        logger.info("Found development using enhanced search for: %s", address)
                        return results[0] if isinstance(results, list) else results
                except Exception as strategy_error:
                    logger.debug("Search strategy failed: %s", str(strategy_error))
                    continue
            
            logger.info("No development found with enhanced search for: %s", address)
            return None
            
        except Exception as e:
            logger.error("Enhanced address search error: %s", str(e))
            return None
    
    def _search_by_address_field(self, address: str, module: str) -> List[Dict]:
        """Search by property address field."""
        query = f"""
            SELECT id, Name, Property_Address, Email
            FROM {module}
            WHERE Property_Address LIKE '%{address}%'
            LIMIT 5
        """
        results = self.client.search.coql_query(query)
        return results.get("data", [])
    
    def _search_by_name_field(self, address: str, module: str) -> List[Dict]:
        """Search by name field."""
        query = f"""
            SELECT id, Name, Property_Address, Email
            FROM {module}
            WHERE Name LIKE '%{address}%'
            LIMIT 5
        """
        results = self.client.search.coql_query(query)
        return results.get("data", [])
    
    def search_by_criteria(self, criteria_dict: Dict[str, str], 
                          module: Optional[str] = None) -> List[Dict]:
        """
        Search developments using multiple criteria.
        
        Args:
            criteria_dict: Dictionary of field:value pairs to search for
            module: Module name (defaults to client's developments_module)
            
        Returns:
            List of matching development records
        """
        try:
            module_name = module or self.client.developments_module
            
            logger.info("Searching developments by criteria in module: %s", module_name)
            logger.debug("Search criteria: %s", criteria_dict)
            
            # Build COQL query from criteria
            conditions = []
            for field, value in criteria_dict.items():
                if value:  # Only add non-empty values
                    # Escape single quotes in values
                    escaped_value = value.replace("'", "\\'")
                    conditions.append(f"{field} LIKE '%{escaped_value}%'")
            
            if not conditions:
                logger.warning("No valid search criteria provided")
                return []
            
            query = f"""
                SELECT id, Name, Property_Address, Email, Phone
                FROM {module_name}
                WHERE {' AND '.join(conditions)}
                LIMIT 10
            """
            
            logger.debug("Executing COQL query: %s", query)
            
            results = self.client.search.coql_query(query)
            developments = results.get("data", [])
            
            logger.info("Found %d developments matching criteria", len(developments))
            return developments
            
        except Exception as e:
            logger.error("Criteria search error: %s", str(e))
            return []
    
    def add_note(self, development_id: str, title: str, content: str, 
                 note_type: str = "Email Note") -> Dict[str, Any]:
        """
        Add a note to a development record.
        
        Args:
            development_id: ID of the development record
            title: Note title
            content: Note content
            note_type: Type of note (default: "Email Note")
            
        Returns:
            Dict containing note creation result
        """
        try:
            logger.info("Adding note to development: %s", development_id)
            
            # Add note type to the title if not already present
            if note_type and note_type not in title:
                enhanced_title = f"[{note_type}] {title}"
            else:
                enhanced_title = title
            
            # Use the notes component to create the note
            result = self.client.notes.create(
                parent_id=development_id,
                content=content,
                title=enhanced_title,
                parent_module=self.client.developments_module
            )
            
            if result.get("success"):
                logger.info("Successfully added note to development: %s", development_id)
            else:
                logger.error("Failed to add note to development: %s", development_id)
            
            return result
            
        except Exception as e:
            logger.error("Error adding note to development: %s", str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    def check_email_processed(self, gmail_message_id: str, 
                             module: Optional[str] = None) -> bool:
        """
        Check if an email has already been processed for this development.
        
        Args:
            gmail_message_id: Gmail message ID to check
            module: Module name (defaults to client's developments_module)
            
        Returns:
            True if email was already processed, False otherwise
        """
        try:
            # For now, we'll skip this check since the Gmail_Message_ID column
            # doesn't exist in the CRM schema. This allows processing to continue.
            logger.info("Skipping email processing check for: %s (column not available)", gmail_message_id)
            return False  # Always return False to allow processing
                
        except (ZohoApiError, ValueError) as e:
            logger.error("Error checking email processing status: %s", str(e))
            # If we can't check, assume it hasn't been processed to avoid skipping
            return False
