#!/usr/bin/env python3
"""
Test search functionality for Zoho CRM with working methods only.
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
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

class WorkingZohoSearcher:
    """Zoho searcher using only the working search methods"""
    
    def __init__(self):
        config = load_config()
        self.access_token = config['zoho_access_token']
        data_center = config.get('zoho_data_center', 'eu')
        self.target_module = config.get('zoho_developments_module', 'Accounts')
        
        if data_center.lower() == 'eu':
            self.base_url = "https://www.zohoapis.eu/crm/v8"
        else:
            self.base_url = f"https://www.zohoapis.{data_center}/crm/v8"
        
        self.headers = {
            "Authorization": f"Zoho-oauthtoken {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def search_by_word(self, word):
        """Search using word search (this works!)"""
        try:
            response = requests.get(
                f"{self.base_url}/{self.target_module}/search",
                headers=self.headers,
                params={'word': word, 'per_page': 10},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            elif response.status_code == 204:
                return []  # No results
            else:
                print(f"Word search failed: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"Word search error: {e}")
            return []
    
    def search_by_email_parts(self, email):
        """Search for email by breaking it into searchable parts"""
        if not email:
            return []
        
        # Try searching by domain
        if '@' in email:
            domain = email.split('@')[1]
            domain_results = self.search_by_word(domain)
            if domain_results:
                return domain_results
            
            # Try searching by username part
            username = email.split('@')[0]
            username_results = self.search_by_word(username)
            if username_results:
                return username_results
        
        # Try full email as word search
        return self.search_by_word(email)
    
    def search_by_address_parts(self, address):
        """Search for address by breaking it into searchable parts"""
        if not address:
            return []
        
        # Split address into meaningful parts
        address_parts = []
        
        # Remove common words and split
        common_words = {'road', 'street', 'avenue', 'lane', 'drive', 'close', 'gardens', 'estate', 'of', 'the', 'and'}
        words = address.lower().replace(',', ' ').replace('-', ' ').split()
        
        # Extract meaningful parts
        for word in words:
            if len(word) > 2 and word not in common_words:
                address_parts.append(word.title())
        
        # Try searching with each significant part
        for part in address_parts[:3]:  # Try first 3 significant parts
            results = self.search_by_word(part)
            if results:
                return results
        
        return []
    
    def search_by_company_name_parts(self, company_name):
        """Search for company by breaking name into parts"""
        if not company_name:
            return []
        
        # Remove common business words
        common_business_words = {'ltd', 'limited', 'plc', 'llc', 'inc', 'corp', 'company', 'co', 'group', 'holdings'}
        words = company_name.lower().replace(',', ' ').replace('-', ' ').split()
        
        # Extract meaningful parts
        meaningful_words = []
        for word in words:
            if len(word) > 2 and word not in common_business_words:
                meaningful_words.append(word.title())
        
        # Try searching with each word
        for word in meaningful_words[:2]:  # Try first 2 meaningful words
            results = self.search_by_word(word)
            if results:
                return results
        
        return []
    
    def get_all_accounts(self, limit=50):
        """Get all accounts for manual matching"""
        try:
            response = requests.get(
                f"{self.base_url}/{self.target_module}",
                headers=self.headers,
                params={'fields': 'id,Account_Name,Email', 'per_page': limit},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                print(f"Failed to get accounts: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"Error getting accounts: {e}")
            return []
    
    def create_note_on_first_account(self, title, content):
        """Create a note on the first available account (fallback method)"""
        try:
            accounts = self.get_all_accounts(1)
            if accounts:
                account = accounts[0]
                account_id = account['id']
                account_name = account.get('Account_Name', 'Unknown')
                
                note_data = {
                    "data": [{
                        "Note_Title": title,
                        "Note_Content": content
                    }]
                }
                
                response = requests.post(
                    f"{self.base_url}/{self.target_module}/{account_id}/Notes",
                    headers=self.headers,
                    json=note_data,
                    timeout=30
                )
                
                if response.status_code == 201:
                    result = response.json()
                    if result.get('data') and result['data'][0].get('status') == 'success':
                        note_id = result['data'][0]['details']['id']
                        print(f"✅ Note created on fallback account: {account_name}")
                        print(f"   Note ID: {note_id}")
                        return {'success': True, 'note_id': note_id, 'account_name': account_name}
                
                print(f"❌ Note creation failed: {response.text}")
                return {'success': False, 'error': response.text}
            else:
                print("❌ No accounts available for fallback")
                return {'success': False, 'error': 'No accounts available'}
                
        except Exception as e:
            print(f"❌ Fallback note creation error: {e}")
            return {'success': False, 'error': str(e)}

def test_working_searches():
    """Test the working search methods"""
    
    print("=== TESTING WORKING SEARCH METHODS ===")
    print(f"Timestamp: {datetime.now()}")
    print()
    
    searcher = WorkingZohoSearcher()
    
    # Test 1: Word searches
    test_words = ["MORRIS", "Estate", "Road", "London"]
    
    print("1. TESTING WORD SEARCHES")
    print("-" * 30)
    
    for word in test_words:
        print(f"\nSearching for: {word}")
        results = searcher.search_by_word(word)
        print(f"   Found {len(results)} results")
        
        for i, result in enumerate(results[:2]):  # Show first 2 results
            name = result.get('Account_Name', 'No name')
            print(f"     {i+1}. {name}")
    
    # Test 2: Email search
    print(f"\n2. TESTING EMAIL SEARCH")
    print("-" * 25)
    
    test_emails = ["ben.younger@gia.uk.com", "test@knightsoflight.co.uk"]
    
    for email in test_emails:
        print(f"\nSearching for email: {email}")
        results = searcher.search_by_email_parts(email)
        print(f"   Found {len(results)} results")
        
        for i, result in enumerate(results[:2]):
            name = result.get('Account_Name', 'No name')
            print(f"     {i+1}. {name}")
    
    # Test 3: Address search
    print(f"\n3. TESTING ADDRESS SEARCH")
    print("-" * 25)
    
    test_addresses = [
        "MORRIS WALK (NORTH) ESTATE, NORTH OF PETT STREET, SE18",
        "126-140 Station Road Edgware HA8 7AA",
        "1 Emanuel Avenue, Acton"
    ]
    
    for address in test_addresses:
        print(f"\nSearching for address: {address}")
        results = searcher.search_by_address_parts(address)
        print(f"   Found {len(results)} results")
        
        for i, result in enumerate(results[:2]):
            name = result.get('Account_Name', 'No name')
            print(f"     {i+1}. {name}")
    
    # Test 4: Fallback note creation
    print(f"\n4. TESTING FALLBACK NOTE CREATION")
    print("-" * 35)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    test_title = f"Fallback Test Note - {timestamp}"
    test_content = f"""This is a test note created using the fallback method.

Created at: {datetime.now()}
Method: Attach to first available account

This ensures notes are always created even when specific account matching fails.
"""
    
    result = searcher.create_note_on_first_account(test_title, test_content)
    
    if result['success']:
        print(f"✅ Fallback method working!")
        print(f"   Account: {result['account_name']}")
        print(f"   Note ID: {result['note_id']}")
    else:
        print(f"❌ Fallback failed: {result['error']}")

if __name__ == "__main__":
    test_working_searches()
