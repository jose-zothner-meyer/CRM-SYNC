#!/usr/bin/env python3
"""
Enhanced Zoho Module Discovery Tool

This tool discovers available Zoho CRM modules and tests access permissions.
Integrated with the unified CRM-SYNC system with improved error handling.

Usage:
    python discover_zoho_modules.py
    
    # From main CLI (recommended)
    python main.py discover-modules

This tool is primarily intended for internal use and diagnostics.
The main CLI provides a more user-friendly interface for module discovery.
"""

import requests
import yaml
import json
import sys
from pathlib import Path
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from email_crm_sync.config import config
except ImportError:
    config = None


class ModuleDiscoveryError(Exception):
    """Custom exception for module discovery errors"""

def load_config() -> Dict[str, Any]:
    """
    Load API configuration using the centralized config or fallback to YAML.
    
    Returns:
        Configuration dictionary
        
    Raises:
        ModuleDiscoveryError: If configuration cannot be loaded
        FileNotFoundError: If no config file is found
    """
    if config:
        try:
            # Convert the config attributes to a dictionary
            config_dict = {
                'zoho_access_token': config.zoho_token,
                'zoho_data_center': config.zoho_data_center,
                'zoho_base_url': getattr(config, 'zoho_base_url', 'https://www.zohoapis.com/crm/v8'),
                'zoho_developments_module': getattr(config, 'zoho_developments_module', 'Accounts')
            }
            
            # Validate required fields
            if not config_dict.get('zoho_access_token'):
                raise ModuleDiscoveryError("Missing zoho_access_token in centralized config")
                
            logger.info("✅ Using centralized configuration")
            return config_dict
        except AttributeError as e:
            logger.warning("⚠️ Could not load from centralized config: %s", e)
        except ImportError as e:
            logger.warning("⚠️ Unexpected error loading centralized config: %s", e)
    
    # Fallback to YAML loading
    config_paths = [
        '../config/api_keys.yaml',
        '../email_crm_sync/config/api_keys.yaml',
        'config/api_keys.yaml',
        'email_crm_sync/config/api_keys.yaml'
    ]
    
    for path in config_paths:
        config_file = Path(path)
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                
                if not isinstance(config_data, dict):
                    logger.warning("Config file %s does not contain a valid dictionary", path)
                    continue
                
                if not config_data.get('zoho_access_token'):
                    logger.warning("Config file %s missing zoho_access_token", path)
                    continue
                
                logger.info("✅ Using config file: %s", path)
                return config_data
            except yaml.YAMLError as e:
                logger.warning("Invalid YAML in %s: %s", path, e)
                continue
            except IOError as e:
                logger.warning("Error reading %s: %s", path, e)
                continue
    
    raise FileNotFoundError("No valid config file found with zoho_access_token")

def discover_modules(config_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Discover available Zoho CRM modules.
    
    Args:
        config_data: Configuration dictionary containing API credentials
        
    Returns:
        List of module information dictionaries
        
    Raises:
        ModuleDiscoveryError: If modules cannot be discovered
        requests.RequestException: If HTTP request fails
    """
    # Build the correct base URL based on data center
    data_center = config_data.get('zoho_data_center', 'com')
    if data_center == 'eu':
        base_url = 'https://www.zohoapis.eu/crm/v8'
    elif data_center == 'in':
        base_url = 'https://www.zohoapis.in/crm/v8'
    elif data_center == 'com.au':
        base_url = 'https://www.zohoapis.com.au/crm/v8'
    else:
        base_url = 'https://www.zohoapis.com/crm/v8'
    
    access_token = config_data['zoho_access_token']
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    logger.info("🔍 Discovering Zoho CRM Modules...")
    logger.info("=" * 50)
    
    try:
        # Get all modules
        response = requests.get(f"{base_url}/settings/modules", headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            modules = data.get('modules', [])
            
            logger.info("✅ Found %d modules:", len(modules))
            logger.info("")
            
            for module in modules:
                api_name = module.get('api_name', 'N/A')
                display_label = module.get('display_label', 'N/A')
                module_name = module.get('module_name', 'N/A')
                is_custom = module.get('generated_type', 'default') == 'custom'
                
                logger.info("📋 %s", display_label)
                logger.info("   API Name: %s", api_name)
                logger.info("   Module Name: %s", module_name)
                logger.info("   Custom: %s", 'Yes' if is_custom else 'No')
                logger.info("")
                
            return modules
        else:
            error_msg = f"Failed to get modules: {response.status_code}"
            logger.error("❌ %s", error_msg)
            logger.error("Response: %s", response.text)
            raise ModuleDiscoveryError(error_msg)
            
    except requests.RequestException as e:
        logger.error("❌ Network error discovering modules: %s", e)
        raise
    except json.JSONDecodeError as e:
        logger.error("❌ Invalid JSON response: %s", e)
        raise ModuleDiscoveryError(f"Invalid JSON response: {e}") from e

def check_module_access(config_data: Dict[str, Any], module_name: str) -> bool:
    """
    Check if we can access a specific module.
    
    Args:
        config_data: Configuration dictionary containing API credentials
        module_name: Name of the module to test
        
    Returns:
        True if module is accessible, False otherwise
    """
    # Build the correct base URL based on data center
    data_center = config_data.get('zoho_data_center', 'com')
    if data_center == 'eu':
        base_url = 'https://www.zohoapis.eu/crm/v8'
    elif data_center == 'in':
        base_url = 'https://www.zohoapis.in/crm/v8'
    elif data_center == 'com.au':
        base_url = 'https://www.zohoapis.com.au/crm/v8'
    else:
        base_url = 'https://www.zohoapis.com/crm/v8'
        
    access_token = config_data['zoho_access_token']
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    logger.info("\n🔍 Testing access to '%s' module...", module_name)
    
    try:
        # Try to get records from the module with required fields parameter
        params = {'per_page': 1, 'fields': 'id,Created_Time'}
        response = requests.get(f"{base_url}/{module_name}", headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            count = len(data.get('data', []))
            logger.info("✅ Can access '%s' - Found %d sample records", module_name, count)
            return True
        else:
            logger.warning("❌ Cannot access '%s': %d", module_name, response.status_code)
            logger.warning("Response: %s", response.text)
            return False
            
    except requests.RequestException as e:
        logger.error("❌ Network error checking module access: %s", e)
        return False
    except json.JSONDecodeError as e:
        logger.error("❌ Invalid JSON response checking module: %s", e)
        return False

def main():
    """
    Main function to discover Zoho modules and test access.
    
    This tool is primarily intended for internal use and diagnostics.
    The main CLI provides a more user-friendly interface via:
    python main.py discover-modules
    """
    try:
        logger.info("🔍 Starting Zoho module discovery...")
        
        # Load configuration
        config_data = load_config()
        data_center = config_data.get('zoho_data_center', 'com')
        base_url = config_data.get('zoho_base_url', f'https://www.zohoapis.{data_center}/crm/v8')
        
        logger.info("Using Zoho Data Center: %s", data_center)
        logger.info("Using Zoho Base URL: %s", base_url)
        logger.info("")
        
        # Discover all modules
        modules = discover_modules(config_data)
        
        if modules:
            # Test access to common module names
            test_modules = ['Developments', 'Deals', 'Contacts', 'Accounts', 'Leads']
            
            logger.info("")
            logger.info("=" * 50)
            logger.info("🧪 Testing Module Access...")
            logger.info("=" * 50)
            
            accessible_modules = []
            for module_name in test_modules:
                if check_module_access(config_data, module_name):
                    accessible_modules.append(module_name)
            
            logger.info("\n📊 Summary:")
            logger.info("Total modules discovered: %d", len(modules))
            logger.info("Tested modules: %d", len(test_modules))
            logger.info("Accessible modules: %d (%s)", len(accessible_modules), ', '.join(accessible_modules))
        
    except ModuleDiscoveryError as e:
        logger.error("❌ Module discovery error: %s", e)
        sys.exit(1)
    except FileNotFoundError as e:
        logger.error("❌ Configuration error: %s", e)
        sys.exit(1)
    except requests.RequestException as e:
        logger.error("❌ Network error: %s", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
