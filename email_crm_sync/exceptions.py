"""
Custom exceptions for the Email CRM Sync application.

This module defines application-specific exceptions that provide better
error handling and debugging capabilities.
"""


class CrmSyncError(Exception):
    """Base class for exceptions in this application."""
    

class ConfigurationError(CrmSyncError):
    """Raised when there's an issue with configuration."""
    

class ZohoApiError(CrmSyncError):
    """Raised for errors related to the Zoho API."""
    

class GmailApiError(CrmSyncError):
    """Raised for errors related to the Gmail API."""
    

class OpenAIApiError(CrmSyncError):
    """Raised for errors related to the OpenAI API."""
    

class NoteCreationError(ZohoApiError):
    """Raised when a note cannot be created in Zoho CRM."""
    

class RecordMatchingError(ZohoApiError):
    """Raised when there's an issue with record matching in Zoho CRM."""
    

class SearchError(ZohoApiError):
    """Raised when search operations fail in Zoho CRM."""
    

class TokenError(CrmSyncError):
    """Raised when there's an issue with API tokens."""
    

class EmailProcessingError(CrmSyncError):
    """Raised when there's an issue processing emails."""
