"""
Zoho CRM Modules management module.

This module handles module discovery, metadata retrieval,
and module-related operations.
"""

import requests
import logging
from typing import Dict, Any, Optional, List
from ...exceptions import ZohoApiError

logger = logging.getLogger(__name__)


class Modules:
    """
    Handles module operations for Zoho CRM.
    
    This class provides methods to discover modules, retrieve metadata,
    and manage module-related operations.
    """
    
    def __init__(self, client):
        """
        Initialize the Modules handler.
        
        Args:
            client: The main Zoho client instance
        """
        self.client = client
        self.base_url = client.base_url
        self.headers = client.headers
        self.session = client.session
        self.timeout = client.timeout
    
    def discover(self, status: Optional[List[str]] = None) -> List[Dict]:
        """
        Discover all available modules in the Zoho CRM.
        
        Args:
            status: Optional list of module statuses to filter by
            
        Returns:
            List of module information dictionaries
            
        Raises:
            ZohoApiError: If module discovery fails
        """
        try:
            cache_key = f"modules_{status or 'all'}"
            
            # Check cache first (24 hour TTL for modules)
            if self.client._is_cache_valid(cache_key, ttl_hours=24):
                cached_data = self.client._module_cache.get(cache_key)
                if cached_data:
                    logger.info("Using cached module data")
                    return cached_data
            
            url = f"{self.base_url}/settings/modules"
            params = {}
            
            if status:
                params['status'] = ','.join(status)
            
            logger.info("Discovering modules from Zoho CRM")
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                modules = data.get("modules", [])
                
                # Cache the results
                self.client._update_cache(cache_key, modules)
                
                logger.info("Successfully discovered %d modules", len(modules))
                return modules
            else:
                error_msg = f"Module discovery failed: HTTP {response.status_code}"
                logger.error("%s - %s", error_msg, response.text)
                raise ZohoApiError(error_msg)
                
        except requests.RequestException as e:
            logger.error("Module discovery error: %s", str(e))
            raise ZohoApiError(f"Module discovery failed: {str(e)}")
    
    def get_metadata(self, module: Optional[str] = None) -> Dict[str, Any]:
        """
        Get metadata for a specific module.
        
        Args:
            module: Module name (defaults to client's developments_module)
            
        Returns:
            Dict containing module metadata
            
        Raises:
            ZohoApiError: If metadata retrieval fails
        """
        try:
            module_name = module or self.client.developments_module
            cache_key = f"metadata_{module_name}"
            
            # Check cache first (12 hour TTL for metadata)
            if self.client._is_cache_valid(cache_key, ttl_hours=12):
                cached_data = self.client._module_cache.get(cache_key)
                if cached_data:
                    logger.info("Using cached metadata for module: %s", module_name)
                    return cached_data
            
            url = f"{self.base_url}/settings/modules/{module_name}"
            
            logger.info("Getting metadata for module: %s", module_name)
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                if "modules" in data and len(data["modules"]) > 0:
                    metadata = data["modules"][0]
                    
                    # Cache the results
                    self.client._update_cache(cache_key, metadata)
                    
                    logger.info("Successfully retrieved metadata for module: %s", module_name)
                    return metadata
                else:
                    raise ZohoApiError(f"No metadata found for module: {module_name}")
            else:
                error_msg = f"Metadata retrieval failed: HTTP {response.status_code}"
                logger.error("%s - %s", error_msg, response.text)
                raise ZohoApiError(error_msg)
                
        except requests.RequestException as e:
            logger.error("Metadata retrieval error: %s", str(e))
            raise ZohoApiError(f"Metadata retrieval failed: {str(e)}")
    
    def get_fields(self, module: Optional[str] = None) -> List[Dict]:
        """
        Get field metadata for a specific module.
        
        Args:
            module: Module name (defaults to client's developments_module)
            
        Returns:
            List of field metadata dictionaries
            
        Raises:
            ZohoApiError: If field metadata retrieval fails
        """
        try:
            module_name = module or self.client.developments_module
            cache_key = f"fields_{module_name}"
            
            # Check cache first (12 hour TTL for fields)
            if self.client._is_cache_valid(cache_key, ttl_hours=12):
                cached_data = self.client._field_cache.get(cache_key)
                if cached_data:
                    logger.info("Using cached field metadata for module: %s", module_name)
                    return cached_data
            
            url = f"{self.base_url}/settings/fields"
            params = {"module": module_name}
            
            logger.info("Getting field metadata for module: %s", module_name)
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                fields = data.get("fields", [])
                
                # Cache the results
                self.client._field_cache[cache_key] = fields
                self.client._update_cache(cache_key, fields)
                
                logger.info("Successfully retrieved %d fields for module: %s", len(fields), module_name)
                return fields
            else:
                error_msg = f"Field metadata retrieval failed: HTTP {response.status_code}"
                logger.error("%s - %s", error_msg, response.text)
                raise ZohoApiError(error_msg)
                
        except requests.RequestException as e:
            logger.error("Field metadata retrieval error: %s", str(e))
            raise ZohoApiError(f"Field metadata retrieval failed: {str(e)}")
    
    def test_access(self, module: Optional[str] = None) -> Dict[str, Any]:
        """
        Test access to a specific module.
        
        Args:
            module: Module name (defaults to client's developments_module)
            
        Returns:
            Dict containing test results
        """
        module_name = module or self.client.developments_module
        try:
            
            logger.info("Testing access to module: %s", module_name)
            
            # Try to get module metadata
            metadata = self.get_metadata(module_name)
            
            # Try to get a few records to test read access
            url = f"{self.base_url}/{module_name}"
            params = {"per_page": 1}
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                records = data.get("data", [])
                
                return {
                    "success": True,
                    "module": module_name,
                    "metadata_accessible": True,
                    "records_accessible": True,
                    "sample_record_count": len(records),
                    "module_display_name": metadata.get("display_label", module_name)
                }
            else:
                return {
                    "success": False,
                    "module": module_name,
                    "metadata_accessible": True,
                    "records_accessible": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error("Module access test failed: %s", str(e))
            return {
                "success": False,
                "module": module_name,
                "metadata_accessible": False,
                "records_accessible": False,
                "error": str(e)
            }
