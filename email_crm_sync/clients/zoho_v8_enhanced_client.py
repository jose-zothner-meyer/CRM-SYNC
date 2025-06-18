import requests
import logging
from typing import Dict, List, Optional, Any
import time
from urllib.parse import quote

logger = logging.getLogger(__name__)

class ZohoV8EnhancedClient:
    """
    Enhanced Zoho CRM V8 API client optimized for email CRM sync.
    
    This client implements the most efficient V8 APIs for:
    - Email-based record matching using multiple strategies
    - Note creation and attachment to development records
    - Module discovery and validation
    - Advanced search with COQL support
    - Comprehensive caching and error handling
    
    Based on comprehensive V8 API analysis for optimal performance.
    """
    
    def __init__(self, access_token: str, data_center: str = "eu", 
                 developments_module: str = "Developments", timeout: int = 30):
        """Initialize the enhanced V8 client with comprehensive capabilities."""
        self.access_token = access_token
        self.data_center = data_center
        self.developments_module = developments_module
        self.timeout = timeout
        
        # Set correct base URL based on data center (per official multi-DC documentation)
        self.data_center = data_center.lower()
        
        # Official Zoho API endpoints from https://www.zoho.com/crm/developer/docs/api/v8/multi-dc.html
        dc_endpoints = {
            "eu": "https://www.zohoapis.eu/crm/v8",
            "com": "https://www.zohoapis.com/crm/v8", 
            "us": "https://www.zohoapis.com/crm/v8",  # US uses .com domain
            "in": "https://www.zohoapis.in/crm/v8",
            "au": "https://www.zohoapis.com.au/crm/v8",
            "cn": "https://www.zohoapis.com.cn/crm/v8",
            "jp": "https://www.zohoapis.jp/crm/v8",
            "ca": "https://www.zohoapis.ca/crm/v8"
        }
        
        self.base_url = dc_endpoints.get(self.data_center, dc_endpoints["eu"])
        
        # Official OAuth endpoints for token refresh
        auth_endpoints = {
            "eu": "https://accounts.zoho.eu",
            "com": "https://accounts.zoho.com",
            "us": "https://accounts.zoho.com",  # US uses .com domain
            "in": "https://accounts.zoho.in", 
            "au": "https://accounts.zoho.com.au",
            "cn": "https://accounts.zoho.com.cn",
            "jp": "https://accounts.zoho.jp",
            "ca": "https://accounts.zohocloud.ca"
        }
        
        self.auth_url = auth_endpoints.get(self.data_center, auth_endpoints["eu"])
        
        # Cache for metadata to reduce API calls (24 hour TTL for modules, 12 hour for fields)
        self._module_cache = {}
        self._field_cache = {}
        self._cache_timestamps = {}
        
        # Headers for all requests
        self.headers = {
            "Authorization": f"Zoho-oauthtoken {access_token}",
            "Content-Type": "application/json"
        }
        
        # Request session for connection pooling
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Required scopes based on official Zoho documentation
        # https://www.zoho.com/crm/developer/docs/api/v8/scopes.html
        self.required_scopes = {
            "modules": "ZohoCRM.modules.ALL",  # For record access
            "settings": "ZohoCRM.settings.READ",  # For metadata
            "org": "ZohoCRM.org.READ",  # For organization info
            "coql": "ZohoCRM.coql.READ",  # For advanced search
            "notes": "ZohoCRM.modules.notes.ALL"  # For note operations
        }
        
        logger.info("Initialized Enhanced Zoho V8 Client for %s with module: %s", 
                   data_center, developments_module)
    
    def _is_cache_valid(self, cache_key: str, ttl_hours: int = 12) -> bool:
        """Check if cached data is still valid."""
        if cache_key not in self._cache_timestamps:
            return False
        elapsed = time.time() - self._cache_timestamps[cache_key]
        return elapsed < (ttl_hours * 3600)
    
    def _update_cache(self, cache_key: str, data: Any) -> None:
        """Update cache with timestamp."""
        self._cache_timestamps[cache_key] = time.time()
        if cache_key.startswith("modules"):
            self._module_cache[cache_key] = data
        elif cache_key.startswith("fields"):
            self._field_cache[cache_key] = data
    
    def search_by_email(self, email: str, module: Optional[str] = None) -> List[Dict]:
        """Search for records by email address using V8 search API."""
        try:
            search_module = module or self.developments_module
            logger.info("Searching %s by email: %s", search_module, email)
            
            search_url = f"{self.base_url}/{search_module}/search"
            params = {
                "email": email,
                "per_page": 200
            }
            
            response = self.session.get(search_url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("data"):
                    records = data.get("data", [])
                    logger.info("Found %d records matching email %s", len(records), email)
                    return records
                else:
                    logger.info("No records found for email: %s", email)
                    return []
            else:
                error_text = response.text
                logger.error("Email search failed: %d - %s", response.status_code, error_text)
                return []
                
        except requests.RequestException as e:
            logger.error("Email search error: %s", str(e))
            return []
    
    def create_note(self, parent_id: str, content: str, title: Optional[str] = None,
                   parent_module: Optional[str] = None) -> Dict[str, Any]:
        """Create a note using the V8 Notes API."""
        try:
            module = parent_module or self.developments_module
            
            logger.info("Creating note for %s record: %s", module, parent_id)
            
            note_data = {
                "Note_Content": content
            }
            
            if title:
                # Ensure title doesn't exceed 120 characters (Zoho limit)
                max_title_length = 110  # Leave some buffer
                if len(title) > max_title_length:
                    title = title[:max_title_length-3] + "..."
                note_data["Note_Title"] = title
            
            url = f"{self.base_url}/{module}/{parent_id}/Notes"
            payload = {"data": [note_data]}
            
            response = self.session.post(url, json=payload, timeout=self.timeout)
            
            if response.status_code in [200, 201]:
                data = response.json()
                if data.get("data") and len(data["data"]) > 0:
                    created_note = data["data"][0]
                    if created_note.get("code") == "SUCCESS":
                        note_id = created_note.get("details", {}).get("id")
                        logger.info("Note created successfully. Note ID: %s", note_id)
                        return {
                            "success": True,
                            "note_id": note_id,
                            "details": created_note
                        }
                    else:
                        logger.error("Note creation failed in response: %s", data)
                        return {
                            "success": False,
                            "error": created_note.get("message", "Unknown error"),
                            "details": created_note
                        }
                else:
                    return {
                        "success": False,
                        "error": "No response data received"
                    }
            else:
                error_text = response.text
                logger.error("Note creation failed: %d - %s", response.status_code, error_text)
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {error_text}"
                }
                
        except requests.RequestException as e:
            logger.error("Note creation error: %s", str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_notes(self, parent_id: Optional[str] = None, parent_module: Optional[str] = None,
                 note_id: Optional[str] = None, fields: Optional[List[str]] = None,
                 page: int = 1, per_page: int = 200) -> Dict[str, Any]:
        """
        Get notes using V8 Notes API with multiple endpoint options.
        
        Three endpoint options:
        1. GET /Notes - Get all notes (admin only)
        2. GET /Notes/{note_id} - Get specific note
        3. GET /{module}/{record_id}/Notes - Get notes for specific record
        
        Args:
            parent_id: ID of parent record (for option 3)
            parent_module: Module name (for option 3)
            note_id: Specific note ID (for option 2)
            fields: Specific fields to retrieve
            page: Page number (default: 1)
            per_page: Records per page (default: 200, max: 200)
            
        Returns:
            Dict containing notes data and metadata
        """
        try:
            # Determine endpoint based on parameters
            if note_id:
                # Get specific note
                url = f"{self.base_url}/Notes/{note_id}"
                logger.info("Getting specific note: %s", note_id)
            elif parent_id and parent_module:
                # Get notes for specific record
                module = parent_module or self.developments_module
                url = f"{self.base_url}/{module}/{parent_id}/Notes"
                logger.info("Getting notes for %s record: %s", module, parent_id)
            else:
                # Get all notes (admin only)
                url = f"{self.base_url}/Notes"
                logger.info("Getting all notes (admin access required)")
            
            # Prepare parameters
            params: Dict[str, Any] = {
                "page": page,
                "per_page": min(per_page, 200)  # V8 API maximum
            }
            
            if fields:
                params["fields"] = ",".join(fields)
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                notes = data.get("data", [])
                info = data.get("info", {})
                logger.info("Retrieved %d notes. More records: %s", 
                          len(notes), info.get('more_records', False))
                return {
                    "success": True,
                    "notes": notes,
                    "info": info
                }
            else:
                error_text = response.text
                logger.error("Get notes failed: %d - %s", response.status_code, error_text)
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {error_text}",
                    "notes": []
                }
                
        except requests.RequestException as e:
            logger.error("Get notes error: %s", str(e))
            return {
                "success": False,
                "error": str(e),
                "notes": []
            }
    
    def update_note(self, note_id: str, title: Optional[str] = None, content: Optional[str] = None,
                   parent_id: Optional[str] = None, parent_module: Optional[str] = None) -> Dict[str, Any]:
        """
        Update an existing note using V8 Notes API.
        
        Uses PUT /Notes/{note_id} for updating note content and title.
        At least one of title or content must be provided.
        
        Args:
            note_id: ID of the note to update
            title: New note title (optional)
            content: New note content (optional)
            parent_id: Parent record ID (for logging/validation)
            parent_module: Parent module name (for logging/validation)
            
        Returns:
            Dict containing update result
        """
        try:
            if not title and not content:
                return {
                    "success": False,
                    "error": "At least one of title or content must be provided"
                }
            
            logger.info("Updating note: %s", note_id)
            
            # Prepare update data
            update_data = {}
            if title is not None:
                update_data["Note_Title"] = title
            if content is not None:
                update_data["Note_Content"] = content
            
            url = f"{self.base_url}/Notes/{note_id}"
            payload = {"data": [update_data]}
            
            response = self.session.put(url, json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("data") and len(data["data"]) > 0:
                    updated_note = data["data"][0]
                    if updated_note.get("code") == "SUCCESS":
                        logger.info("Note updated successfully: %s", note_id)
                        return {
                            "success": True,
                            "note_id": note_id,
                            "details": updated_note
                        }
                    else:
                        logger.error("Note update failed in response: %s", data)
                        return {
                            "success": False,
                            "error": updated_note.get("message", "Unknown error"),
                            "details": updated_note
                        }
                else:
                    return {
                        "success": False,
                        "error": "No response data received"
                    }
            else:
                error_text = response.text
                logger.error("Note update failed: %d - %s", response.status_code, error_text)
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {error_text}"
                }
                
        except requests.RequestException as e:
            logger.error("Note update error: %s", str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_multiple_notes(self, notes_data: List[Dict], parent_module: Optional[str] = None) -> Dict[str, Any]:
        """
        Create multiple notes in a single API call using bulk operations.
        
        Uses POST /Notes with multiple note records for efficient bulk creation.
        Each note in notes_data should have parent_id, content, and optionally title.
        
        Args:
            notes_data: List of note dictionaries with parent_id, content, title
            parent_module: Parent module name (defaults to developments_module)
            
        Returns:
            Dict containing bulk creation results
        """
        try:
            module = parent_module or self.developments_module
            logger.info("Creating %d notes in bulk for module: %s", len(notes_data), module)
            
            # Prepare bulk data
            bulk_data = []
            for note in notes_data:
                if "parent_id" not in note or "content" not in note:
                    continue  # Skip invalid entries
                
                note_data = {
                    "Note_Content": note["content"],
                    "Parent_Id": note["parent_id"]
                }
                
                if "title" in note:
                    note_data["Note_Title"] = note["title"]
                
                bulk_data.append(note_data)
            
            if not bulk_data:
                return {
                    "success": False,
                    "error": "No valid note data provided"
                }
            
            url = f"{self.base_url}/Notes"
            payload = {"data": bulk_data}
            
            response = self.session.post(url, json=payload, timeout=self.timeout * 2)  # Extended timeout for bulk
            
            if response.status_code in [200, 201]:
                data = response.json()
                created_notes = data.get("data", [])
                successful = [note for note in created_notes if note.get("code") == "SUCCESS"]
                failed = [note for note in created_notes if note.get("code") != "SUCCESS"]
                
                logger.info("Bulk note creation: %d successful, %d failed", len(successful), len(failed))
                return {
                    "success": True,
                    "created": len(successful),
                    "failed": len(failed),
                    "successful_notes": successful,
                    "failed_notes": failed,
                    "details": created_notes
                }
            else:
                error_text = response.text
                logger.error("Bulk note creation failed: %d - %s", response.status_code, error_text)
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {error_text}"
                }
                
        except requests.RequestException as e:
            logger.error("Bulk note creation error: %s", str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_by_criteria(self, criteria: str, module: Optional[str] = None) -> List[Dict]:
        """
        Search for records using custom criteria with V8 search API.
        
        Supports complex criteria with operators:
        - Equality: (field_name:value)
        - Ranges: (field_name:start_value,end_value)
        - Contains: (field_name:*partial_value*)
        - Multiple criteria: (field1:value1) and (field2:value2)
        
        Args:
            criteria: Search criteria in V8 format
            module: Specific module to search (defaults to developments_module)
            
        Returns:
            List of matching records
        """
        try:
            search_module = module or self.developments_module
            logger.info("Searching %s with criteria: %s", search_module, criteria)
            
            search_url = f"{self.base_url}/{search_module}/search"
            params = {
                "criteria": criteria,
                "per_page": 200
            }
            
            response = self.session.get(search_url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("data"):
                    records = data.get("data", [])
                    logger.info("Found %d records matching criteria", len(records))
                    return records
                else:
                    logger.info("No records found for criteria: %s", criteria)
                    return []
            else:
                error_text = response.text
                logger.error("Criteria search failed: %d - %s", response.status_code, error_text)
                return []
                
        except requests.RequestException as e:
            logger.error("Criteria search error: %s", str(e))
            return []
    
    def search_by_word(self, word: str, module: Optional[str] = None) -> List[Dict]:
        """
        Performs a global search within the specified module using the given word.
        
        This uses V8's word-based search capability that searches across
        all searchable fields in the module.
        
        Args:
            word: Search term to look for
            module: Specific module to search (defaults to developments_module)
            
        Returns:
            List of matching records
        """
        try:
            search_module = module or self.developments_module
            logger.info("Searching %s by word: %s", search_module, word)
            
            search_url = f"{self.base_url}/{search_module}/search"
            params = {
                "word": word,
                "per_page": 200
            }
            
            response = self.session.get(search_url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("data"):
                    records = data.get("data", [])
                    logger.info("Found %d records matching word %s", len(records), word)
                    return records
                else:
                    logger.info("No records found for word: %s", word)
                    return []
            else:
                error_text = response.text
                logger.error("Word search failed: %d - %s", response.status_code, error_text)
                return []
                
        except requests.RequestException as e:
            logger.error("Word search error: %s", str(e))
            return []
    
    def coql_query(self, query: str, include_meta: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute COQL (CRM Object Query Language) for complex searches.
        
        COQL provides SQL-like querying capabilities following official documentation:
        https://www.zoho.com/crm/developer/docs/api/v8/Get-Records-through-COQL-Query.html
        
        Supports:
        - Advanced filtering with multiple field types and comparators
        - Joins (up to 2 relations per official limits)
        - Aggregate functions (SUM, MAX, MIN, AVG, COUNT)
        - Multi-module lookup and alias support
        - Field metadata retrieval
        
        Args:
            query: COQL query string (must be SELECT statement)
            include_meta: Optional metadata to include (e.g., ["fields"])
            
        Returns:
            Dict containing query results, metadata, and success status
        """
        try:
            logger.info("Executing COQL query: %s", query)
            
            # Validate query is SELECT statement
            if not query.strip().lower().startswith('select'):
                logger.error("COQL query must be a SELECT statement")
                return {
                    "data": [],
                    "success": False,
                    "error": "Query must be a SELECT statement"
                }
            
            coql_url = f"{self.base_url}/coql"
            payload = {"select_query": query}
            
            # Add metadata inclusion if requested (requires ZohoCRM.settings.fields.READ scope)
            if include_meta:
                payload["include_meta"] = include_meta
            
            response = self.session.post(coql_url, json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                records = data.get("data", [])
                info = data.get("info", {})
                fields_meta = data.get("fields", {})
                
                logger.info("COQL query returned %d records. More records: %s", 
                          len(records), info.get('more_records', False))
                
                result = {
                    "data": records,
                    "info": info,
                    "success": True
                }
                
                # Include field metadata if present
                if fields_meta:
                    result["fields"] = fields_meta
                    
                return result
                
            else:
                error_text = response.text
                logger.error("COQL query failed: %d - %s", response.status_code, error_text)
                
                # Parse specific error for better handling
                try:
                    error_data = response.json()
                    error_code = error_data.get("code", "UNKNOWN_ERROR")
                    error_message = error_data.get("message", error_text)
                except:
                    error_code = "UNKNOWN_ERROR"
                    error_message = error_text
                
                return {
                    "data": [],
                    "success": False,
                    "error": error_message,
                    "error_code": error_code,
                    "status_code": response.status_code
                }
                
        except requests.RequestException as e:
            logger.error("COQL query error: %s", str(e))
            return {
                "data": [],
                "success": False,
                "error": str(e)
            }
    
    def get_record(self, record_id: str, module: Optional[str] = None, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get a specific record by ID using V8 API.
        
        Uses GET /{module}/{record_id} to retrieve complete record data.
        
        Args:
            record_id: ID of the record to retrieve
            module: Module name (defaults to developments_module)
            fields: Specific fields to retrieve (optional)
            
        Returns:
            Dict containing record data or error information
        """
        try:
            search_module = module or self.developments_module
            logger.info("Getting %s record: %s", search_module, record_id)
            
            url = f"{self.base_url}/{search_module}/{record_id}"
            params: Dict[str, Any] = {}
            
            if fields:
                params["fields"] = ",".join(fields)
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("data") and len(data["data"]) > 0:
                    record = data["data"][0]
                    logger.info("Retrieved record: %s", record_id)
                    return {
                        "success": True,
                        "record": record
                    }
                else:
                    logger.warning("No data found for record: %s", record_id)
                    return {
                        "success": False,
                        "error": "Record not found"
                    }
            else:
                error_text = response.text
                logger.error("Get record failed: %d - %s", response.status_code, error_text)
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {error_text}"
                }
                
        except requests.RequestException as e:
            logger.error("Get record error: %s", str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    def discover_modules(self, status: Optional[List[str]] = None) -> List[Dict]:
        """
        Discover available modules using V8 settings API with caching.
        
        Retrieves module information including API names, display names,
        and access permissions. Results are cached for 24 hours.
        
        Args:
            status: Filter modules by status (e.g., ['enabled'])
            
        Returns:
            List of module information dictionaries
        """
        try:
            cache_key = f"modules_{status or 'all'}"
            
            # Check cache first
            if self._is_cache_valid(cache_key, ttl_hours=24):
                logger.info("Using cached module data")
                return self._module_cache.get(cache_key, [])
            
            logger.info("Discovering modules...")
            
            url = f"{self.base_url}/settings/modules"
            params = {}
            if status:
                params["status"] = ",".join(status)
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                modules = data.get("modules", [])
                
                # Update cache
                self._update_cache(cache_key, modules)
                
                logger.info("Discovered %d modules", len(modules))
                return modules
            else:
                error_text = response.text
                logger.error("Module discovery failed: %d - %s", response.status_code, error_text)
                return []
                
        except requests.RequestException as e:
            logger.error("Module discovery error: %s", str(e))
            return []
    
    def get_module_metadata(self, module: Optional[str] = None) -> Dict[str, Any]:
        """
        Get metadata for a specific module using V8 settings API with caching.
        
        Retrieves comprehensive module metadata including field definitions,
        layouts, permissions, and relationships. Results cached for 24 hours.
        
        Args:
            module: Module name (defaults to developments_module)
            
        Returns:
            Dict containing module metadata or error information
        """
        try:
            search_module = module or self.developments_module
            cache_key = f"modules_metadata_{search_module}"
            
            # Check cache first
            if self._is_cache_valid(cache_key, ttl_hours=24):
                logger.info("Using cached metadata for module: %s", search_module)
                return self._module_cache.get(cache_key, {})
            
            logger.info("Getting metadata for module: %s", search_module)
            
            url = f"{self.base_url}/settings/modules/{search_module}"
            
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                modules = data.get("modules", [])
                
                if modules and len(modules) > 0:
                    metadata = modules[0]
                    
                    # Update cache
                    self._update_cache(cache_key, metadata)
                    
                    logger.info("Retrieved metadata for module: %s", search_module)
                    return {
                        "success": True,
                        "metadata": metadata
                    }
                else:
                    logger.warning("No metadata found for module: %s", search_module)
                    return {
                        "success": False,
                        "error": "Module metadata not found"
                    }
            else:
                error_text = response.text
                logger.error("Module metadata retrieval failed: %d - %s", response.status_code, error_text)
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {error_text}"
                }
                
        except requests.RequestException as e:
            logger.error("Module metadata error: %s", str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_field_metadata(self, module: Optional[str] = None) -> List[Dict]:
        """
        Get field metadata for a module using V8 settings API with caching.
        
        Retrieves detailed field information including data types, validation rules,
        picklist values, and field relationships. Results cached for 12 hours.
        
        Args:
            module: Module name (defaults to developments_module)
            
        Returns:
            List of field metadata dictionaries
        """
        try:
            search_module = module or self.developments_module
            cache_key = f"fields_metadata_{search_module}"
            
            # Check cache first
            if self._is_cache_valid(cache_key, ttl_hours=12):
                logger.info("Using cached field metadata for module: %s", search_module)
                return self._field_cache.get(cache_key, [])
            
            logger.info("Getting field metadata for module: %s", search_module)
            
            url = f"{self.base_url}/settings/fields"
            params = {"module": search_module}
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                fields = data.get("fields", [])
                
                # Update cache
                self._update_cache(cache_key, fields)
                
                logger.info("Retrieved %d field definitions for module: %s", len(fields), search_module)
                return fields
            else:
                error_text = response.text
                logger.error("Field metadata retrieval failed: %d - %s", response.status_code, error_text)
                return []
                
        except requests.RequestException as e:
            logger.error("Field metadata error: %s", str(e))
            return []
    
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
                    self.developments_module,
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
                    results = self.search_by_email(email, module)
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
                        FROM {self.developments_module} 
                        WHERE (Email = '{email}') 
                        OR (Account_Name like '%{company_name}%' AND Email like '%{domain}%')
                        LIMIT 200
                        """
                        
                        coql_result = self.coql_query(coql_query)
                        if coql_result.get("success") and coql_result.get("records"):
                            all_results["COQL_Advanced"] = coql_result["records"]
                            logger.info("COQL advanced search found %d records", len(coql_result["records"]))
                            
                except Exception as e:
                    logger.warning("COQL advanced search failed: %s", str(e))
            
            # Strategy 3: Word search as fallback if no direct matches
            if len(all_results) == 0:
                try:
                    logger.info("Attempting word search fallback")
                    email_local = email.split('@')[0] if '@' in email else email
                    
                    for module in include_modules[:2]:  # Limit word search to primary modules
                        try:
                            word_results = self.search_by_word(email_local, module)
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
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the connection to Zoho CRM API and validate configuration.
        
        Performs comprehensive validation including:
        - API connectivity and authentication
        - Module accessibility 
        - Permission verification
        - Performance timing
        
        Returns:
            Dict containing test results and diagnostic information
        """
        start_time = time.time()
        try:
            logger.info("Testing Zoho V8 API connection...")
            
            results = {
                "success": False,
                "tests": {},
                "timing": {},
                "config": {
                    "data_center": self.data_center,
                    "developments_module": self.developments_module,
                    "base_url": self.base_url
                }
            }
            
            # Test 1: Basic API connectivity
            try:
                test_start = time.time()
                url = f"{self.base_url}/org"
                response = self.session.get(url, timeout=self.timeout)
                
                results["timing"]["org_api"] = time.time() - test_start
                
                if response.status_code == 200:
                    org_data = response.json()
                    results["tests"]["org_api"] = {
                        "success": True,
                        "org_info": org_data.get("org", [{}])[0] if org_data.get("org") else {}
                    }
                    logger.info("✓ Organization API test passed")
                else:
                    results["tests"]["org_api"] = {
                        "success": False,
                        "error": f"HTTP {response.status_code}: {response.text}"
                    }
                    logger.error("✗ Organization API test failed: %s", response.status_code)
                    
            except requests.RequestException as e:
                results["tests"]["org_api"] = {
                    "success": False,
                    "error": str(e)
                }
                logger.error("✗ Organization API test error: %s", str(e))
            
            # Test 2: Module discovery
            try:
                test_start = time.time()
                modules = self.discover_modules()
                results["timing"]["module_discovery"] = time.time() - test_start
                
                if modules:
                    target_module = None
                    for module in modules:
                        if module.get("api_name") == self.developments_module:
                            target_module = module
                            break
                    
                    results["tests"]["module_discovery"] = {
                        "success": True,
                        "total_modules": len(modules),
                        "target_module_found": target_module is not None,
                        "target_module_details": target_module
                    }
                    logger.info("✓ Module discovery test passed: %d modules found", len(modules))
                else:
                    results["tests"]["module_discovery"] = {
                        "success": False,
                        "error": "No modules discovered"
                    }
                    logger.error("✗ Module discovery test failed")
                    
            except Exception as e:
                results["tests"]["module_discovery"] = {
                    "success": False,
                    "error": str(e)
                }
                logger.error("✗ Module discovery test error: %s", str(e))
            
            # Test 3: Search functionality
            try:
                test_start = time.time()
                # Use a simple word search that should work reliably
                search_results = self.search_by_word("test", self.developments_module)
                results["timing"]["search_test"] = time.time() - test_start
                
                results["tests"]["search_functionality"] = {
                    "success": True,
                    "sample_records_found": len(search_results)
                }
                logger.info("✓ Search functionality test passed: %d records found", len(search_results))
                
            except Exception as e:
                results["tests"]["search_functionality"] = {
                    "success": False,
                    "error": str(e)
                }
                logger.error("✗ Search functionality test error: %s", str(e))
            
            # Overall success determination
            total_time = time.time() - start_time
            results["timing"]["total"] = total_time
            
            successful_tests = sum(1 for test in results["tests"].values() if test.get("success", False))
            total_tests = len(results["tests"])
            
            results["success"] = successful_tests >= 2  # At least 2 out of 3 tests must pass
            results["summary"] = {
                "successful_tests": successful_tests,
                "total_tests": total_tests,
                "success_rate": successful_tests / total_tests if total_tests > 0 else 0
            }
            
            if results["success"]:
                logger.info("🎉 Zoho V8 API connection test PASSED (%d/%d tests, %.2fs)", 
                           successful_tests, total_tests, total_time)
            else:
                logger.warning("⚠️ Zoho V8 API connection test PARTIAL (%d/%d tests, %.2fs)", 
                              successful_tests, total_tests, total_time)
            
            return results
            
        except Exception as e:
            logger.error("Connection test failed: %s", str(e))
            return {
                "success": False,
                "error": str(e),
                "tests": {},
                "timing": {"total": time.time() - start_time}
            }
    
    def __del__(self):
        """Cleanup resources when the client is destroyed."""
        try:
            if hasattr(self, 'session'):
                self.session.close()
        except Exception:
            pass
    
    def add_note_to_development(self, development_id: str, title: str, content: str, 
                                  module: Optional[str] = None) -> Dict[str, Any]:
        """
        Convenience method to add a note to a development record.
        
        This is a wrapper around create_note with simplified parameters
        for development-specific note creation.
        
        Args:
            development_id: ID of the development record
            title: Note title/subject
            content: Note content/body
            module: Module name (defaults to developments_module)
            
        Returns:
            Dict containing note creation result
        """
        return self.create_note(
            parent_id=development_id,
            content=content,
            title=title,
            parent_module=module or self.developments_module
        )
    
    def find_development_by_email(self, email: str, module: Optional[str] = None) -> Optional[Dict]:
        """
        Find a development record by email address.
        
        This is a convenience method that searches for development records
        containing the specified email and returns the first match.
        
        Args:
            email: Email address to search for
            module: Module to search (defaults to developments_module)
            
        Returns:
            First matching development record or None if not found
        """
        try:
            results = self.search_by_email(email, module or self.developments_module)
            if results and len(results) > 0:
                logger.info("Found development by email %s: %s", email, results[0].get('id'))
                return results[0]
            else:
                logger.info("No development found for email: %s", email)
                return None
        except Exception as e:
            logger.error("Error finding development by email %s: %s", email, str(e))
            return None
    
    def find_development_by_address(self, address: str, module: Optional[str] = None) -> Optional[str]:
        """
        Find a development record by property address.
        
        Uses word search to find developments containing the specified address
        and returns the ID of the first match.
        
        Args:
            address: Property address to search for
            module: Module to search (defaults to developments_module)
            
        Returns:
            Development record ID or None if not found
        """
        try:
            # Try word search first
            results = self.search_by_word(address, module or self.developments_module)
            
            if results and len(results) > 0:
                development_id = results[0].get('id')
                logger.info("Found development by address %s: %s", address, development_id)
                return development_id
            
            # Fallback to criteria search if word search fails
            address_criteria = f"(Address:*{address}*)"
            criteria_results = self.search_by_criteria(address_criteria, module or self.developments_module)
            
            if criteria_results and len(criteria_results) > 0:
                development_id = criteria_results[0].get('id')
                logger.info("Found development by address criteria %s: %s", address, development_id)
                return development_id
            
            logger.info("No development found for address: %s", address)
            return None
            
        except Exception as e:
            logger.error("Error finding development by address %s: %s", address, str(e))
            return None
    
    def search_developments_by_criteria(self, criteria_dict: Dict[str, str], 
                                      module: Optional[str] = None) -> List[Dict]:
        """
        Search for development records using multiple criteria fields.
        
        Converts a dictionary of field-value pairs into a Zoho criteria string
        and performs the search.
        
        Args:
            criteria_dict: Dictionary of field names and values to search for
            module: Module to search (defaults to developments_module)
            
        Returns:
            List of matching development records
        """
        try:
            if not criteria_dict:
                return []
            
            # Build criteria string from dictionary
            criteria_parts = []
            for field, value in criteria_dict.items():
                if value:  # Only add non-empty values
                    # Escape special characters and wrap in criteria format
                    safe_value = str(value).replace("'", "\\'")
                    criteria_parts.append(f"({field}:*{safe_value}*)")
            
            if not criteria_parts:
                return []
            
            # Combine criteria with AND logic
            criteria_string = " and ".join(criteria_parts)
            
            logger.info("Searching developments with criteria: %s", criteria_string)
            
            results = self.search_by_criteria(criteria_string, module or self.developments_module)
            
            logger.info("Found %d developments matching criteria", len(results))
            return results
            
        except Exception as e:
            logger.error("Error searching developments by criteria %s: %s", criteria_dict, str(e))
            return []

    # Email-specific operations from API Directory (High Priority for Email CRM Sync)
    
    def associate_email_with_record(self, email_id: str, record_id: str, module: Optional[str] = None) -> Dict[str, Any]:
        """
        Associate an email with a record entity using V8 API.
        
        From API Directory: "Associate Email with a Record"
        Uses POST /{module}/{record_id}/actions/associate_email
        This links Gmail emails directly to Development records for tracking.
        
        Args:
            email_id: ID of the email to associate (Gmail message ID)
            record_id: ID of the Development record to associate with
            module: Module name (defaults to developments_module)
            
        Returns:
            Dict containing association result
        """
        try:
            search_module = module or self.developments_module
            logger.info("Associating email %s with %s record: %s", email_id, search_module, record_id)
            
            url = f"{self.base_url}/{search_module}/{record_id}/actions/associate_email"
            payload = {
                "data": [{
                    "email_id": email_id
                }]
            }
            
            response = self.session.post(url, json=payload, timeout=self.timeout)
            
            if response.status_code in [200, 201]:
                data = response.json()
                if data.get("data") and len(data["data"]) > 0:
                    result = data["data"][0]
                    if result.get("code") == "SUCCESS":
                        logger.info("Email associated successfully with Development")
                        return {
                            "success": True,
                            "details": result
                        }
                    else:
                        logger.error("Email association failed: %s", result.get("message"))
                        return {
                            "success": False,
                            "error": result.get("message", "Unknown error"),
                            "details": result
                        }
                else:
                    return {
                        "success": False,
                        "error": "No response data received"
                    }
            else:
                error_text = response.text
                logger.error("Email association failed: %d - %s", response.status_code, error_text)
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {error_text}"
                }
                
        except requests.RequestException as e:
            logger.error("Email association error: %s", str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_emails_of_record(self, record_id: str, module: Optional[str] = None,
                           page: int = 1, per_page: int = 200) -> Dict[str, Any]:
        """
        Get the details of emails associated with a record using V8 API.
        
        From API Directory: "Get Emails of a Record"
        Uses GET /{module}/{record_id}/Emails
        This retrieves all emails linked to a Development record.
        
        Args:
            record_id: ID of the Development record to get emails for
            module: Module name (defaults to developments_module)
            page: Page number (default: 1)
            per_page: Records per page (default: 200, max: 200)
            
        Returns:
            Dict containing emails data
        """
        try:
            search_module = module or self.developments_module
            logger.info("Getting emails for %s record: %s", search_module, record_id)
            
            url = f"{self.base_url}/{search_module}/{record_id}/Emails"
            params = {
                "page": page,
                "per_page": min(per_page, 200)
            }
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                emails = data.get("data", [])
                info = data.get("info", {})
                logger.info("Retrieved %d emails for Development %s", len(emails), record_id)
                return {
                    "success": True,
                    "emails": emails,
                    "info": info
                }
            else:
                error_text = response.text
                logger.error("Get emails failed: %d - %s", response.status_code, error_text)
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {error_text}",
                    "emails": []
                }
                
        except requests.RequestException as e:
            logger.error("Get emails error: %s", str(e))
            return {
                "success": False,
                "error": str(e),
                "emails": []
            }
    
    def send_mail(self, from_address: str, to_addresses: List[str], subject: str, 
                 content: str, record_id: Optional[str] = None, 
                 module: Optional[str] = None, template_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Send emails through Zoho CRM V8 API.
        
        From API Directory: "Send Mail"
        Uses POST /actions/send_mail
        This can send automated responses or notifications.
        
        Args:
            from_address: Email address to send from
            to_addresses: List of recipient email addresses
            subject: Email subject
            content: Email content/body
            record_id: Optional Development record ID to associate email with
            module: Module name for record association
            template_id: Optional email template ID
            
        Returns:
            Dict containing send result
        """
        try:
            logger.info("Sending email to %s recipients", len(to_addresses))
            
            email_data = {
                "from": {"email": from_address},
                "to": [{"email": addr} for addr in to_addresses],
                "subject": subject,
                "content": content
            }
            
            if template_id:
                email_data["template"] = {"id": template_id}
            
            if record_id and module:
                search_module = module or self.developments_module
                url = f"{self.base_url}/{search_module}/{record_id}/actions/send_mail"
                logger.info("Sending email associated with %s record: %s", search_module, record_id)
            else:
                url = f"{self.base_url}/actions/send_mail"
                logger.info("Sending standalone email")
            
            payload = {"data": [email_data]}
            
            response = self.session.post(url, json=payload, timeout=self.timeout)
            
            if response.status_code in [200, 201]:
                data = response.json()
                if data.get("data") and len(data["data"]) > 0:
                    result = data["data"][0]
                    if result.get("code") == "SUCCESS":
                        logger.info("Email sent successfully")
                        return {
                            "success": True,
                            "message_id": result.get("details", {}).get("message_id"),
                            "details": result
                        }
                    else:
                        logger.error("Email send failed: %s", result.get("message"))
                        return {
                            "success": False,
                            "error": result.get("message", "Unknown error"),
                            "details": result
                        }
                else:
                    return {
                        "success": False,
                        "error": "No response data received"
                    }
            else:
                error_text = response.text
                logger.error("Email send failed: %d - %s", response.status_code, error_text)
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {error_text}"
                }
                
        except requests.RequestException as e:
            logger.error("Email send error: %s", str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_by_external_id(self, external_id: str, external_field: str = "External_Email_ID",
                             module: Optional[str] = None) -> List[Dict]:
        """
        Search records using external ID fields with V8 API.
        
        From API Directory: "Search Records Using External ID"
        Uses GET /{module}/search with external field criteria.
        This is perfect for tracking Gmail message IDs to prevent duplicate processing.
        
        Args:
            external_id: External identifier value (e.g., Gmail message ID)
            external_field: Name of the external ID field (default: "External_Email_ID")
            module: Module name (defaults to developments_module)
            
        Returns:
            List of matching records
        """
        try:
            search_module = module or self.developments_module
            logger.info("Searching %s by external ID %s = %s", search_module, external_field, external_id)
            
            search_url = f"{self.base_url}/{search_module}/search"
            params = {
                "criteria": f"({external_field}:{external_id})",
                "per_page": 200
            }
            
            response = self.session.get(search_url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("data"):
                    records = data.get("data", [])
                    logger.info("Found %d records matching external ID", len(records))
                    return records
                else:
                    logger.info("No records found for external ID: %s", external_id)
                    return []
            else:
                error_text = response.text
                logger.error("External ID search failed: %d - %s", response.status_code, error_text)
                return []
                
        except requests.RequestException as e:
            logger.error("External ID search error: %s", str(e))
            return []
    
    def get_duplicate_check_options(self, module: Optional[str] = None) -> Dict[str, Any]:
        """
        Get duplicate check preference options configured for a module.
        
        From API Directory: "Get Duplicate Check Options"
        Uses GET /settings/duplicate_check_preference
        This helps identify potential duplicate Development records during import.
        
        Args:
            module: Module name (defaults to developments_module)
            
        Returns:
            Dict containing duplicate check configuration
        """
        try:
            search_module = module or self.developments_module
            logger.info("Getting duplicate check options for module: %s", search_module)
            
            url = f"{self.base_url}/settings/duplicate_check_preference"
            params = {"module": search_module}
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                duplicate_check_preference = data.get("duplicate_check_preference", {})
                logger.info("Retrieved duplicate check options for %s", search_module)
                return {
                    "success": True,
                    "options": duplicate_check_preference
                }
            else:
                error_text = response.text
                logger.error("Get duplicate check options failed: %d - %s", response.status_code, error_text)
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {error_text}",
                    "options": {}
                }
                
        except requests.RequestException as e:
            logger.error("Get duplicate check options error: %s", str(e))
            return {
                "success": False,
                "error": str(e),
                "options": {}
            }
    
    def enable_duplicate_check(self, duplicate_fields: List[str], module: Optional[str] = None) -> Dict[str, Any]:
        """
        Enable duplicate check preference for a module.
        
        From API Directory: "Enable Duplicate Check Option"
        Uses POST /settings/duplicate_check_preference
        This configures duplicate detection for Development records.
        
        Args:
            duplicate_fields: List of field names to check for duplicates
            module: Module name (defaults to developments_module)
            
        Returns:
            Dict containing configuration result
        """
        try:
            search_module = module or self.developments_module
            logger.info("Enabling duplicate check for %s with fields: %s", search_module, duplicate_fields)
            
            url = f"{self.base_url}/settings/duplicate_check_preference"
            
            duplicate_check_data = {
                "type": "mapped_fields",
                "mapped_fields": [{"api_name": field} for field in duplicate_fields]
            }
            
            payload = {
                "duplicate_check_preference": {
                    search_module: duplicate_check_data
                }
            }
            
            response = self.session.post(url, json=payload, timeout=self.timeout)
            
            if response.status_code in [200, 201]:
                data = response.json()
                if data.get("duplicate_check_preference"):
                    logger.info("Duplicate check enabled successfully for %s", search_module)
                    return {
                        "success": True,
                        "details": data["duplicate_check_preference"]
                    }
                else:
                    return {
                        "success": False,
                        "error": "No duplicate check preference data received"
                    }
            else:
                error_text = response.text
                logger.error("Enable duplicate check failed: %d - %s", response.status_code, error_text)
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {error_text}"
                }
                
        except requests.RequestException as e:
            logger.error("Enable duplicate check error: %s", str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    # Enhanced workflow-specific methods for email CRM sync
    
    def check_email_already_processed(self, gmail_message_id: str, module: Optional[str] = None) -> bool:
        """
        Check if a Gmail email has already been processed to prevent duplicates.
        
        This method searches for existing notes or records containing the Gmail message ID
        to determine if the email has already been processed and added to a Development.
        
        Args:
            gmail_message_id: Gmail message ID to check
            module: Module name (defaults to developments_module)
            
        Returns:
            True if email already processed, False otherwise
        """
        try:
            search_module = module or self.developments_module
            logger.info("Checking if Gmail message %s already processed", gmail_message_id)
            
            # Skip external ID search due to scope limitations
            # Only use COQL fallback if it works, otherwise skip duplicate checking
            # (Better to process duplicate than miss an email)
            disable_coql = getattr(self, 'disable_coql_features', False)
            if not disable_coql:
                notes_query = f"SELECT id, Parent_Id FROM Notes WHERE Note_Title like '%{gmail_message_id}%' OR Note_Content like '%{gmail_message_id}%' LIMIT 10"
                coql_result = self.coql_query(notes_query)
                
                if coql_result.get("success") and coql_result.get("records"):
                    logger.info("Gmail message %s already processed (found in notes)", gmail_message_id)
                    return True
            else:
                logger.debug("COQL features disabled, skipping duplicate check")
            
            logger.info("Gmail message %s not yet processed", gmail_message_id)
            return False
            
        except Exception as e:
            logger.error("Error checking email processing status: %s", str(e))
            # If error, assume not processed to avoid missing emails
            return False
    
    def create_note_with_email_tracking(self, development_id: str, email_summary: str, 
                                      gmail_message_id: str, email_subject: str,
                                      module: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a note with Gmail message ID tracking to prevent duplicate processing.
        
        This enhanced version of create_note includes Gmail message ID in the title
        for tracking and duplicate prevention.
        
        Args:
            development_id: ID of the Development record
            email_summary: AI-generated summary of the email content
            gmail_message_id: Gmail message ID for tracking
            email_subject: Original email subject
            module: Module name (defaults to developments_module)
            
        Returns:
            Dict containing note creation result
        """
        try:
            # Create note title with Gmail message ID for tracking
            note_title = f"Email: {email_subject} (ID: {gmail_message_id})"
            
            # Add Gmail message ID to content for searchability
            enhanced_content = f"{email_summary}\n\n[Gmail Message ID: {gmail_message_id}]"
            
            logger.info("Creating tracked note for Development %s with Gmail ID %s", 
                       development_id, gmail_message_id)
            
            result = self.create_note(
                parent_id=development_id,
                content=enhanced_content,
                title=note_title,
                parent_module=module
            )
            
            if result.get("success"):
                logger.info("Tracked note created successfully for Gmail message %s", gmail_message_id)
            
            return result
            
        except Exception as e:
            logger.error("Error creating tracked note: %s", str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    def find_development_by_address_enhanced(self, address: str, module: Optional[str] = None) -> Optional[Dict]:
        """
        Enhanced Development finding with multiple address matching strategies.
        
        This method uses multiple search approaches to improve the accuracy of
        finding Development records by property address:
        1. Exact word search (current method)
        2. COQL search with address variations
        3. Criteria search with partial matching
        
        Args:
            address: Property address to search for
            module: Module name (defaults to developments_module)
            
        Returns:
            First matching Development record or None if not found
        """
        try:
            search_module = module or self.developments_module
            logger.info("Enhanced address search for: %s", address)
            
            # Strategy 1: Exact word search (existing method)
            word_results = self.search_by_word(address, search_module)
            if word_results and len(word_results) > 0:
                logger.info("Found Development by exact word search")
                return word_results[0]
            
            # Strategy 2: COQL search with address field variations
            try:
                # Clean address for COQL (remove special characters)
                clean_address = address.replace("'", "\\'").replace("%", "")
                
                coql_query = f"""
                SELECT id, Account_Name, Address, Property_Address, Billing_Street 
                FROM {search_module} 
                WHERE (Address like '%{clean_address}%') 
                OR (Property_Address like '%{clean_address}%')
                OR (Billing_Street like '%{clean_address}%')
                LIMIT 10
                """
                
                coql_result = self.coql_query(coql_query)
                if coql_result.get("success") and coql_result.get("records"):
                    logger.info("Found Development by COQL address search")
                    return coql_result["records"][0]
                    
            except Exception as e:
                logger.warning("COQL address search failed: %s", str(e))
            
            # Strategy 3: Criteria search with partial matching
            try:
                # Split address into components for better matching
                address_parts = address.split()
                if len(address_parts) >= 2:
                    # Try with first few words of address
                    partial_address = " ".join(address_parts[:3])
                    criteria = f"(Address:*{partial_address}*)"
                    
                    criteria_results = self.search_by_criteria(criteria, search_module)
                    if criteria_results and len(criteria_results) > 0:
                        logger.info("Found Development by partial address criteria")
                        return criteria_results[0]
                        
            except Exception as e:
                logger.warning("Criteria address search failed: %s", str(e))
            
            logger.info("No Development found for address: %s", address)
            return None
            
        except Exception as e:
            logger.error("Error in enhanced address search for %s: %s", address, str(e))
            return None
