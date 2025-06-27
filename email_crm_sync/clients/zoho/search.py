"""
Zoho CRM Search module.

This module handles all search-related operations for Zoho CRM,
including COQL queries and record searching.
"""

import requests
import logging
from typing import Dict, Any, Optional, List
from ...exceptions import SearchError

logger = logging.getLogger(__name__)


class Search:
    """
    Handles search operations for Zoho CRM.
    
    This class provides methods to search for records using various
    search mechanisms including COQL queries.
    """
    
    def __init__(self, client):
        """
        Initialize the Search handler.
        
        Args:
            client: The main Zoho client instance
        """
        self.client = client
        self.base_url = client.base_url
        self.headers = client.headers
    
    def coql_query(self, query: str) -> Dict[str, Any]:
        """
        Execute a COQL (CRM Object Query Language) query.
        
        Args:
            query: COQL query string
            
        Returns:
            Dict containing query results
            
        Raises:
            SearchError: If the query fails
        """
        url = f"{self.base_url}/coql"
        
        data = {"select_query": query}
        
        try:
            response = requests.post(url, json=data, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                raise SearchError(f"COQL query failed: HTTP {response.status_code}: {response.text}")
                
        except requests.RequestException as e:
            raise SearchError(f"Network error executing COQL query: {str(e)}") from e
    
    def search_records(self, module: str, criteria: str, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Search for records in a specific module.
        
        Args:
            module: Module name to search in
            criteria: Search criteria
            fields: List of fields to retrieve
            
        Returns:
            Dict containing search results
            
        Raises:
            SearchError: If the search fails
        """
        url = f"{self.base_url}/{module}/search"
        
        params: Dict[str, Any] = {"criteria": criteria}
        
        if fields:
            params["fields"] = ",".join(fields)
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 204:
                # No records found
                return {"data": []}
            else:
                raise SearchError(f"Search failed: HTTP {response.status_code}: {response.text}")
                
        except requests.RequestException as e:
            raise SearchError(f"Network error during search: {str(e)}") from e
    
    def find_by_email(self, email: str, module: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Find records by email address.
        
        Args:
            email: Email address to search for
            module: Module to search in (defaults to client's module)
            
        Returns:
            List of matching records
        """
        search_module = module or self.client.developments_module
        
        try:
            # Try COQL first for more flexible searching
            query = f"SELECT * FROM {search_module} WHERE Email = '{email}'"
            result = self.coql_query(query)
            return result.get('data', [])
        except SearchError:
            # Fall back to regular search
            try:
                criteria = f"Email:equals:{email}"
                result = self.search_records(search_module, criteria)
                return result.get('data', [])
            except SearchError:
                return []
    
    def find_by_field(self, field: str, value: str, module: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Find records by a specific field value.
        
        Args:
            field: Field name to search
            value: Value to search for
            module: Module to search in
            
        Returns:
            List of matching records
        """
        search_module = module or self.client.developments_module
        
        try:
            criteria = f"{field}:equals:{value}"
            result = self.search_records(search_module, criteria)
            return result.get('data', [])
        except SearchError:
            return []
    
    def semantic_search(self, content: str, module: Optional[str] = None, 
                       confidence_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Perform semantic search using AI analysis.
        
        Args:
            content: Content to search for
            module: Module to search in
            confidence_threshold: Minimum confidence score for matches
            
        Returns:
            List of matching records with confidence scores
        """
        search_module = module or self.client.developments_module
        
        # This is a placeholder for semantic search implementation
        # In a real implementation, this would use AI/ML to find semantically similar records
        try:
            # For now, we'll do a simple text search across common fields
            # This can be enhanced with actual semantic matching later
            search_terms = content.lower().split()
            results = []
            
            for term in search_terms[:3]:  # Limit to first 3 terms for performance
                try:
                    # Search in common text fields
                    for field in ['Name', 'Description', 'Subject']:
                        criteria = f"{field}:contains:{term}"
                        result = self.search_records(search_module, criteria)
                        for record in result.get('data', []):
                            if record not in results:
                                # Add confidence score (simplified)
                                record['_confidence_score'] = 0.8  # Placeholder score
                                results.append(record)
                except SearchError:
                    continue
            
            # Filter by confidence threshold
            return [r for r in results if r.get('_confidence_score', 0) >= confidence_threshold]
            
        except Exception as e:
            raise SearchError(f"Semantic search failed: {str(e)}") from e
    
    def by_email(self, email: str, module: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for records by email address.
        
        Args:
            email: Email address to search for
            module: Module name (defaults to client's developments_module)
            
        Returns:
            List of matching records
        """
        try:
            module_name = module or self.client.developments_module
            
            # Try different email field names that might exist
            email_fields = ["Email", "Email_Address", "Primary_Email", "Contact_Email"]
            
            for field in email_fields:
                try:
                    criteria = f"({field}:equals:{email})"
                    result = self.search_records(module_name, criteria)
                    
                    if result.get("data"):
                        return result["data"]
                except Exception:
                    continue
            
            # If no exact matches, try COQL search
            query = f"""
                SELECT id, Name, Email
                FROM {module_name}
                WHERE Email = '{email}'
                LIMIT 10
            """
            
            coql_result = self.coql_query(query)
            return coql_result.get("data", [])
            
        except Exception as e:
            raise SearchError(f"Email search failed: {str(e)}") from e
    
    def by_criteria(self, criteria: str, module: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for records using criteria string.
        
        Args:
            criteria: Search criteria string
            module: Module name (defaults to client's developments_module)
            
        Returns:
            List of matching records
        """
        try:
            module_name = module or self.client.developments_module
            result = self.search_records(module_name, criteria)
            return result.get("data", [])
            
        except Exception as e:
            raise SearchError(f"Criteria search failed: {str(e)}") from e
    
    def by_word(self, word: str, module: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for records using word search.
        
        Args:
            word: Word to search for
            module: Module name (defaults to client's developments_module)
            
        Returns:
            List of matching records
        """
        try:
            module_name = module or self.client.developments_module
            
            url = f"{self.base_url}/{module_name}/search"
            params = {
                "word": word,
                "per_page": 50
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("data", [])
            elif response.status_code == 204:
                return []
            else:
                raise SearchError(f"Word search failed: HTTP {response.status_code}: {response.text}")
                
        except requests.RequestException as e:
            raise SearchError(f"Word search network error: {str(e)}") from e

    def advanced_email_search(self, email: str, company_name: Optional[str] = None,
                            include_modules: Optional[List[str]] = None) -> Dict[str, List[Dict]]:
        """
        Perform advanced email search across multiple modules and strategies.
        
        This method combines multiple search approaches for comprehensive results:
        1. Direct email field search in specified modules
        2. COQL-based search with company name correlation
        3. Word-based search for partial matches
        
        Args:
            email: Email address to search for
            company_name: Optional company name for enhanced matching
            include_modules: List of modules to search (defaults to common modules)
            
        Returns:
            Dict mapping module names to lists of matching records
        """
        try:
            logger.info("Starting advanced email search for: %s", email)
            
            # Default modules to search if not specified
            if include_modules is None:
                include_modules = [
                    self.client.developments_module,
                    "Contacts",
                    "Leads", 
                    "Accounts",
                    "Deals"
                ]
            
            all_results = {}
            
            # Strategy 1: Direct email search per module
            for module in include_modules:
                try:
                    logger.info("Searching %s module for email: %s", module, email)
                    results = self.by_email(email, module)
                    if results:
                        all_results[module] = results
                        logger.info("Found %d records in %s", len(results), module)
                except Exception as e:
                    logger.warning("Email search failed for module %s: %s", module, str(e))
                    continue
            
            # Strategy 2: COQL search with company correlation if provided
            if company_name and len(all_results) == 0:
                try:
                    logger.info("Attempting COQL search with company correlation")
                    
                    # Build COQL query for email and company correlation
                    domain = email.split('@')[1] if '@' in email else ''
                    
                    if domain:
                        coql_query = f"""
                        SELECT id, Account_Name, Email, Owner 
                        FROM {self.client.developments_module} 
                        WHERE (Email = '{email}') 
                        OR (Account_Name like '%{company_name}%' AND Email like '%{domain}%')
                        LIMIT 200
                        """
                        
                        coql_result = self.coql_query(coql_query)
                        if coql_result.get("success") and coql_result.get("data"):
                            all_results["COQL_Advanced"] = coql_result["data"]
                            logger.info("COQL advanced search found %d records", len(coql_result["data"]))
                            
                except Exception as e:
                    logger.warning("COQL advanced search failed: %s", str(e))
            
            # Strategy 3: Word search as fallback if no direct matches
            if len(all_results) == 0:
                try:
                    logger.info("Attempting word search fallback")
                    email_local = email.split('@')[0] if '@' in email else email
                    
                    for module in include_modules[:2]:  # Limit word search to primary modules
                        try:
                            word_results = self.by_word(email_local, module)
                            if word_results:
                                # Filter results that actually contain the email
                                filtered_results = []
                                for record in word_results:
                                    record_str = str(record).lower()
                                    if email.lower() in record_str:
                                        filtered_results.append(record)
                                
                                if filtered_results:
                                    all_results[f"{module}_Word"] = filtered_results
                                    logger.info("Word search found %d filtered records in %s", 
                                              len(filtered_results), module)
                        except Exception as e:
                            logger.warning("Word search failed for module %s: %s", module, str(e))
                            continue
                            
                except Exception as e:
                    logger.warning("Word search fallback failed: %s", str(e))
            
            # Summary
            total_records = sum(len(records) for records in all_results.values())
            logger.info("Advanced email search completed. Found %d total records across %d result sets", 
                       total_records, len(all_results))
            
            return all_results
            
        except Exception as e:
            logger.error("Advanced email search error: %s", str(e))
            return {}
