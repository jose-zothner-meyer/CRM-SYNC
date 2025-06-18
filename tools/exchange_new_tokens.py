#!/usr/bin/env python3
"""
Exchange Zoho authorization code for access and refresh tokens.
"""

import requests
import yaml
import os
from datetime import datetime, timedelta

def exchange_authorization_code(auth_code):
    """Exchange authorization code for tokens"""
    
    print("=== ZOHO OAUTH TOKEN EXCHANGE ===")
    print(f"Authorization Code: {auth_code}")
    print()
    
    # Load current config to get client credentials
    config_path = "../email_crm_sync/config/api_keys.yaml"
    if not os.path.exists(config_path):
        config_path = "config/api_keys.yaml"
    
    if not os.path.exists(config_path):
        print("❌ Config file not found!")
        return
    
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
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
                with open(config_path, 'w') as file:
                    yaml.dump(config, file, default_flow_style=False, sort_keys=False)
                
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
            
    except Exception as e:
        print(f"❌ Token exchange error: {e}")

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
            print(f"✅ Token test successful!")
            print(f"   Connected to: {org_name}")
        else:
            print(f"❌ Token test failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Token test error: {e}")

if __name__ == "__main__":
    # Get the authorization code from command line argument or hardcode it
    auth_code = "1000.33f700b9654faf71f9fc0ef65380c979.254f15c0df27648311eabe69052eaad6"
    exchange_authorization_code(auth_code)
