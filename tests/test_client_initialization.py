#!/usr/bin/env python3
"""
Test Zoho client initialization with current config.
"""

import sys
import os
import yaml

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from email_crm_sync.clients.zoho_v8_enhanced_client import ZohoV8EnhancedClient

def test_client_init():
    """Test client initialization"""
    
    print("=== ZOHO CLIENT INITIALIZATION TEST ===")
    
    # Load config directly
    config_path = "email_crm_sync/config/api_keys.yaml"
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    print(f"Config loaded from: {config_path}")
    print(f"Access token: {config['zoho_access_token'][:30]}...")
    print(f"Data center: {config.get('zoho_data_center', 'com')}")
    print(f"Module: {config.get('zoho_developments_module', 'Developments')}")
    print()
    
    # Initialize client
    try:
        zoho_client = ZohoV8EnhancedClient(
            access_token=config['zoho_access_token'],
            data_center=config.get('zoho_data_center', 'com'),
            developments_module=config.get('zoho_developments_module', 'Developments')
        )
        print("✅ Client initialized successfully")
        
        # Test connection
        print("\nTesting connection...")
        connection_test = zoho_client.test_connection()
        print(f"Connection test result: {connection_test}")
        
        # Test a simple search
        print("\nTesting basic search...")
        try:
            results = zoho_client.search_by_email("test@example.com")
            print(f"✅ Search test completed (found {len(results)} results)")
        except Exception as e:
            print(f"⚠️  Search test failed: {e}")
        
    except Exception as e:
        print(f"❌ Client initialization failed: {e}")

if __name__ == "__main__":
    test_client_init()
