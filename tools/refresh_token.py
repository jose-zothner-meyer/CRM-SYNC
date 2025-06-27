#!/usr/bin/env python3
"""
Enhanced Zoho Token Refresh Tool

This tool refreshes Zoho OAuth2 access tokens using refresh tokens.
Integrated with the unified CRM-SYNC system with improved error handling.

SECURITY: Tokens are handled securely and configuration files are validated.

Usage:
    python refresh_token.py
    
    # From main CLI (recommended)
    python main.py token refresh

This tool is primarily intended for internal use. The main CLI provides
a more user-friendly interface for token management operations.
"""

import requests
import yaml
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TokenRefreshError(Exception):
    """Custom exception for token refresh errors"""


def load_config() -> Tuple[Dict[str, Any], str]:
    """
    Load API configuration from multiple possible locations.
    
    Returns:
        Tuple of (config_dict, config_path)
        
    Raises:
        FileNotFoundError: If no config file is found
        yaml.YAMLError: If config file is invalid
    """
    config_paths = [
        '../email_crm_sync/config/api_keys.yaml',  # From tools/ subdirectory
        '../config/api_keys.yaml',                 # From tools/ to project root config
        'config/api_keys.yaml',                    # From project root
        'email_crm_sync/config/api_keys.yaml'      # From project root to package config
    ]
    
    for path in config_paths:
        config_file = Path(path)
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                
                if not isinstance(config, dict):
                    logger.warning("Config file %s does not contain a valid dictionary", path)
                    continue
                    
                logger.info("✅ Using config: %s", path)
                return config, str(config_file.resolve())
            except yaml.YAMLError as e:
                logger.warning("Invalid YAML in %s: %s", path, e)
                continue
            except IOError as e:
                logger.warning("Error reading %s: %s", path, e)
                continue
    
    logger.error("❌ Config file not found!")
    logger.error("   Searched in:")
    for path in config_paths:
        logger.error("   - %s", path)
    raise FileNotFoundError("No valid config file found")


def refresh_zoho_token(config: Dict[str, Any]) -> str:
    """
    Refresh Zoho access token using refresh token.
    
    Args:
        config: Configuration dictionary containing OAuth credentials
        
    Returns:
        New access token if successful
        
    Raises:
        TokenRefreshError: If required credentials are missing or refresh fails
        requests.RequestException: If the HTTP request fails
    """
    
    refresh_token = config.get('zoho_refresh_token')
    client_id = config.get('zoho_client_id')
    client_secret = config.get('zoho_client_secret')
    data_center = config.get('zoho_data_center', 'com')
    
    if not all([refresh_token, client_id, client_secret]):
        missing = []
        if not refresh_token:
            missing.append('zoho_refresh_token')
        if not client_id:
            missing.append('zoho_client_id')
        if not client_secret:
            missing.append('zoho_client_secret')
        raise TokenRefreshError(f"Missing required OAuth2 credentials: {', '.join(missing)}")
    
    # Determine the correct accounts domain for the data center
    accounts_domains = {
        'com': 'https://accounts.zoho.com',
        'eu': 'https://accounts.zoho.eu',
        'in': 'https://accounts.zoho.in',
        'com.au': 'https://accounts.zoho.com.au',
        'jp': 'https://accounts.zoho.jp'
    }
    
    accounts_url = accounts_domains.get(data_center, 'https://accounts.zoho.com')
    token_url = f"{accounts_url}/oauth/v2/token"
    
    logger.info("🔄 Refreshing Zoho OAuth2 token for data center: %s", data_center)
    logger.info("Using accounts URL: %s", accounts_url)
    
    # Prepare the refresh request
    data = {
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'refresh_token'
    }
    
    try:
        response = requests.post(token_url, data=data, timeout=30)
        
        if response.status_code == 200:
            token_data = response.json()
            
            new_access_token = token_data.get('access_token')
            if new_access_token:
                logger.info("✅ Successfully refreshed access token!")
                logger.info("New token: %s...", new_access_token[:20])
                return new_access_token
            else:
                logger.error("❌ No access token in response")
                logger.error("Response: %s", json.dumps(token_data, indent=2))
                raise TokenRefreshError("No access token in response")
        else:
            logger.error("❌ Failed to refresh token: %d", response.status_code)
            logger.error("Response: %s", response.text)
            raise TokenRefreshError(f"Failed to refresh token: {response.status_code}")
            
    except requests.RequestException as e:
        logger.error("❌ Network error refreshing token: %s", e)
        raise
    except json.JSONDecodeError as e:
        logger.error("❌ Invalid JSON response: %s", e)
        raise TokenRefreshError(f"Invalid JSON response: {e}") from e


def update_config_file(config_path: str, new_access_token: str) -> bool:
    """
    Update the config file with new access token.
    
    Args:
        config_path: Path to the configuration file
        new_access_token: New access token to write
        
    Returns:
        True if successful, False otherwise
    """
    try:
        config_file = Path(config_path)
        
        # Read current config
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if not isinstance(config, dict):
            logger.error("Config file %s does not contain a valid dictionary", config_path)
            return False
        
        # Update token and add timestamp
        config['zoho_access_token'] = new_access_token
        config['token_updated_at'] = datetime.now().isoformat()
        
        # Write updated config
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        logger.info("✅ Updated config file: %s", config_path)
        return True
        
    except yaml.YAMLError as e:
        logger.error("❌ YAML error updating config file: %s", e)
        return False
    except PermissionError as e:
        logger.error("❌ Permission error updating config file: %s", e)
        return False
    except IOError as e:
        logger.error("❌ IO error updating config file: %s", e)
        return False


def main():
    """
    Main function to refresh Zoho tokens and update configuration files.
    
    This tool is primarily intended for internal use. The main CLI provides
    a more user-friendly interface via: python main.py token refresh
    """
    try:
        logger.info("🔄 Starting Zoho token refresh process...")
        
        # Load configuration
        config, config_path = load_config()
        logger.info("📁 Using config file: %s", config_path)
        
        # Refresh the token
        new_token = refresh_zoho_token(config)
        
        # Update both config files if they exist
        config_files = [
            'config/api_keys.yaml',
            'email_crm_sync/config/api_keys.yaml'
        ]
        
        updated_files = []
        for config_file in config_files:
            if Path(config_file).exists():
                if update_config_file(config_file, new_token):
                    updated_files.append(config_file)
        
        if updated_files:
            logger.info("\n🎉 Token refresh completed successfully!")
            logger.info("Updated %d config file(s): %s", len(updated_files), ', '.join(updated_files))
            logger.info("You can now run the main project again.")
        else:
            logger.warning("⚠️ Token refreshed but no config files were updated")
        
    except TokenRefreshError as e:
        logger.error("❌ Token refresh error: %s", e)
        sys.exit(1)
    except FileNotFoundError as e:
        logger.error("❌ Configuration error: %s", e)
        sys.exit(1)
    except requests.RequestException as e:
        logger.error("❌ Network error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
