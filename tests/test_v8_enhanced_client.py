#!/usr/bin/env python3
"""
Test script for the Enhanced Zoho V8 Client

This script tests the synchronous V8 client implementation against the comprehensive
API analysis and validates all key functionality for email CRM sync.
"""

import sys
import logging
import requests
from pathlib import Path
from typing import Dict, Any, Optional

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from email_crm_sync.clients.zoho_v8_enhanced_client import ZohoV8EnhancedClient
from email_crm_sync.config.loader import ConfigLoader

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class V8ClientTester:
    """Test the enhanced V8 client functionality."""
    
    def __init__(self):
        self.client: Optional[ZohoV8EnhancedClient] = None
        self.config: Optional[ConfigLoader] = None
        self.test_results: Dict[str, Any] = {
            "connection": None,
            "module_discovery": None,
            "email_search": None,
            "criteria_search": None,
            "coql_query": None,
            "note_creation": None,
            "advanced_search": None,
            "metadata_retrieval": None
        }
    
    def initialize_client(self) -> bool:
        """Initialize the V8 client with configuration."""
        try:
            # Load configuration
            self.config = ConfigLoader()
            
            # Get Zoho configuration
            zoho_config = self.config.get_zoho_config()
            
            if not zoho_config or not zoho_config.get('access_token'):
                logger.error("❌ No Zoho access token found in configuration")
                logger.info("📝 Please run: make setup-tokens")
                return False
            
            # Initialize V8 enhanced client
            self.client = ZohoV8EnhancedClient(
                access_token=zoho_config['access_token'],
                data_center=zoho_config.get('data_center', 'com'),
                developments_module=zoho_config.get('developments_module', 'Developments')
            )
            
            logger.info("✅ V8 Enhanced Client initialized successfully")
            return True
            
        except (ValueError, FileNotFoundError) as e:
            logger.error("❌ Failed to initialize client: %s", str(e))
            return False
        except (ImportError, AttributeError, TypeError) as e:
            logger.error("❌ Failed to initialize client: %s", str(e))
            return False
    
    def test_connection(self) -> bool:
        """Test basic connection to Zoho CRM."""
        if not self.client:
            logger.error("❌ Client not initialized")
            return False
            
        try:
            logger.info("🔍 Testing connection...")
            results = self.client.test_connection()
            
            self.test_results["connection"] = results
            
            if results.get("connection"):
                logger.info("✅ Connection test passed")
                return True
            else:
                logger.error("❌ Connection test failed")
                for error in results.get("errors", []):
                    logger.error("   - %s", error)
                return False
                
        except (ConnectionError, TimeoutError, requests.RequestException) as e:
            logger.error("❌ Connection test error: %s", str(e))
            self.test_results["connection"] = {"error": str(e)}
            return False
    
    def test_module_discovery(self) -> bool:
        """Test module discovery functionality."""
        if not self.client:
            logger.error("❌ Client not initialized")
            return False
            
        try:
            logger.info("🔍 Testing module discovery...")
            modules = self.client.discover_modules()
            
            self.test_results["module_discovery"] = {
                "count": len(modules),
                "modules": [m.get("api_name", "Unknown") for m in modules[:5]]
            }
            
            if modules:
                logger.info("✅ Discovered %d modules", len(modules))
                logger.info("   Sample modules: %s", [m.get('api_name', 'Unknown') for m in modules[:3]])
                return True
            else:
                logger.error("❌ No modules discovered")
                return False
                
        except Exception as e:
            logger.error("❌ Module discovery error: %s", str(e))
            self.test_results["module_discovery"] = {"error": str(e)}
            return False
    
    def test_email_search(self) -> bool:
        """Test email-based search functionality."""
        if not self.client:
            logger.error("❌ Client not initialized")
            return False
            
        try:
            logger.info("🔍 Testing email search...")
            
            # Test with a sample email (won't find results but tests API)
            test_email = "test@example.com"
            results = self.client.search_by_email(test_email)
            
            self.test_results["email_search"] = {
                "test_email": test_email,
                "results_count": len(results),
                "success": True
            }
            
            logger.info("✅ Email search completed (found %d records)", len(results))
            return True
            
        except Exception as e:
            logger.error("❌ Email search error: %s", str(e))
            self.test_results["email_search"] = {"error": str(e)}
            return False
    
    def test_criteria_search(self) -> bool:
        """Test criteria-based search functionality."""
        if not self.client:
            logger.error("❌ Client not initialized")
            return False
            
        try:
            logger.info("🔍 Testing criteria search...")
            
            # Test with a sample criteria
            test_criteria = "(Email:*@example.com)"
            results = self.client.search_by_criteria(test_criteria)
            
            self.test_results["criteria_search"] = {
                "test_criteria": test_criteria,
                "results_count": len(results),
                "success": True
            }
            
            logger.info("✅ Criteria search completed (found %d records)", len(results))
            return True
            
        except Exception as e:
            logger.error("❌ Criteria search error: %s", str(e))
            self.test_results["criteria_search"] = {"error": str(e)}
            return False
    
    def test_notes_functionality(self) -> bool:
        """Test notes functionality (read-only)."""
        if not self.client:
            logger.error("❌ Client not initialized")
            return False
            
        try:
            logger.info("🔍 Testing notes functionality...")
            
            # Test getting notes (read-only test)
            notes_result = self.client.get_notes()
            
            self.test_results["note_creation"] = {
                "get_notes_success": notes_result.get("success", False),
                "notes_count": len(notes_result.get("notes", [])),
                "test_type": "read_only"
            }
            
            if notes_result.get("success"):
                logger.info("✅ Notes functionality working (found %d notes)", len(notes_result.get('notes', [])))
                return True
            else:
                logger.error("❌ Notes functionality test failed")
                return False
                
        except Exception as e:
            logger.error("❌ Notes test error: %s", str(e))
            self.test_results["note_creation"] = {"error": str(e)}
            return False
    
    def test_advanced_search(self) -> bool:
        """Test advanced search functionality."""
        if not self.client:
            logger.error("❌ Client not initialized")
            return False
            
        try:
            logger.info("🔍 Testing advanced search...")
            
            # Test advanced search with sample data
            results = self.client.advanced_email_search(
                email="test@example.com",
                company_name="Example Corp"
            )
            
            self.test_results["advanced_search"] = {
                "results_count": len(results),
                "success": True
            }
            
            logger.info("✅ Advanced search completed (found %d records)", len(results))
            return True
            
        except Exception as e:
            logger.error("❌ Advanced search error: %s", str(e))
            self.test_results["advanced_search"] = {"error": str(e)}
            return False
    
    def test_metadata_retrieval(self) -> bool:
        """Test metadata retrieval functionality."""
        if not self.client:
            logger.error("❌ Client not initialized")
            return False
            
        try:
            logger.info("🔍 Testing metadata retrieval...")
            
            # Test getting field metadata
            fields = self.client.get_field_metadata()
            
            self.test_results["metadata_retrieval"] = {
                "fields_count": len(fields),
                "success": len(fields) > 0
            }
            
            if fields:
                logger.info("✅ Metadata retrieval working (found %d fields)", len(fields))
                return True
            else:
                logger.error("❌ No field metadata retrieved")
                return False
                
        except Exception as e:
            logger.error("❌ Metadata retrieval error: %s", str(e))
            self.test_results["metadata_retrieval"] = {"error": str(e)}
            return False
    
    def run_all_tests(self) -> None:
        """Run all tests and display results."""
        logger.info("🚀 Starting Enhanced V8 Client Tests")
        logger.info("=" * 50)
        
        # Initialize client
        if not self.initialize_client():
            logger.error("❌ Failed to initialize client. Aborting tests.")
            return
        
        # Run tests
        tests = [
            ("Connection", self.test_connection),
            ("Module Discovery", self.test_module_discovery),
            ("Email Search", self.test_email_search),
            ("Criteria Search", self.test_criteria_search),
            ("Notes Functionality", self.test_notes_functionality),
            ("Advanced Search", self.test_advanced_search),
            ("Metadata Retrieval", self.test_metadata_retrieval)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            logger.info("\n📋 Running %s test...", test_name)
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                logger.error("❌ %s test failed with exception: %s", test_name, str(e))
        
        # Display summary
        logger.info("\n%s", "=" * 50)
        logger.info("🏆 Test Results Summary")
        logger.info("=" * 50)
        logger.info("Tests Passed: %d/%d", passed, total)
        logger.info("Success Rate: %.1f%%", (passed/total)*100)
        
        if passed == total:
            logger.info("🎉 All tests passed! V8 Enhanced Client is ready for production.")
        elif passed >= total * 0.7:
            logger.info("⚠️  Most tests passed. Client is functional with minor issues.")
        else:
            logger.error("❌ Multiple test failures. Please check configuration and API access.")
        
        # Display detailed results
        logger.info("\n📊 Detailed Results:")
        for test_name, result in self.test_results.items():
            if result:
                try:
                    if isinstance(result, dict) and "error" in result:
                        logger.info("   %s: ❌ %s", test_name, result.get("error", "Unknown error"))
                    else:
                        logger.info("   %s: ✅ Success", test_name)
                except (TypeError, AttributeError):
                    logger.info("   %s: ✅ Success", test_name)

def main():
    """Main function to run tests."""
    try:
        tester = V8ClientTester()
        tester.run_all_tests()
    except KeyboardInterrupt:
        logger.info("\n⏹️  Tests interrupted by user")
    except Exception as e:
        logger.error("❌ Test runner error: %s", str(e))

if __name__ == "__main__":
    main()