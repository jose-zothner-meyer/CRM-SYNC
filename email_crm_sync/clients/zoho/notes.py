"""
Zoho CRM Notes management module.

This module handles all note-related operations for Zoho CRM,
including creating, retrieving, and managing notes.
"""

import requests
import logging
from typing import Dict, Any, Optional, List
from ...exceptions import NoteCreationError, ZohoApiError

logger = logging.getLogger(__name__)


class Notes:
    """
    Handles note operations for Zoho CRM.
    
    This class provides methods to create, retrieve, and manage notes
    in Zoho CRM records.
    """
    
    def __init__(self, client):
        """
        Initialize the Notes handler.
        
        Args:
            client: The main Zoho client instance
        """
        self.client = client
        self.base_url = client.base_url
        self.headers = client.headers
        self.session = client.session
        self.timeout = client.timeout
    
    def create(self, parent_id: str, content: str, title: Optional[str] = None, 
               parent_module: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a note in Zoho CRM using the V8 Notes API.
        
        Args:
            parent_id: ID of the parent record
            content: Note content
            title: Optional note title
            parent_module: Parent module name (defaults to client's module)
            
        Returns:
            Dict containing the created note information
            
        Raises:
            NoteCreationError: If note creation fails
        """
        try:
            module = parent_module or self.client.developments_module
            
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
                            "details": created_note,
                            "data": created_note
                        }
                    else:
                        error_msg = created_note.get("message", "Unknown error")
                        error_code = created_note.get("code", "UNKNOWN")
                        logger.error("Note creation failed in response: %s", data)
                        raise NoteCreationError(f"Note creation failed [{error_code}]: {error_msg}")
                else:
                    raise NoteCreationError("No response data received")
            else:
                # Handle specific HTTP error codes based on API documentation
                error_text = response.text
                if response.status_code == 400:
                    if "INVALID_MODULE" in error_text:
                        logger.error("Invalid module specified: %s", module)
                        raise NoteCreationError(f"Invalid module '{module}': {error_text}")
                    elif "MANDATORY_NOT_FOUND" in error_text:
                        logger.error("Missing mandatory fields for note creation")
                        raise NoteCreationError(f"Missing mandatory fields: {error_text}")
                    elif "INVALID_DATA" in error_text:
                        logger.error("Invalid parent record ID: %s", parent_id)
                        raise NoteCreationError(f"Invalid parent record ID '{parent_id}': {error_text}")
                    else:
                        logger.error("Bad request for note creation: %s", error_text)
                        raise NoteCreationError(f"Bad request (400): {error_text}")
                elif response.status_code == 401:
                    if "OAUTH_SCOPE_MISMATCH" in error_text:
                        logger.error("OAuth scope mismatch - missing notes.CREATE scope")
                        raise ZohoApiError(f"OAuth scope mismatch: {error_text}")
                    else:
                        logger.error("Unauthorized note creation request")
                        raise ZohoApiError(f"Unauthorized (401): {error_text}")
                elif response.status_code == 403:
                    logger.error("Permission denied for note creation")
                    raise ZohoApiError(f"Permission denied (403): {error_text}")
                elif response.status_code == 404:
                    logger.error("Invalid URL pattern for note creation")
                    raise NoteCreationError(f"Invalid URL pattern (404): {error_text}")
                elif response.status_code == 500:
                    logger.error("Internal server error during note creation")
                    raise ZohoApiError(f"Internal server error (500): {error_text}")
                else:
                    logger.error("Note creation failed: %d - %s", response.status_code, error_text)
                    raise NoteCreationError(f"HTTP {response.status_code}: {error_text}")
                
        except requests.RequestException as e:
            logger.error("Note creation error: %s", str(e))
            raise NoteCreationError(f"Request failed: {str(e)}") from e
    
    def get(self, parent_id: Optional[str] = None, parent_module: Optional[str] = None,
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
            
        Raises:
            ZohoApiError: If the request fails
        """
        try:
            # Determine endpoint based on parameters
            if note_id:
                # Get specific note
                url = f"{self.base_url}/Notes/{note_id}"
                logger.info("Getting specific note: %s", note_id)
            elif parent_id and parent_module:
                # Get notes for specific record
                module = parent_module or self.client.developments_module
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
                    "info": info,
                    "data": notes
                }
            else:
                error_text = response.text
                logger.error("Get notes failed: %d - %s", response.status_code, error_text)
                raise ZohoApiError(f"HTTP {response.status_code}: {error_text}")
                
        except requests.RequestException as e:
            logger.error("Get notes error: %s", str(e))
            raise ZohoApiError(f"Request failed: {str(e)}") from e
    
    def list_by_parent(self, parent_id: str, parent_module: Optional[str] = None,
                       fields: Optional[List[str]] = None, page: int = 1, per_page: int = 200) -> Dict[str, Any]:
        """
        Get all notes for a specific parent record.
        
        Args:
            parent_id: ID of the parent record
            parent_module: Module name (defaults to client's module)
            fields: Specific fields to retrieve
            page: Page number (default: 1)
            per_page: Records per page (default: 200, max: 200)
            
        Returns:
            Dict containing notes data and metadata
        """
        return self.get(
            parent_id=parent_id,
            parent_module=parent_module,
            fields=fields,
            page=page,
            per_page=per_page
        )

    def update(self, note_id: str, title: Optional[str] = None, content: Optional[str] = None) -> Dict[str, Any]:
        """
        Update an existing note using V8 Notes API.
        
        Uses PUT /Notes/{note_id} for updating note content and title.
        At least one of title or content must be provided.
        
        Args:
            note_id: ID of the note to update
            title: New note title (optional)
            content: New note content (optional)
            
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

    def create_multiple(self, notes_data: List[Dict], parent_module: Optional[str] = None) -> Dict[str, Any]:
        """
        Create multiple notes in a single API call using bulk operations.
        
        Uses POST /Notes with multiple note records for efficient bulk creation.
        Each note in notes_data should have parent_id, content, and optionally title.
        
        Args:
            notes_data: List of note dictionaries with parent_id, content, title
            parent_module: Parent module name (defaults to client's developments_module)
            
        Returns:
            Dict containing bulk creation results
        """
        try:
            module = parent_module or self.client.developments_module
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
