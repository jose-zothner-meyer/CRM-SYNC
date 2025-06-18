#!/usr/bin/env python3
"""
Test the Zoho access token directly
"""

import requests
import yaml

def test_zoho_token():
    """Test if the Zoho access token is valid"""
    
    # Load the token from config
    with open('../email_crm_sync/config/api_keys.yaml', 'r') as file:
        config = yaml.safe_load(file)
    
    access_token = config['zoho_access_token']
    data_center = config.get('zoho_data_center', 'eu')
    
    print(f"Testing token: {access_token[:20]}...")
    print(f"Data center: {data_center}")
    
    # Determine the correct base URL
    if data_center.lower() == 'eu':
        base_url = "https://www.zohoapis.eu/crm/v8"
    else:
        base_url = f"https://www.zohoapis.{data_center}/crm/v8"
    
    print(f"Base URL: {base_url}")
    
    # Test with a simple API call to get user info
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test 1: Get user info
        print("\n1. Testing user info...")
        response = requests.get(f"{base_url}/users?type=ActiveUsers", headers=headers, timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            users = data.get('users', [])
            print(f"   Found {len(users)} users")
            if users:
                print(f"   First user: {users[0].get('full_name', 'Unknown')}")
            print("   ✅ User info test PASSED")
        else:
            print(f"   ❌ User info test FAILED: {response.text}")
            return False
        
        # Test 2: Get modules
        print("\n2. Testing modules...")
        response = requests.get(f"{base_url}/settings/modules", headers=headers, timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            modules = data.get('modules', [])
            print(f"   Found {len(modules)} modules")
            for module in modules[:5]:  # Show first 5
                print(f"     - {module.get('module_name', 'Unknown')}")
            print("   ✅ Modules test PASSED")
        else:
            print(f"   ❌ Modules test FAILED: {response.text}")
        
        # Test 3: Get accounts (the target module)
        print("\n3. Testing Accounts module...")
        response = requests.get(f"{base_url}/Accounts", headers=headers, params={'per_page': 5}, timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            accounts = data.get('data', [])
            print(f"   Found {len(accounts)} accounts")
            for account in accounts:
                name = account.get('Account_Name', 'Unknown')
                print(f"     - {name}")
            print("   ✅ Accounts test PASSED")
        else:
            print(f"   ❌ Accounts test FAILED: {response.text}")
        
        # Test 4: Word search
        print("\n4. Testing word search...")
        response = requests.get(
            f"{base_url}/Accounts/search", 
            headers=headers, 
            params={'word': 'London', 'per_page': 3}, 
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            results = data.get('data', [])
            print(f"   Found {len(results)} results for 'London'")
            for result in results:
                name = result.get('Account_Name', 'Unknown')
                print(f"     - {name}")
            print("   ✅ Word search test PASSED")
        elif response.status_code == 204:
            print("   ⚠️ Word search test: No results found (204)")
        else:
            print(f"   ❌ Word search test FAILED: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    test_zoho_token()
