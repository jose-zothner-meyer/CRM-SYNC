"""
Centralized configuration management for the Email CRM Sync application.

This module provides a singleton configuration instance that can be imported and used
throughout the application without reloading config files multiple times.

Usage:
    from email_crm_sync.config import config
    
    # Access configuration values
    openai_key = config.openai_key
    zoho_token = config.zoho_token
    gmail_credentials = config.gmail_credentials
    
    # Get configuration dictionaries
    zoho_config = config.get_zoho_config()
    openai_config = config.get_openai_config()

The ConfigLoader uses a singleton pattern to ensure:
- Configuration is loaded only once
- All parts of the application use the same configuration
- Better performance by avoiding repeated file reads
- Consistent configuration across all modules
"""

from .loader import ConfigLoader

# Create a single instance of ConfigLoader that will be shared across the application
config = ConfigLoader()

__all__ = ['config']
