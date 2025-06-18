#!/usr/bin/env python3
"""
Refresh Zoho OAuth2 access token using refresh token.
"""

import requests
import yaml
import json
from pathlib import Path

def load_config():
    """Load API configuration"""
    config_paths = [
        '../email_crm_sync/config/api_keys.yaml',  # From tools/ subdirectory
        '../config/api_keys.yaml',                 # From tools/ to project root config
        'config/api_keys.yaml',                    # From project root
        'email_crm_sync/config/api_keys.yaml'      # From project root to package config
    ]
    
    for path in config_paths:
        if Path(path).exists():
            with open(path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            print(f"✅ Using config: {path}")
            return config, path
    
    print("❌ Config file not found!")
    print("   Searched in:")
    for path in config_paths:
        print(f"   - {path}")
    raise FileNotFoundError("No config file found")

def refresh_zoho_token(config):
    """Refresh Zoho access token using refresh token"""
    
    refresh_token = config.get('zoho_refresh_token')
    client_id = config.get('zoho_client_id')
    client_secret = config.get('zoho_client_secret')
    data_center = config.get('zoho_data_center', 'com')
    
    if not all([refresh_token, client_id, client_secret]):
        raise ValueError("Missing required OAuth2 credentials")
    
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
    
    print(f"🔄 Refreshing Zoho OAuth2 token for data center: {data_center}")
    print(f"Using accounts URL: {accounts_url}")
    
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
                print("✅ Successfully refreshed access token!")
                print(f"New token: {new_access_token[:20]}...")
                
                return new_access_token
            else:
                print("❌ No access token in response")
                print(f"Response: {json.dumps(token_data, indent=2)}")
                return None
        else:
            print(f"❌ Failed to refresh token: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error refreshing token: {e}")
        return None

def update_config_file(config_path, new_access_token):
    """Update the config file with new access token"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        config['zoho_access_token'] = new_access_token
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        print(f"✅ Updated config file: {config_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating config file: {e}")
        return False

def main():
    try:
        config, config_path = load_config()
        print(f"📁 Using config file: {config_path}")
        
        new_token = refresh_zoho_token(config)
        
        if new_token:
            # Update both config files if they exist
            config_files = [
                'config/api_keys.yaml',
                'email_crm_sync/config/api_keys.yaml'
            ]
            
            for config_file in config_files:
                if Path(config_file).exists():
                    update_config_file(config_file, new_token)
            
            print("\n🎉 Token refresh completed successfully!")
            print("You can now run the main project again.")
        else:
            print("\n❌ Failed to refresh token. Please check your credentials.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
