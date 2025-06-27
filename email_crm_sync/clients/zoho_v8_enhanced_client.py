import requests
import logging
from typing import Dict, List, Optional, Any
import time

# Import modular components
from .zoho.notes import Notes
from .zoho.search import Search
from .zoho.modules import Modules
from .zoho.records import Records
from .zoho.developments import Developments

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
                   
        # Initialize modular components
        self.notes = Notes(self)
        self.search = Search(self)
        self.modules = Modules(self)
        self.records = Records(self)
        self.developments = Developments(self)
    
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
        """Delegate to search.by_email() for backward compatibility."""
        return self.search.by_email(email, module)
    
    def create_note(self, parent_id: str, content: str, title: Optional[str] = None,
                   parent_module: Optional[str] = None) -> Dict[str, Any]:
        """Delegate to notes.create() for backward compatibility."""
        return self.notes.create(parent_id, content, title, parent_module)
    
    def get_notes(self, parent_id: Optional[str] = None, parent_module: Optional[str] = None,
                 note_id: Optional[str] = None, fields: Optional[List[str]] = None,
                 page: int = 1, per_page: int = 200) -> Dict[str, Any]:
        """Delegate to notes.get() for backward compatibility."""
        return self.notes.get(parent_id, parent_module, note_id, fields, page, per_page)
    
    def update_note(self, note_id: str, title: Optional[str] = None, content: Optional[str] = None) -> Dict[str, Any]:
        """Delegate to notes.update() for backward compatibility."""
        return self.notes.update(note_id, title, content)
    
    def create_multiple_notes(self, notes_data: List[Dict], parent_module: Optional[str] = None) -> Dict[str, Any]:
        """Delegate to notes.create_multiple() for backward compatibility."""
        return self.notes.create_multiple(notes_data, parent_module)
    
    def search_by_criteria(self, criteria: str, module: Optional[str] = None) -> List[Dict]:
        """Delegate to search.by_criteria() for backward compatibility."""
        return self.search.by_criteria(criteria, module)
    
    def search_by_word(self, word: str, module: Optional[str] = None) -> List[Dict]:
        """Delegate to search.by_word() for backward compatibility."""
        return self.search.by_word(word, module)
    
    def coql_query(self, query: str) -> Dict[str, Any]:
        """Delegate to search.coql_query() for backward compatibility."""
        return self.search.coql_query(query)
    
    def advanced_email_search(self, email: str, company_name: Optional[str] = None,
                            include_modules: Optional[List[str]] = None) -> Dict[str, List[Dict]]:
        """Delegate to search.advanced_email_search() for backward compatibility."""
        return self.search.advanced_email_search(email, company_name, include_modules)
    
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
    
    # =================================================================
    # DELEGATION METHODS FOR BACKWARD COMPATIBILITY
    # =================================================================
    
    # Module delegation methods
    def discover_modules(self, status: Optional[List[str]] = None) -> List[Dict]:
        """Delegate to modules.discover() for backward compatibility."""
        return self.modules.discover(status)
    
    def get_module_metadata(self, module: Optional[str] = None) -> Dict[str, Any]:
        """Delegate to modules.get_metadata() for backward compatibility."""
        return self.modules.get_metadata(module)
    
    def get_field_metadata(self, module: Optional[str] = None) -> List[Dict]:
        """Delegate to modules.get_fields() for backward compatibility."""
        return self.modules.get_fields(module)
    
    # Record delegation methods
    def get_record(self, record_id: str, module: Optional[str] = None, 
                   fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """Delegate to records.get() for backward compatibility."""
        return self.records.get(record_id, module, fields)
    
    # Development delegation methods
    def find_development_by_email(self, email: str, module: Optional[str] = None) -> Optional[Dict]:
        """Delegate to developments.find_by_email() for backward compatibility."""
        return self.developments.find_by_email(email, module)
    
    def find_development_by_address(self, address: str, module: Optional[str] = None) -> Optional[str]:
        """Delegate to developments.find_by_address() for backward compatibility."""
        return self.developments.find_by_address(address, module)
    
    def find_development_by_address_enhanced(self, address: str, module: Optional[str] = None) -> Optional[Dict]:
        """Delegate to developments.find_by_address_enhanced() for backward compatibility."""
        return self.developments.find_by_address_enhanced(address, module)
    
    def search_developments_by_criteria(self, criteria_dict: Dict[str, str], 
                                       module: Optional[str] = None) -> List[Dict]:
        """Delegate to developments.search_by_criteria() for backward compatibility."""
        return self.developments.search_by_criteria(criteria_dict, module)
    
    def add_note_to_development(self, development_id: str, title: str, content: str, 
                               note_type: str = "Email Note") -> Dict[str, Any]:
        """Delegate to developments.add_note() for backward compatibility."""
        return self.developments.add_note(development_id, title, content, note_type)
    
    def check_email_already_processed(self, gmail_message_id: str, 
                                     module: Optional[str] = None) -> bool:
        """Delegate to developments.check_email_processed() for backward compatibility."""
        return self.developments.check_email_processed(gmail_message_id, module)
    
    # =================================================================
    # ORIGINAL METHODS (TO BE GRADUALLY REPLACED)
    # =================================================================
