#!/usr/bin/env python3
"""
Quick token test to debug the 401 errors.
"""

import requests
import yaml
import os

def test_current_token():
    """Test the current access token"""
    
    print("=== ZOHO TOKEN DEBUG TEST ===")
    
    # Load current config
    config_path = "email_crm_sync/config/api_keys.yaml"
    if not os.path.exists(config_path):
        config_path = "config/api_keys.yaml"
    
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    access_token = config['zoho_access_token']
    data_center = config.get('zoho_data_center', 'eu')
    
    print(f"Access Token: {access_token[:30]}...")
    print(f"Data Center: {data_center}")
    print(f"Expires At: {config.get('zoho_token_expires_at', 'Unknown')}")
    print()
    
    # Set up URLs
    if data_center.lower() == 'eu':
        test_url = "https://www.zohoapis.eu/crm/v8/org"
        accounts_url = "https://www.zohoapis.eu/crm/v8/Accounts"
    else:
        test_url = f"https://www.zohoapis.{data_center}/crm/v8/org"
        accounts_url = f"https://www.zohoapis.{data_center}/crm/v8/Accounts"
    
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}"
    }
    
    # Test 1: Organization info
    print("1. Testing organization endpoint...")
    try:
        response = requests.get(test_url, headers=headers, timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            org_data = response.json()
            org_name = org_data.get('org', [{}])[0].get('company_name', 'N/A')
            print(f"   ✅ Success: {org_name}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 2: Accounts access
    print("\n2. Testing accounts endpoint...")
    try:
        response = requests.get(
            accounts_url, 
            headers=headers, 
            params={'fields': 'id,Account_Name', 'per_page': 1},
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('data'):
                print(f"   ✅ Success: Found {len(data['data'])} accounts")
            else:
                print(f"   ⚠️  No account data: {data}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 3: Search endpoint
    print("\n3. Testing search endpoint...")
    try:
        search_url = f"{accounts_url}/search"
        response = requests.get(
            search_url,
            headers=headers,
            params={'criteria': '(Account_Name:*)', 'per_page': 1},
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('data'):
                print(f"   ✅ Success: Search found {len(data['data'])} results")
            else:
                print(f"   ⚠️  No search results: {data}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    test_current_token()
