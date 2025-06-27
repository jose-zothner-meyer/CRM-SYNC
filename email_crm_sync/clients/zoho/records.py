"""
Zoho CRM Records management module.

This module handles record operations including retrieval,
creation, and basic record management.
"""

import requests
import logging
from typing import Dict, Any, Optional, List
from ...exceptions import ZohoApiError

logger = logging.getLogger(__name__)


class Records:
    """
    Handles record operations for Zoho CRM.
    
    This class provides methods to retrieve, create, and manage
    records in Zoho CRM modules.
    """
    
    def __init__(self, client):
        """
        Initialize the Records handler.
        
        Args:
            client: The main Zoho client instance
        """
        self.client = client
        self.base_url = client.base_url
        self.headers = client.headers
        self.session = client.session
        self.timeout = client.timeout
    
    def get(self, record_id: str, module: Optional[str] = None, 
            fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get a specific record by ID.
        
        Args:
            record_id: The ID of the record to retrieve
            module: Module name (defaults to client's developments_module)
            fields: Optional list of fields to retrieve
            
        Returns:
            Dict containing record data
            
        Raises:
            ZohoApiError: If record retrieval fails
        """
        try:
            module_name = module or self.client.developments_module
            
            logger.info("Getting record %s from module: %s", record_id, module_name)
            
            url = f"{self.base_url}/{module_name}/{record_id}"
            params = {}
            
            if fields:
                params['fields'] = ','.join(fields)
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                if "data" in data and len(data["data"]) > 0:
                    record = data["data"][0]
                    logger.info("Successfully retrieved record: %s", record_id)
                    return record
                else:
                    raise ZohoApiError(f"Record not found: {record_id}")
            elif response.status_code == 404:
                raise ZohoApiError(f"Record not found: {record_id}")
            else:
                error_msg = f"Record retrieval failed: HTTP {response.status_code}"
                logger.error("%s - %s", error_msg, response.text)
                raise ZohoApiError(error_msg)
                
        except requests.RequestException as e:
            logger.error("Record retrieval error: %s", str(e))
            raise ZohoApiError(f"Record retrieval failed: {str(e)}") from e
    
    def get_multiple(self, record_ids: List[str], module: Optional[str] = None,
                    fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Get multiple records by their IDs.
        
        Args:
            record_ids: List of record IDs to retrieve
            module: Module name (defaults to client's developments_module)
            fields: Optional list of fields to retrieve
            
        Returns:
            List of record dictionaries
            
        Raises:
            ZohoApiError: If record retrieval fails
        """
        try:
            module_name = module or self.client.developments_module
            
            logger.info("Getting %d records from module: %s", len(record_ids), module_name)
            
            url = f"{self.base_url}/{module_name}"
            params = {
                'ids': ','.join(record_ids)
            }
            
            if fields:
                params['fields'] = ','.join(fields)
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                records = data.get("data", [])
                
                logger.info("Successfully retrieved %d records", len(records))
                return records
            else:
                error_msg = f"Multiple record retrieval failed: HTTP {response.status_code}"
                logger.error("%s - %s", error_msg, response.text)
                raise ZohoApiError(error_msg)
                
        except requests.RequestException as e:
            logger.error("Multiple record retrieval error: %s", str(e))
            raise ZohoApiError(f"Multiple record retrieval failed: {str(e)}") from e
    
    def create(self, record_data: Dict[str, Any], module: Optional[str] = None,
               duplicate_check_fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a new record.
        
        Args:
            record_data: Dictionary containing record field data
            module: Module name (defaults to client's developments_module)
            duplicate_check_fields: Optional fields to check for duplicates
            
        Returns:
            Dict containing creation result
            
        Raises:
            ZohoApiError: If record creation fails
        """
        try:
            module_name = module or self.client.developments_module
            
            logger.info("Creating new record in module: %s", module_name)
            
            url = f"{self.base_url}/{module_name}"
            payload = {"data": [record_data]}
            
            # Add duplicate check if specified
            if duplicate_check_fields:
                payload["duplicate_check_fields"] = [{"field": field} for field in duplicate_check_fields]
            
            response = self.session.post(url, json=payload, timeout=self.timeout)
            
            if response.status_code in [200, 201]:
                data = response.json()
                
                if "data" in data and len(data["data"]) > 0:
                    result = data["data"][0]
                    
                    if result.get("code") == "SUCCESS":
                        record_id = result.get("details", {}).get("id")
                        logger.info("Successfully created record: %s", record_id)
                        return {
                            "success": True,
                            "record_id": record_id,
                            "details": result
                        }
                    else:
                        error_msg = result.get("message", "Unknown error")
                        logger.error("Record creation failed: %s", error_msg)
                        raise ZohoApiError(f"Record creation failed: {error_msg}")
                else:
                    raise ZohoApiError("No response data received")
            else:
                error_msg = f"Record creation failed: HTTP {response.status_code}"
                logger.error("%s - %s", error_msg, response.text)
                raise ZohoApiError(error_msg)
                
        except requests.RequestException as e:
            logger.error("Record creation error: %s", str(e))
            raise ZohoApiError(f"Record creation failed: {str(e)}") from e
    
    def update(self, record_id: str, record_data: Dict[str, Any], 
               module: Optional[str] = None) -> Dict[str, Any]:
        """
        Update an existing record.
        
        Args:
            record_id: ID of the record to update
            record_data: Dictionary containing updated field data
            module: Module name (defaults to client's developments_module)
            
        Returns:
            Dict containing update result
            
        Raises:
            ZohoApiError: If record update fails
        """
        try:
            module_name = module or self.client.developments_module
            
            logger.info("Updating record %s in module: %s", record_id, module_name)
            
            url = f"{self.base_url}/{module_name}/{record_id}"
            payload = {"data": [record_data]}
            
            response = self.session.put(url, json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                if "data" in data and len(data["data"]) > 0:
                    result = data["data"][0]
                    
                    if result.get("code") == "SUCCESS":
                        logger.info("Successfully updated record: %s", record_id)
                        return {
                            "success": True,
                            "record_id": record_id,
                            "details": result
                        }
                    else:
                        error_msg = result.get("message", "Unknown error")
                        logger.error("Record update failed: %s", error_msg)
                        raise ZohoApiError(f"Record update failed: {error_msg}")
                else:
                    raise ZohoApiError("No response data received")
            else:
                error_msg = f"Record update failed: HTTP {response.status_code}"
                logger.error("%s - %s", error_msg, response.text)
                raise ZohoApiError(error_msg)
                
        except requests.RequestException as e:
            logger.error("Record update error: %s", str(e))
            raise ZohoApiError(f"Record update failed: {str(e)}") from e
    
    def delete(self, record_id: str, module: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete a record.
        
        Args:
            record_id: ID of the record to delete
            module: Module name (defaults to client's developments_module)
            
        Returns:
            Dict containing deletion result
            
        Raises:
            ZohoApiError: If record deletion fails
        """
        try:
            module_name = module or self.client.developments_module
            
            logger.info("Deleting record %s from module: %s", record_id, module_name)
            
            url = f"{self.base_url}/{module_name}/{record_id}"
            
            response = self.session.delete(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                if "data" in data and len(data["data"]) > 0:
                    result = data["data"][0]
                    
                    if result.get("code") == "SUCCESS":
                        logger.info("Successfully deleted record: %s", record_id)
                        return {
                            "success": True,
                            "record_id": record_id,
                            "details": result
                        }
                    else:
                        error_msg = result.get("message", "Unknown error")
                        logger.error("Record deletion failed: %s", error_msg)
                        raise ZohoApiError(f"Record deletion failed: {error_msg}")
                else:
                    raise ZohoApiError("No response data received")
            else:
                error_msg = f"Record deletion failed: HTTP {response.status_code}"
                logger.error("%s - %s", error_msg, response.text)
                raise ZohoApiError(error_msg)
                
        except requests.RequestException as e:
            logger.error("Record deletion error: %s", str(e))
            raise ZohoApiError(f"Record deletion failed: {str(e)}") from e
