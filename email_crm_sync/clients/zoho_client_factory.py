"""
Unified Zoho CRM Client Factory

This module provides a unified interface for creating Zoho CRM clients
with proper EU data center support and all advanced functionalities.

The factory creates the enhanced V8 client with EU support and comprehensive features.
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, Union
import logging

# Import client implementation
from .zoho_v8_enhanced_client import ZohoV8EnhancedClient

logger = logging.getLogger(__name__)


def load_config(config_path: Union[str, Path]) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    try:
        config_path = Path(config_path)
        with open(config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file) or {}
    except (OSError, yaml.YAMLError) as e:
        logger.error("Failed to load config from %s: %s", config_path, e)
        return {}


def create_zoho_client(
    config_path: Optional[str] = None,
    access_token: Optional[str] = None,
    region: str = "eu",
    developments_module: str = "Developments",
    timeout: int = 30
) -> ZohoV8EnhancedClient:
    """
    Factory function to create a Zoho CRM client with EU support.
    
    This function creates the enhanced V8 client with proper EU data center
    endpoints and all advanced functionality for email-CRM sync.
    
    Args:
        config_path: Path to API keys configuration file
        access_token: Direct access token (if not using config file)
        region: Data center region ('eu' or 'us')
        developments_module: Name of the developments module
        timeout: Request timeout in seconds
        
    Returns:
        Configured Zoho CRM client instance
        
    Raises:
        ValueError: If neither config_path nor access_token is provided
        FileNotFoundError: If config file doesn't exist
    """
    
    logger.info("Creating Zoho V8 Enhanced client for %s region", region.upper())
    
    if not access_token:
        if config_path:
            # Load token from config
            if not os.path.exists(config_path):
                raise FileNotFoundError(f"Config file not found: {config_path}")
                
            config = load_config(config_path)
            access_token = config.get('zoho', {}).get('access_token')
            
            if not access_token:
                raise ValueError("No access token found in config file")
        else:
            raise ValueError("Either config_path or access_token must be provided")
    
    # Map region to data center
    data_center = "eu" if region.lower() == "eu" else "com"
    
    return ZohoV8EnhancedClient(
        access_token=access_token,
        data_center=data_center,
        developments_module=developments_module,
        timeout=timeout
    )


def create_eu_client(config_path: str, **kwargs) -> ZohoV8EnhancedClient:
    """
    Convenience function to create an EU client.
    
    Args:
        config_path: Path to API keys configuration file
        **kwargs: Additional arguments for ZohoV8EnhancedClient
        
    Returns:
        Configured EU Zoho CRM client
    """
    return create_zoho_client(
        config_path=config_path,
        region="eu",
        **kwargs
    )


def create_us_client(config_path: str, **kwargs) -> ZohoV8EnhancedClient:
    """
    Convenience function to create a US client.
    
    Args:
        config_path: Path to API keys configuration file
        **kwargs: Additional arguments for ZohoV8EnhancedClient
        
    Returns:
        Configured US Zoho CRM client
    """
    return create_zoho_client(
        config_path=config_path,
        region="us",
        **kwargs
    )


def create_client_with_token(access_token: str, region: str = "eu", **kwargs) -> ZohoV8EnhancedClient:
    """
    Convenience function to create a client with direct token.
    
    Args:
        access_token: Zoho CRM access token
        region: Data center region ('eu' or 'us')
        **kwargs: Additional arguments for ZohoV8EnhancedClient
        
    Returns:
        Configured Zoho CRM client
    """
    return create_zoho_client(
        access_token=access_token,
        region=region,
        **kwargs
    )


def get_recommended_client(config_path: str) -> ZohoV8EnhancedClient:
    """
    Get the recommended client based on available configuration.
    
    This function analyzes the configuration and returns a configured client
    with the appropriate region settings.
    
    Args:
        config_path: Path to API keys configuration file
        
    Returns:
        Configured Zoho CRM client instance
        
    Raises:
        ValueError: If no valid credentials are found
    """
    config = load_config(config_path)
    zoho_config = config.get('zoho', {})
    
    access_token = zoho_config.get('access_token')
    
    if not access_token:
        raise ValueError("No access token found in config file")
    
    # Default to EU region
    region = "eu"
    
    logger.info("Creating recommended client for %s region", region.upper())
    return create_zoho_client(
        config_path=config_path,
        region=region
    )


def test_client_connection(client: ZohoV8EnhancedClient) -> Dict[str, Any]:
    """
    Test the connection of a Zoho client.
    
    Args:
        client: Zoho CRM client instance to test
        
    Returns:
        Dict containing test results
    """
    try:
        logger.info("Testing client connection...")
        result = client.test_connection()
        
        if result.get("success"):
            logger.info("✅ Client connection test passed")
        else:
            logger.warning("⚠️ Client connection test failed: %s", result.get("error"))
            
        return result
        
    except (ValueError, ConnectionError, TimeoutError) as e:
        logger.error("❌ Client connection test error: %s", e)
        return {
            "success": False,
            "error": str(e)
        }


# Aliases for backward compatibility and convenience
ZohoClient = create_zoho_client
ZohoEUClient = create_eu_client
ZohoUSClient = create_us_client
