#!/usr/bin/env python3
"""
Diagnose Zoho CRM search issues and test various search methods.
"""

import sys
import os
import yaml
import requests
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def load_config():
    """Load configuration from YAML file"""
    config_path = "email_crm_sync/config/api_keys.yaml"
    with open(config_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def test_search_methods():
    """Test different search methods to identify issues"""
    
    print("=== ZOHO CRM SEARCH DIAGNOSTICS ===")
    print(f"Timestamp: {datetime.now()}")
    print()
    
    config = load_config()
    access_token = config['zoho_access_token']
    data_center = config.get('zoho_data_center', 'eu')
    target_module = config.get('zoho_developments_module', 'Accounts')
    
    if data_center.lower() == 'eu':
        base_url = "https://www.zohoapis.eu/crm/v8"
    else:
        base_url = f"https://www.zohoapis.{data_center}/crm/v8"
    
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json"
    }
    
    print(f"Base URL: {base_url}")
    print(f"Target Module: {target_module}")
    print()
    
    # Test 1: Basic record retrieval
    print("1. TESTING BASIC RECORD RETRIEVAL")
    print("-" * 40)
    
    try:
        response = requests.get(
            f"{base_url}/{target_module}",
            headers=headers,
            params={'fields': 'id,Account_Name,Email', 'per_page': 3},
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('data'):
                records = data['data']
                print(f"   ✅ Found {len(records)} records")
                for i, record in enumerate(records):
                    name = record.get('Account_Name', f"Record-{record['id'][:8]}")
                    email = record.get('Email', 'No email')
                    print(f"     {i+1}. {name} - {email}")
                
                # Store first record for testing
                test_record = records[0]
                test_record_name = test_record.get('Account_Name', 'Unknown')
                test_record_email = test_record.get('Email')
                
            else:
                print(f"   ❌ No records found: {data}")
                return
        else:
            print(f"   ❌ Failed: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 2: COQL queries
    print(f"\n2. TESTING COQL QUERIES")
    print("-" * 30)
    
    coql_queries = [
        ("Simple SELECT", f"SELECT id, Account_Name FROM {target_module} LIMIT 1"),
        ("Notes search", "SELECT id, Note_Title FROM Notes LIMIT 1"),
        ("Email search", f"SELECT id, Account_Name FROM {target_module} WHERE Email = 'test@example.com' LIMIT 1"),
    ]
    
    for query_name, query in coql_queries:
        print(f"\n   Testing: {query_name}")
        print(f"   Query: {query}")
        
        try:
            response = requests.post(
                f"{base_url}/coql",
                headers=headers,
                json={"select_query": query},
                timeout=30
            )
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if data.get('data'):
                    print(f"   ✅ Success: Found {len(data['data'])} records")
                else:
                    print(f"   ℹ️  No results: {data}")
            elif response.status_code == 204:
                print(f"   ℹ️  No content (empty result)")
            else:
                print(f"   ❌ Failed: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test 3: Search API
    print(f"\n3. TESTING SEARCH API")
    print("-" * 25)
    
    search_tests = [
        ("Basic criteria", f"(Account_Name:*{test_record_name.split()[0] if test_record_name != 'Unknown' else 'MORRIS'}*)"),
        ("Email search", f"(Email:{test_record_email})" if test_record_email else "(Email:*test*)"),
        ("Simple name", f"(Account_Name:*MORRIS*)"),
    ]
    
    for search_name, criteria in search_tests:
        print(f"\n   Testing: {search_name}")
        print(f"   Criteria: {criteria}")
        
        try:
            response = requests.get(
                f"{base_url}/{target_module}/search",
                headers=headers,
                params={'criteria': criteria, 'per_page': 1},
                timeout=30
            )
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if data.get('data'):
                    print(f"   ✅ Success: Found {len(data['data'])} records")
                    record = data['data'][0]
                    name = record.get('Account_Name', 'No name')
                    print(f"     Result: {name}")
                else:
                    print(f"   ℹ️  No results: {data}")
            elif response.status_code == 204:
                print(f"   ℹ️  No content (empty result)")
            else:
                print(f"   ❌ Failed: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test 4: Word search
    print(f"\n4. TESTING WORD SEARCH")
    print("-" * 25)
    
    word_tests = [
        "MORRIS",
        "Estate",
        test_record_name.split()[0] if test_record_name != 'Unknown' else "MORRIS"
    ]
    
    for word in word_tests:
        print(f"\n   Testing word: {word}")
        
        try:
            response = requests.get(
                f"{base_url}/{target_module}/search",
                headers=headers,
                params={'word': word, 'per_page': 1},
                timeout=30
            )
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if data.get('data'):
                    print(f"   ✅ Success: Found {len(data['data'])} records")
                else:
                    print(f"   ℹ️  No results: {data}")
            elif response.status_code == 204:
                print(f"   ℹ️  No content (empty result)")
            else:
                print(f"   ❌ Failed: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test 5: Field metadata
    print(f"\n5. TESTING FIELD METADATA")
    print("-" * 30)
    
    try:
        response = requests.get(
            f"{base_url}/settings/fields",
            headers=headers,
            params={'module': target_module},
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('fields'):
                fields = data['fields']
                print(f"   ✅ Found {len(fields)} fields")
                
                # Look for searchable fields
                searchable_fields = [f for f in fields if f.get('searchable')]
                print(f"   Searchable fields: {len(searchable_fields)}")
                
                # Show key fields
                key_fields = ['Account_Name', 'Email', 'Property_Address', 'Address', 'Deal_Name']
                found_fields = []
                for field in fields:
                    api_name = field.get('api_name', '')
                    if api_name in key_fields:
                        found_fields.append(api_name)
                        print(f"     - {api_name}: {field.get('data_type')} (searchable: {field.get('searchable', False)})")
                
                missing_fields = set(key_fields) - set(found_fields)
                if missing_fields:
                    print(f"   Missing expected fields: {list(missing_fields)}")
            else:
                print(f"   ❌ No fields data: {data}")
        else:
            print(f"   ❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n6. RECOMMENDATIONS")
    print("=" * 50)
    print("Based on the test results:")
    print("1. If basic retrieval works but search fails → Check search syntax")
    print("2. If COQL fails → May need additional scopes or COQL might be restricted")
    print("3. If criteria search fails → Try simpler criteria patterns")
    print("4. If word search works → Use word search instead of criteria")
    print("5. Check field metadata to ensure you're searching the right fields")

if __name__ == "__main__":
    test_search_methods()
