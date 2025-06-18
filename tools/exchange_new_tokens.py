#!/usr/bin/env python3
"""
Exchange Zoho authorization code for access and refresh tokens.

SECURITY NOTE: This script has been updated to remove hard-coded authorization codes.
Authorization codes should be provided in one of these ways (in order of preference):
1. Command line argument: python exchange_new_tokens.py "your_auth_code_here"
2. Environment variable: export ZOHO_AUTH_CODE="your_auth_code_here"
3. Configuration file: Add to zoho_authorization_code in api_keys.yaml

The authorization code will be automatically cleared from the config file after successful use.

Usage:
    python exchange_new_tokens.py [authorization_code]

Example:
    python exchange_new_tokens.py "1000.abcd1234.efgh5678"
"""

import requests
import yaml
import os
import sys
from datetime import datetime, timedelta

def exchange_authorization_code(auth_code=None):
    """Exchange authorization code for tokens"""
    
    print("=== ZOHO OAUTH TOKEN EXCHANGE ===")
    
    # Load current config to get client credentials - try multiple possible paths
    config_paths = [
        "../email_crm_sync/config/api_keys.yaml",  # From tools/ subdirectory
        "../config/api_keys.yaml",                 # From tools/ to project root config
        "config/api_keys.yaml",                    # From project root
        "email_crm_sync/config/api_keys.yaml"      # From project root to package config
    ]
    
    config_path = None
    for path in config_paths:
        if os.path.exists(path):
            config_path = path
            break
    
    if not config_path:
        print("❌ Config file not found!")
        print("   Searched in:")
        for path in config_paths:
            print(f"   - {path}")
        return
    
    print(f"✅ Using config: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    
    # Get authorization code from parameter, config file, or prompt user
    if not auth_code:
        auth_code = config.get('zoho_authorization_code', '')
        
    if not auth_code or auth_code.strip() == "":
        print("❌ No authorization code provided!")
        print("   Please either:")
        print("   1. Add the authorization code to 'zoho_authorization_code' in your api_keys.yaml file")
        print("   2. Pass it as a command line argument")
        print("   3. Set it as an environment variable ZOHO_AUTH_CODE")
        
        # Try environment variable as fallback
        auth_code = os.environ.get('ZOHO_AUTH_CODE', '')
        if not auth_code:
            return
        else:
            print("✅ Using authorization code from environment variable")
    
    print(f"Authorization Code: {auth_code[:20]}...")
    print()
    
    client_id = config.get('zoho_client_id')
    client_secret = config.get('zoho_client_secret')
    data_center = config.get('zoho_data_center', 'eu')
    
    if not client_id or not client_secret:
        print("❌ Client ID or Secret missing from config!")
        return
    
    print(f"✅ Using Client ID: {client_id}")
    print(f"✅ Data Center: {data_center}")
    print()
    
    # Determine token URL based on data center
    if data_center.lower() == 'eu':
        token_url = "https://accounts.zoho.eu/oauth/v2/token"
    else:
        token_url = f"https://accounts.zoho.{data_center}/oauth/v2/token"
    
    # Prepare token exchange request
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'code': auth_code
    }
    
    print("🔄 Exchanging authorization code for tokens...")
    
    try:
        response = requests.post(token_url, data=token_data, timeout=30)
        
        if response.status_code == 200:
            token_response = response.json()
            
            access_token = token_response.get('access_token')
            refresh_token = token_response.get('refresh_token')
            expires_in = token_response.get('expires_in', 3600)
            
            if access_token and refresh_token:
                print("✅ Token exchange successful!")
                print(f"   Access Token: {access_token[:20]}...")
                print(f"   Refresh Token: {refresh_token[:20]}...")
                print(f"   Expires in: {expires_in} seconds")
                print()
                
                # Calculate expiration time
                expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                # Update config file
                config['zoho_access_token'] = access_token
                config['zoho_refresh_token'] = refresh_token
                config['zoho_token_expires_at'] = expires_at.isoformat()
                
                # Write updated config
                with open(config_path, 'w', encoding='utf-8') as file:
                    yaml.dump(config, file, default_flow_style=False, sort_keys=False)
                
                # Clear the authorization code from config for security
                if 'zoho_authorization_code' in config:
                    config['zoho_authorization_code'] = ""
                    with open(config_path, 'w', encoding='utf-8') as file:
                        yaml.dump(config, file, default_flow_style=False, sort_keys=False)
                    print("🔒 Authorization code cleared from config file for security")
                
                print(f"✅ Config updated in: {config_path}")
                print(f"   Token expires at: {expires_at}")
                
                # Test the new token
                print("\n🧪 Testing new access token...")
                test_token(access_token, data_center)
                
            else:
                print("❌ No tokens received in response!")
                print(f"Response: {token_response}")
        else:
            print(f"❌ Token exchange failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except (requests.RequestException, requests.ConnectionError, requests.Timeout) as e:
        print(f"❌ Network error during token exchange: {e}")
    except Exception as e:
        print(f"❌ Unexpected error during token exchange: {e}")

def test_token(access_token, data_center):
    """Test the new access token"""
    try:
        if data_center.lower() == 'eu':
            test_url = "https://www.zohoapis.eu/crm/v8/org"
        else:
            test_url = f"https://www.zohoapis.{data_center}/crm/v8/org"
        
        headers = {
            "Authorization": f"Zoho-oauthtoken {access_token}"
        }
        
        response = requests.get(test_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            org_data = response.json()
            org_name = org_data.get('org', [{}])[0].get('company_name', 'N/A')
            print("✅ Token test successful!")
            print(f"   Connected to: {org_name}")
        else:
            print(f"❌ Token test failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except (requests.RequestException, requests.ConnectionError, requests.Timeout) as e:
        print(f"❌ Network error during token test: {e}")
    except Exception as e:
        print(f"❌ Unexpected error during token test: {e}")

if __name__ == "__main__":
    # Get the authorization code from command line argument
    authorization_code = None
    if len(sys.argv) > 1:
        authorization_code = sys.argv[1]
        print("✅ Using authorization code from command line argument")
    
    exchange_authorization_code(authorization_code)
