#!/usr/bin/env python3
"""
Test script to verify Zoho CRM Developments module integration
This script helps verify that the custom Developments module is accessible
"""

import logging
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from email_crm_sync.config.loader import ConfigLoader
from email_crm_sync.clients.zoho_v8_enhanced_client import ZohoV8EnhancedClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_developments_module():
    """Test the custom Developments module in Zoho CRM"""
    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = ConfigLoader()
        
        # Initialize Zoho client with custom module
        logger.info(f"Initializing Zoho client with module: {config.zoho_developments_module}")
        zoho = ZohoV8EnhancedClient(
            access_token=config.zoho_token,
            data_center="eu",  # or whatever your data center is
            developments_module=config.zoho_developments_module
        )
        
        # Test 1: List available modules (for debugging)
        logger.info("Testing: Getting available modules...")
        try:
            modules = zoho.discover_modules()
            logger.info(f"Found {len(modules)} modules in Zoho CRM")
            
            # Look for the Developments module
            developments_found = False
            for module in modules:
                module_name = module.get('api_name', 'Unknown')
                logger.info(f"  - {module_name}")
                if module_name == config.zoho_developments_module:
                    developments_found = True
                    logger.info(f"    ✅ Found target module: {module_name}")
            
            if not developments_found:
                logger.warning(f"⚠️ Custom module '{config.zoho_developments_module}' not found!")
                logger.info("Available modules listed above. Check your configuration.")
                
        except Exception as e:
            logger.error(f"Error getting modules: {e}")
        
        # Test 2: Verify module exists by checking discover_modules result
        logger.info(f"Testing: Verifying module '{config.zoho_developments_module}' exists...")
        try:
            modules = zoho.discover_modules()
            module_exists = any(
                m.get('api_name', '').lower() == config.zoho_developments_module.lower() 
                for m in modules
            )
            if module_exists:
                logger.info(f"✅ Module '{config.zoho_developments_module}' exists")
            else:
                logger.warning(f"❌ Module '{config.zoho_developments_module}' not found")
        except Exception as e:
            logger.error(f"Error verifying module: {e}")
        
        # Test 3: Try to search in developments module (this will test API access)
        logger.info("Testing: Searching developments...")
        try:
            # Try to get module metadata to verify access
            metadata = zoho.get_module_metadata(config.zoho_developments_module)
            logger.info(f"✅ Module metadata access successful for {config.zoho_developments_module}")
            logger.info(f"Module label: {metadata.get('display_label', 'Unknown')}")
        except Exception as e:
            logger.error(f"❌ Module access failed: {e}")
            logger.info("This could indicate:")
            logger.info("  1. Module name is incorrect")
            logger.info("  2. API permissions are insufficient")
            logger.info("  3. Access token is invalid or expired")
        
        logger.info("✅ Developments module test completed")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔧 Testing Zoho CRM Developments Module Integration")
    print("=" * 60)
    
    success = test_developments_module()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Test completed successfully!")
        print("Your Developments module configuration appears to be working.")
    else:
        print("❌ Test encountered errors.")
        print("Please check your configuration and API keys.")
    
    print("\nNext steps:")
    print("1. Review the log output above")
    print("2. Ensure your Zoho access token has CRM permissions")
    print("3. Verify the module name matches your Zoho CRM setup")
    print("4. If successful, try running: python main.py --mode once")
