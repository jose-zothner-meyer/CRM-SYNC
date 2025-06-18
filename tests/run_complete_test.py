#!/usr/bin/env python3
"""
Email CRM Sync - Complete Setup and Test Script
This script provides a comprehensive test of your email CRM sync setup
"""

import sys
import subprocess
import logging
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'=' * 60}")
    print(f" {title}")
    print(f"{'=' * 60}")

def print_step(step, description):
    """Print a formatted step"""
    print(f"\n🔹 Step {step}: {description}")
    print("-" * 40)

def check_dependencies():
    """Check if all dependencies are installed"""
    try:
        import yaml
        import requests
        import google.oauth2.credentials
        import openai
        logger.info("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def check_configuration():
    """Check if configuration files exist and are valid"""
    config_file = Path("email_crm_sync/config/api_keys.yaml")
    
    if not config_file.exists():
        logger.error(f"❌ Configuration file not found: {config_file}")
        print("Please copy api_keys.yaml.example to api_keys.yaml and configure your API keys")
        return False
    
    try:
        from email_crm_sync.config.loader import ConfigLoader
        config = ConfigLoader()
        
        # Check required fields
        if not config.openai_key or config.openai_key == "your-openai-api-key":
            logger.error("❌ OpenAI API key not configured")
            return False
        
        if not config.zoho_token or config.zoho_token == "your-zoho-access-token":
            logger.error("❌ Zoho access token not configured")
            return False
        
        if not config.gmail_credentials or config.gmail_credentials == "credentials.json":
            logger.error("❌ Gmail credentials path not configured")
            return False
        
        logger.info("✅ Configuration appears valid")
        logger.info(f"   Using Zoho module: {config.zoho_developments_module}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Configuration error: {e}")
        return False

def test_zoho_connection():
    """Test Zoho CRM connection and module access"""
    try:
        logger.info("Testing Zoho CRM connection...")
        result = subprocess.run([sys.executable, "tools/discover_zoho_modules.py"], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            logger.info("✅ Zoho CRM connection successful")
            print(result.stdout)
            return True
        else:
            logger.error("❌ Zoho CRM connection failed")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Zoho CRM test timed out")
        return False
    except Exception as e:
        logger.error("❌ Zoho CRM test failed: %s", e)
        return False

def test_developments_module():
    """Test the specific Developments module"""
    try:
        logger.info("Testing Developments module access...")
        result = subprocess.run([sys.executable, "tests/test_developments_module.py"], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            logger.info("✅ Developments module test passed")
            print(result.stdout)
            return True
        else:
            logger.error("❌ Developments module test failed")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Developments module test timed out")
        return False
    except Exception as e:
        logger.error("❌ Developments module test failed: %s", e)
        return False

def run_email_sync_test():
    """Run a test of the email sync process"""
    try:
        logger.info("Running email sync test (once mode)...")
        result = subprocess.run([sys.executable, "main.py", "--mode", "once"], 
                              capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            logger.info("✅ Email sync test completed")
            print(result.stdout)
            return True
        else:
            logger.error("❌ Email sync test failed")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Email sync test timed out")
        return False
    except Exception as e:
        logger.error("❌ Email sync test failed: %s", e)
        return False

def main():
    """Main test routine"""
    print_header("Email CRM Sync - Complete Setup Test")
    print("This script will test your complete email CRM sync setup")
    print("including the custom Zoho 'Developments' module integration.")
    
    # Test results tracking
    tests_passed = 0
    total_tests = 5
    
    # Step 1: Check dependencies
    print_step(1, "Checking Dependencies")
    if check_dependencies():
        tests_passed += 1
    
    # Step 2: Check configuration
    print_step(2, "Validating Configuration")
    if check_configuration():
        tests_passed += 1
    
    # Step 3: Test Zoho connection
    print_step(3, "Testing Zoho CRM Connection")
    if test_zoho_connection():
        tests_passed += 1
    
    # Step 4: Test Developments module
    print_step(4, "Testing Developments Module")
    if test_developments_module():
        tests_passed += 1
    
    # Step 5: Test email sync
    print_step(5, "Testing Email Sync Process")
    if run_email_sync_test():
        tests_passed += 1
    
    # Summary
    print_header("Test Results Summary")
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Your email CRM sync is ready to use.")
        print("\nNext steps:")
        print("1. Star some emails in Gmail that you want to process")
        print("2. Run: python main.py --mode once")
        print("3. For continuous monitoring: python main.py --mode monitor")
    else:
        print("❌ Some tests failed. Please review the output above and fix any issues.")
        print("\nCommon issues:")
        print("1. API keys not configured correctly")
        print("2. Zoho module name doesn't match your CRM setup")
        print("3. Gmail OAuth credentials not set up")
        print("4. Network connectivity issues")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
