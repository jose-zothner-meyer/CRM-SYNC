#!/usr/bin/env python3
"""
Discover available Zoho CRM modules and their details.
"""

import requests
import yaml
import json
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from email_crm_sync.config.loader import ConfigLoader
except ImportError:
    ConfigLoader = None

def load_config():
    """Load API configuration using the main config loader"""
    if ConfigLoader:
        try:
            config_loader = ConfigLoader()
            # Convert the config loader attributes to a dictionary
            config = {
                'zoho_access_token': config_loader.zoho_token,
                'zoho_data_center': config_loader.zoho_data_center,
                'zoho_base_url': getattr(config_loader, 'zoho_base_url', 'https://www.zohoapis.com/crm/v8'),
                'zoho_developments_module': getattr(config_loader, 'zoho_developments_module', 'Accounts')
            }
            return config
        except Exception as e:
            print(f"⚠️ Could not load from main config loader: {e}")
    
    # Fallback to YAML loading
    config_paths = [
        '../config/api_keys.yaml',
        '../email_crm_sync/config/api_keys.yaml'
    ]
    
    for path in config_paths:
        if Path(path).exists():
            with open(path, 'r') as f:
                return yaml.safe_load(f)
    
    raise FileNotFoundError("No config file found")

def discover_modules(config):
    """Discover available Zoho CRM modules"""
    # Build the correct base URL based on data center
    data_center = config.get('zoho_data_center', 'com')
    if data_center == 'eu':
        base_url = 'https://www.zohoapis.eu/crm/v8'
    elif data_center == 'in':
        base_url = 'https://www.zohoapis.in/crm/v8'
    elif data_center == 'com.au':
        base_url = 'https://www.zohoapis.com.au/crm/v8'
    else:
        base_url = 'https://www.zohoapis.com/crm/v8'
    
    access_token = config['zoho_access_token']
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    print("🔍 Discovering Zoho CRM Modules...")
    print("=" * 50)
    
    try:
        # Get all modules
        response = requests.get(f"{base_url}/settings/modules", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            modules = data.get('modules', [])
            
            print(f"✅ Found {len(modules)} modules:")
            print()
            
            for module in modules:
                api_name = module.get('api_name', 'N/A')
                display_label = module.get('display_label', 'N/A')
                module_name = module.get('module_name', 'N/A')
                is_custom = module.get('generated_type', 'default') == 'custom'
                
                print(f"📋 {display_label}")
                print(f"   API Name: {api_name}")
                print(f"   Module Name: {module_name}")
                print(f"   Custom: {'Yes' if is_custom else 'No'}")
                print()
                
            return modules
        else:
            print(f"❌ Failed to get modules: {response.status_code}")
            print(f"Response: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Error discovering modules: {e}")
        return []

def check_module_access(config, module_name):
    """Check if we can access a specific module"""
    # Build the correct base URL based on data center
    data_center = config.get('zoho_data_center', 'com')
    if data_center == 'eu':
        base_url = 'https://www.zohoapis.eu/crm/v8'
    elif data_center == 'in':
        base_url = 'https://www.zohoapis.in/crm/v8'
    elif data_center == 'com.au':
        base_url = 'https://www.zohoapis.com.au/crm/v8'
    else:
        base_url = 'https://www.zohoapis.com/crm/v8'
        
    access_token = config['zoho_access_token']
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    print(f"\n🔍 Testing access to '{module_name}' module...")
    
    try:
        # Try to get records from the module with required fields parameter
        params = {'per_page': 1, 'fields': 'id,Created_Time'}
        response = requests.get(f"{base_url}/{module_name}", headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            count = len(data.get('data', []))
            print(f"✅ Can access '{module_name}' - Found {count} sample records")
            return True
        else:
            print(f"❌ Cannot access '{module_name}': {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking module access: {e}")
        return False

def main():
    try:
        config = load_config()
        print(f"Using Zoho Data Center: {config.get('zoho_data_center', 'com')}")
        print(f"Using Zoho Base URL: {config.get('zoho_base_url')}")
        print()
        
        # Discover all modules
        modules = discover_modules(config)
        
        if modules:
            # Test access to common module names
            test_modules = ['Developments', 'Deals', 'Contacts', 'Accounts', 'Leads']
            
            print("\n" + "=" * 50)
            print("🧪 Testing Module Access...")
            print("=" * 50)
            
            for module_name in test_modules:
                check_module_access(config, module_name)
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
