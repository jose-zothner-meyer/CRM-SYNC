#!/usr/bin/env python3
"""
Enhanced Zoho OAuth Token Exchange Tool

This tool exchanges Zoho authorization codes for access and refresh tokens.
Integrated with the unified CRM-SYNC system with improved error handling.

SECURITY: Authorization codes are handled securely and cleared after use.

Usage:
    python exchange_new_tokens.py [authorization_code]
    
    # From main CLI (recommended)
    python main.py token exchange --code "1000.abcd1234.efgh5678"

Example:
    python exchange_new_tokens.py "1000.abcd1234.efgh5678"
"""

import requests
import yaml
import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TokenExchangeError(Exception):
    """Custom exception for token exchange errors"""
    pass

def load_config() -> tuple[Dict[str, Any], str]:
    """
    Load configuration from multiple possible locations.
    
    Returns:
        Tuple of (config_dict, config_path)
        
    Raises:
        FileNotFoundError: If no config file is found
    """
    config_paths = [
        "../email_crm_sync/config/api_keys.yaml",  # From tools/ subdirectory
        "../config/api_keys.yaml",                 # From tools/ to project root config
        "config/api_keys.yaml",                    # From project root
        "email_crm_sync/config/api_keys.yaml"      # From project root to package config
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as file:
                    config = yaml.safe_load(file)
                logger.info("✅ Using config: %s", config_path)
                return config, config_path
            except (yaml.YAMLError, IOError) as e:
                logger.warning("Failed to load config from %s: %s", config_path, e)
                continue
    
    logger.error("❌ Config file not found!")
    logger.error("   Searched in:")
    for path in config_paths:
        logger.error("   - %s", path)
    raise FileNotFoundError("No valid config file found")

def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate required configuration fields.
    
    Args:
        config: Configuration dictionary
        
    Raises:
        TokenExchangeError: If required fields are missing
    """
    required_fields = ['zoho_client_id', 'zoho_client_secret']
    missing_fields = [field for field in required_fields if not config.get(field)]
    
    if missing_fields:
        raise TokenExchangeError(f"Missing required fields: {', '.join(missing_fields)}")

def get_authorization_code(config: Dict[str, Any], provided_code: Optional[str] = None) -> str:
    """
    Get authorization code from various sources.
    
    Args:
        config: Configuration dictionary
        provided_code: Code provided as parameter
        
    Returns:
        Authorization code
        
    Raises:
        TokenExchangeError: If no valid authorization code is found
    """
    # Priority order: provided_code > environment variable > config file
    auth_code = provided_code
    
    if not auth_code:
        auth_code = os.environ.get('ZOHO_AUTH_CODE', '')
        if auth_code:
            logger.info("✅ Using authorization code from environment variable")
    
    if not auth_code:
        auth_code = config.get('zoho_authorization_code', '')
        if auth_code:
            logger.info("✅ Using authorization code from config file")
    
    if not auth_code or auth_code.strip() == "":
        raise TokenExchangeError(
            "No authorization code provided!\n"
            "   Please either:\n"
            "   1. Pass it as a command line argument\n"
            "   2. Set ZOHO_AUTH_CODE environment variable\n"
            "   3. Add 'zoho_authorization_code' to your api_keys.yaml file"
        )
    
    return auth_code.strip()

def get_token_url(data_center: str) -> str:
    """
    Get the appropriate token URL for the data center.
    
    Args:
        data_center: Zoho data center (eu, com, in, etc.)
        
    Returns:
        Token URL for the data center
    """
    # Mapping of data centers to account domains
    domain_mapping = {
        'eu': 'https://accounts.zoho.eu',
        'com': 'https://accounts.zoho.com',
        'in': 'https://accounts.zoho.in',
        'com.au': 'https://accounts.zoho.com.au',
        'jp': 'https://accounts.zoho.jp'
    }
    
    base_domain = domain_mapping.get(data_center.lower(), f'https://accounts.zoho.{data_center}')
    return f"{base_domain}/oauth/v2/token"

def exchange_tokens_request(auth_code: str, client_id: str, client_secret: str, 
                           data_center: str) -> Dict[str, Any]:
    """
    Make the token exchange request to Zoho.
    
    Args:
        auth_code: Authorization code
        client_id: Zoho client ID
        client_secret: Zoho client secret
        data_center: Data center location
        
    Returns:
        Token response data
        
    Raises:
        TokenExchangeError: If token exchange fails
    """
    token_url = get_token_url(data_center)
    
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'code': auth_code
    }
    
    logger.info("🔄 Requesting tokens from: %s", token_url)
    
    try:
        response = requests.post(token_url, data=token_data, timeout=30)
        
        if response.status_code == 200:
            token_response = response.json()
            
            if 'access_token' in token_response:
                logger.info("✅ Token exchange successful!")
                return token_response
            else:
                error_msg = token_response.get('error_description', 'Unknown error')
                raise TokenExchangeError(f"Token exchange failed: {error_msg}")
        else:
            try:
                error_data = response.json()
                error_msg = error_data.get('error_description', response.text)
            except ValueError:
                error_msg = response.text
            
            raise TokenExchangeError(f"HTTP {response.status_code}: {error_msg}")
            
    except requests.RequestException as e:
        raise TokenExchangeError(f"Network error during token exchange: {str(e)}") from e

def update_config_files(token_response: Dict[str, Any], config: Dict[str, Any], 
                       config_path: str) -> None:
    """
    Update configuration files with new tokens.
    
    Args:
        token_response: Response from token exchange
        config: Current configuration
        config_path: Path to config file
    """
    # Calculate token expiration time
    expires_in = token_response.get('expires_in', 3600)
    expires_at = datetime.now() + timedelta(seconds=expires_in)
    
    # Update configuration
    config['zoho_token'] = token_response['access_token']
    config['zoho_refresh_token'] = token_response['refresh_token']
    config['zoho_token_expires_at'] = expires_at.isoformat()
    
    # Clear the authorization code for security
    if 'zoho_authorization_code' in config:
        del config['zoho_authorization_code']
    
    # Update primary config file
    try:
        with open(config_path, 'w', encoding='utf-8') as file:
            yaml.dump(config, file, default_flow_style=False, sort_keys=False)
        logger.info("✅ Updated primary config: %s", config_path)
    except IOError as e:
        logger.error("Failed to update primary config: %s", e)
    
    # Update secondary config file if it exists
    secondary_config_paths = [
        "config/api_keys.yaml",
        "email_crm_sync/config/api_keys.yaml"
    ]
    
    for secondary_path in secondary_config_paths:
        if os.path.exists(secondary_path) and secondary_path != config_path:
            try:
                with open(secondary_path, 'r', encoding='utf-8') as file:
                    secondary_config = yaml.safe_load(file)
                
                # Update with new tokens
                secondary_config.update({
                    'zoho_token': token_response['access_token'],
                    'zoho_refresh_token': token_response['refresh_token'],
                    'zoho_token_expires_at': expires_at.isoformat()
                })
                
                # Clear authorization code
                if 'zoho_authorization_code' in secondary_config:
                    del secondary_config['zoho_authorization_code']
                
                with open(secondary_path, 'w', encoding='utf-8') as file:
                    yaml.dump(secondary_config, file, default_flow_style=False, sort_keys=False)
                
                logger.info("✅ Updated secondary config: %s", secondary_path)
                
            except (IOError, yaml.YAMLError) as e:
                logger.warning("Failed to update secondary config %s: %s", secondary_path, e)

def exchange_authorization_code(auth_code: Optional[str] = None) -> bool:
    """
    Main function to exchange authorization code for tokens.
    
    Args:
        auth_code: Optional authorization code
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("=== ZOHO OAUTH TOKEN EXCHANGE ===")
        
        # Load configuration
        config, config_path = load_config()
        
        # Validate configuration
        validate_config(config)
        
        # Get authorization code
        auth_code = get_authorization_code(config, auth_code)
        logger.info("Authorization Code: %s...", auth_code[:20])
        
        # Get required configuration values
        client_id = config['zoho_client_id']
        client_secret = config['zoho_client_secret']
        data_center = config.get('zoho_data_center', 'eu')
        
        logger.info("✅ Client ID: %s", client_id)
        logger.info("✅ Data Center: %s", data_center)
        
        # Exchange tokens
        token_response = exchange_tokens_request(auth_code, client_id, client_secret, data_center)
        
        # Update configuration files
        update_config_files(token_response, config, config_path)
        
        # Display results
        expires_in = token_response.get('expires_in', 3600)
        logger.info("📊 Token Exchange Results:")
        logger.info("   Access Token: %s...", token_response['access_token'][:50])
        logger.info("   Refresh Token: %s...", token_response['refresh_token'][:50])
        logger.info("   Expires In: %d seconds (%.1f hours)", expires_in, expires_in / 3600)
        
        return True
        
    except (TokenExchangeError, FileNotFoundError, ValueError) as e:
        logger.error("❌ Token exchange failed: %s", str(e))
        return False
    except Exception as e:
        logger.error("❌ Unexpected error during token exchange: %s", str(e), exc_info=True)
        return False

def test_token(access_token: str, data_center: str) -> bool:
    """
    Test the new access token by making a simple API call.
    
    Args:
        access_token: Access token to test
        data_center: Data center location
        
    Returns:
        True if token is valid, False otherwise
    """
    try:
        # Determine test URL based on data center
        domain_mapping = {
            'eu': 'https://www.zohoapis.eu',
            'com': 'https://www.zohoapis.com',
            'in': 'https://www.zohoapis.in',
            'com.au': 'https://www.zohoapis.com.au',
            'jp': 'https://www.zohoapis.jp'
        }
        
        base_domain = domain_mapping.get(data_center.lower(), f'https://www.zohoapis.{data_center}')
        test_url = f"{base_domain}/crm/v8/org"
        
        headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
        
        logger.info("🧪 Testing new access token...")
        response = requests.get(test_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            org_data = response.json()
            org_name = org_data.get('org', [{}])[0].get('company_name', 'N/A')
            logger.info("✅ Token test successful!")
            logger.info("   Connected to: %s", org_name)
            return True
        else:
            logger.error("❌ Token test failed: %d", response.status_code)
            logger.error("   Error: %s", response.text)
            return False
            
    except requests.RequestException as e:
        logger.error("❌ Network error during token test: %s", str(e))
        return False
    except Exception as e:
        logger.error("❌ Unexpected error during token test: %s", str(e))
        return False

def main():
    """Main entry point for command line usage."""
    authorization_code = None
    if len(sys.argv) > 1:
        authorization_code = sys.argv[1]
        logger.info("✅ Using authorization code from command line argument")
    
    success = exchange_authorization_code(authorization_code)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
