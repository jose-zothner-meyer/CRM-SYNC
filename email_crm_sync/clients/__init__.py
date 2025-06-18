"""
Email CRM Sync - Client Modules

This package contains all the client implementations for interacting with
external APIs including Gmail, OpenAI, and Zoho CRM.
"""

from .gmail_client import GmailClient
from .openai_client import OpenAISummarizer
from .zoho_v8_enhanced_client import ZohoV8EnhancedClient
from .zoho_client_factory import (
    create_zoho_client,
    create_eu_client,
    create_us_client,
    create_client_with_token,
    get_recommended_client,
    test_client_connection,
    ZohoClient,
    ZohoEUClient,
    ZohoUSClient
)

__all__ = [
    'GmailClient',
    'OpenAISummarizer', 
    'ZohoV8EnhancedClient',
    'create_zoho_client',
    'create_eu_client',
    'create_us_client',
    'create_client_with_token',
    'get_recommended_client',
    'test_client_connection',
    'ZohoClient',
    'ZohoEUClient',
    'ZohoUSClient'
]