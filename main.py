#!/usr/bin/env python3
"""
Enhanced Email to CRM Sync - Unified CLI Application

Comprehensive refactored version with all functionality consolidated:
- Centralized configuration management
- Modular client components  
- Complete CLI interface with all tools integrated
- Better error handling with custom exceptions
- Consolidated token management and setup

Usage:
    python main_refactored.py run --mode once                        # Process emails once
    python main_refactored.py run --mode monitor                     # Monitor continuously
    python main_refactored.py token refresh                          # Refresh expired tokens
    python main_refactored.py token exchange --code "auth_code"      # Exchange authorization code
    python main_refactored.py setup verify-gmail                     # Verify Gmail setup
    python main_refactored.py health                                 # Run health checks
    python main_refactored.py discover                               # Discover Zoho modules
"""

import sys
import os
import logging
import argparse
import time
import json
from typing import Dict, Any, Optional
from pathlib import Path

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import refactored components
from email_crm_sync.config import config
from email_crm_sync.exceptions import (
    CrmSyncError, ConfigurationError, TokenError, 
    EmailProcessingError, ZohoApiError, GmailApiError, OpenAIApiError
)
from email_crm_sync.clients.gmail_client import GmailClient
from email_crm_sync.clients.openai_client import EnhancedOpenAIProcessor
from email_crm_sync.clients.zoho_v8_enhanced_client import ZohoV8EnhancedClient
from email_crm_sync.services.email_processor import EmailProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('email_crm_sync.log', mode='a')
    ]
)

logger = logging.getLogger(__name__)


class EmailCRMSyncApp:
    """
    Main application class for Email to CRM synchronization.
    
    This class provides a unified interface for all application functionality
    including email processing, token management, and health checks.
    """
    
    def __init__(self):
        """Initialize the application with centralized configuration."""
        self.config = config
        self.gmail_client: Optional[GmailClient] = None
        self.openai_client: Optional[EnhancedOpenAIProcessor] = None
        self.zoho_client: Optional[ZohoV8EnhancedClient] = None
        self.processor: Optional[EmailProcessor] = None
    
    def initialize(self) -> bool:
        """
        Initialize all clients and services.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            logger.info("🚀 Initializing Email CRM Sync Application...")
            
            # Validate configuration
            if not self._validate_config():
                raise ConfigurationError("Configuration validation failed")
            
            # Initialize clients
            self._init_clients()
            
            # Initialize processor
            self.processor = EmailProcessor(
                gmail=self.gmail_client,
                openai=self.openai_client,
                zoho=self.zoho_client
            )
            
            logger.info("✅ Application initialized successfully")
            return True
            
        except (ConfigurationError, CrmSyncError) as e:
            logger.error("❌ Failed to initialize application: %s", str(e))
            return False
    
    def _validate_config(self) -> bool:
        """Validate configuration settings."""
        required_keys = [
            ('openai_key', 'OpenAI API key'),
            ('zoho_token', 'Zoho access token'), 
            ('zoho_refresh_token', 'Zoho refresh token'),
            ('zoho_client_id', 'Zoho client ID'),
            ('zoho_client_secret', 'Zoho client secret'),
            ('gmail_credentials', 'Gmail credentials path')
        ]
        
        for key, description in required_keys:
            if not getattr(self.config, key, None):
                logger.error("❌ Missing required configuration: %s", description)
                return False
        
        return True
    
    def _init_clients(self):
        """Initialize API clients."""
        try:
            # Initialize Gmail client
            gmail_credentials = self.config.gmail_credentials
            if not gmail_credentials:
                raise ConfigurationError("Gmail credentials path not configured")
            
            self.gmail_client = GmailClient(
                credentials_path=str(gmail_credentials)
            )
            
            # Initialize OpenAI client
            openai_key = self.config.openai_key
            if not openai_key:
                raise ConfigurationError("OpenAI API key not configured")
                
            self.openai_client = EnhancedOpenAIProcessor(
                api_key=str(openai_key)
            )
            
            # Initialize Zoho client
            zoho_token = self.config.zoho_token
            if not zoho_token:
                raise ConfigurationError("Zoho access token not configured")
                
            self.zoho_client = ZohoV8EnhancedClient(
                access_token=str(zoho_token),
                data_center=str(self.config.zoho_data_center),
                developments_module=str(self.config.zoho_developments_module)
            )
            
        except ConfigurationError:
            raise
        except CrmSyncError as e:
            raise ConfigurationError(f"Failed to initialize clients: {str(e)}") from e
    
    def run_health_check(self) -> Dict[str, Any]:
        """
        Run comprehensive health checks on all components.
        
        Returns:
            Dict containing health check results
        """
        logger.info("🔍 Running health checks...")
        
        health_status = {
            'gmail': False,
            'openai': False,
            'zoho': False,
            'overall': False
        }
        
        try:
            # Check Gmail client
            if self.gmail_client:
                try:
                    self.gmail_client.get_starred_emails()
                    health_status['gmail'] = True
                    logger.info("✅ Gmail client: OK")
                except GmailApiError as e:
                    logger.error("❌ Gmail client: %s", str(e))
            
            # Check OpenAI client
            if self.openai_client:
                try:
                    # Simple test call
                    test_result = self.openai_client.extract_development_info("Test", "Test email content")
                    if test_result:
                        health_status['openai'] = True
                        logger.info("✅ OpenAI client: OK")
                except OpenAIApiError as e:
                    logger.error("❌ OpenAI client: %s", str(e))
            
            # Check Zoho client
            if self.zoho_client:
                try:
                    # Test basic API access with word search (which works)
                    test_result = self.zoho_client.search_by_word("test")
                    health_status['zoho'] = True
                    logger.info("✅ Zoho client: OK")
                except ZohoApiError as e:
                    logger.error("❌ Zoho client: %s", str(e))
            
            # Overall health
            health_status['overall'] = all([
                health_status['gmail'],
                health_status['openai'],
                health_status['zoho']
            ])
            
            if health_status['overall']:
                logger.info("✅ All health checks passed")
            else:
                logger.warning("⚠️ Some health checks failed")
            
        except CrmSyncError as e:
            logger.error("❌ Health check failed: %s", str(e))
        
        return health_status
    
    def process_emails_once(self) -> Dict[str, Any]:
        """
        Process emails once and return results.
        
        Returns:
            Dict containing processing results
        """
        if not self.processor:
            raise EmailProcessingError("Processor not initialized")
        
        logger.info("📧 Starting email processing...")
        
        try:
            results = self.processor.process_emails()
            
            # The processor might not return results, so create a default
            if results is None:
                results = {'emails_processed': 0, 'notes_created': 0}
            
            # Log summary
            total_processed = results.get('emails_processed', 0)
            notes_created = results.get('notes_created', 0)
            
            logger.info("📊 Processing complete:")
            logger.info("   Emails processed: %d", total_processed)
            logger.info("   Notes created: %d", notes_created)
            
            return results
            
        except (EmailProcessingError, GmailApiError, ZohoApiError, OpenAIApiError) as e:
            logger.error("❌ Email processing failed: %s", str(e))
            raise EmailProcessingError(f"Processing failed: {str(e)}") from e
        except (ValueError, TypeError, KeyError) as e:
            logger.error("❌ Data validation error in email processing: %s", str(e))
            raise ConfigurationError(f"Data validation error: {str(e)}") from e
        except Exception as e:
            logger.error("❌ Unexpected error in email processing: %s", str(e), exc_info=True)
            raise EmailProcessingError(f"Unexpected processing error: {str(e)}") from e
    
    def refresh_tokens(self) -> bool:
        """
        Refresh expired Zoho tokens.
        
        Returns:
            bool: True if refresh successful, False otherwise
        """
        try:
            logger.info("🔄 Refreshing Zoho tokens...")
            
            # Import token refresh functionality
            from tools.refresh_token import refresh_zoho_token, load_config
            
            config_data, _ = load_config()
            result = refresh_zoho_token(config_data)
            
            if result:
                # Reload configuration
                self.config = config  # Reload centralized config
                logger.info("✅ Tokens refreshed successfully")
                return True
            else:
                logger.error("❌ Token refresh failed")
                return False
                
        except (TokenError, ConfigurationError) as e:
            logger.error("❌ Token/configuration error: %s", str(e))
            raise TokenError(f"Token refresh failed: {str(e)}") from e
        except (FileNotFoundError, PermissionError, json.JSONDecodeError) as e:
            logger.error("❌ File access error during token refresh: %s", str(e))
            raise TokenError(f"Token refresh file error: {str(e)}") from e
        except Exception as e:
            logger.error("❌ Unexpected token refresh error: %s", str(e), exc_info=True)
            raise TokenError(f"Unexpected token refresh error: {str(e)}") from e
    
    def exchange_authorization_code(self, auth_code: str) -> bool:
        """
        Exchange authorization code for tokens.
        
        Args:
            auth_code: Authorization code from Zoho OAuth
            
        Returns:
            bool: True if exchange successful, False otherwise
        """
        try:
            logger.info("🔐 Exchanging authorization code for tokens...")
            
            # Import token exchange functionality
            from tools.exchange_new_tokens import exchange_authorization_code
            
            exchange_authorization_code(auth_code)
            
            # Reload configuration
            self.config = config  # Reload centralized config
            logger.info("✅ Authorization code exchanged successfully")
            return True
            
        except (TokenError, ConfigurationError) as e:
            logger.error("❌ Token/configuration error during exchange: %s", str(e))
            raise TokenError(f"Token exchange failed: {str(e)}") from e
        except (FileNotFoundError, PermissionError, json.JSONDecodeError) as e:
            logger.error("❌ File access error during token exchange: %s", str(e))
            raise TokenError(f"Token exchange file error: {str(e)}") from e
        except ImportError as e:
            logger.error("❌ Import error during token exchange: %s", str(e))
            raise TokenError(f"Token exchange import error: {str(e)}") from e
        except Exception as e:
            logger.error("❌ Unexpected error during authorization code exchange: %s", str(e), exc_info=True)
            raise TokenError(f"Unexpected token exchange error: {str(e)}") from e
    
    def discover_modules(self) -> Dict[str, Any]:
        """
        Discover available Zoho modules.
        
        Returns:
            Dict containing discovered modules
        """
        try:
            logger.info("🔍 Discovering Zoho modules...")
            
            if not self.zoho_client:
                raise ZohoApiError("Zoho client not initialized")
            
            # Use the client's built-in module discovery
            # For now, we'll import the existing functionality
            from tools.discover_zoho_modules import main as discover_main
            
            discover_main()
            
            return {"status": "completed"}
            
        except (ZohoApiError, ConfigurationError) as e:
            logger.error("❌ Zoho/configuration error during module discovery: %s", str(e))
            raise ZohoApiError(f"Module discovery failed: {str(e)}") from e
        except ImportError as e:
            logger.error("❌ Import error during module discovery: %s", str(e))
            raise ZohoApiError(f"Module discovery import error: {str(e)}") from e
        except Exception as e:
            logger.error("❌ Unexpected error during module discovery: %s", str(e), exc_info=True)
            raise ZohoApiError(f"Unexpected module discovery error: {str(e)}") from e

    def verify_gmail_setup(self) -> bool:
        """
        Verify Gmail API setup and credentials.
        
        Returns:
            bool: True if Gmail setup is valid, False otherwise
        """
        try:
            logger.info("🔍 Verifying Gmail setup...")
            
            creds_path = Path("email_crm_sync/config/gmail_credentials.json")
            
            if not creds_path.exists():
                logger.error("❌ gmail_credentials.json file not found!")
                logger.error("Please download the credentials file from Google Cloud Console")
                logger.error("Expected location: %s", creds_path)
                return False
            
            with open(creds_path, 'r', encoding='utf-8') as f:
                creds = json.load(f)
            
            # Check if it's the correct format
            if 'installed' not in creds:
                logger.error("❌ Invalid credentials format!")
                logger.error("Make sure you downloaded the file for 'Desktop Application'")
                return False
            
            installed = creds['installed']
            required_fields = ['client_id', 'client_secret', 'auth_uri', 'token_uri']
            
            missing_fields = []
            for field in required_fields:
                if field not in installed or installed[field] == f"your-{field.replace('_', '-')}-here":
                    missing_fields.append(field)
            
            if missing_fields:
                logger.error("❌ Missing or incomplete fields: %s", ', '.join(missing_fields))
                logger.error("Please download the complete credentials file from Google Cloud Console")
                return False
            
            logger.info("✅ Gmail credentials file looks good!")
            logger.info("   Client ID: %s...", installed['client_id'][:50])
            logger.info("   Project ID: %s", installed.get('project_id', 'Not specified'))
            
            # Test Gmail client initialization if possible
            if self.gmail_client:
                try:
                    # Simple test to see if we can initialize
                    self.gmail_client.get_starred_emails()
                    logger.info("✅ Gmail client test successful")
                except (GmailApiError, CrmSyncError) as e:
                    logger.warning("⚠️ Gmail client test failed: %s", str(e))
                    logger.info("This might be normal if Gmail hasn't been authorized yet")
            
            return True
            
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            logger.error("❌ Gmail setup verification failed: %s", str(e))
            return False


def create_cli_parser() -> argparse.ArgumentParser:
    """Create and configure the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description='Enhanced Email CRM Sync Application - Unified CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s run --mode once                        # Process emails once
    %(prog)s run --mode monitor                     # Monitor continuously
    %(prog)s token refresh                          # Refresh expired tokens
    %(prog)s token exchange --code "auth_code"      # Exchange authorization code
    %(prog)s setup verify-gmail                     # Verify Gmail setup
    %(prog)s health                                 # Run health checks
    %(prog)s discover                               # Discover Zoho modules
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run the email sync process')
    run_parser.add_argument(
        '--mode', 
        choices=['once', 'monitor'], 
        default='once',
        help='Run once or continuously monitor for new emails'
    )
    run_parser.add_argument(
        '--interval', 
        type=int, 
        default=300,
        help='Monitoring interval in seconds (default: 300)'
    )
    
    # Token management command
    token_parser = subparsers.add_parser('token', help='Manage Zoho tokens')
    token_subparsers = token_parser.add_subparsers(dest='token_action')
    
    # Token refresh
    token_subparsers.add_parser('refresh', help='Refresh expired tokens')
    
    # Token exchange
    exchange_parser = token_subparsers.add_parser('exchange', help='Exchange authorization code')
    exchange_parser.add_argument(
        '--code', 
        required=True,
        help='Authorization code from Zoho OAuth'
    )
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Setup and verification tools')
    setup_subparsers = setup_parser.add_subparsers(dest='setup_action')
    
    # Gmail verification
    setup_subparsers.add_parser('verify-gmail', help='Verify Gmail API setup and credentials')
    
    # Health check command
    subparsers.add_parser('health', help='Run health checks')
    
    # Discover modules command
    subparsers.add_parser('discover', help='Discover available Zoho modules')
    
    return parser


def main():
    """Main entry point for the application."""
    parser = create_cli_parser()
    args = parser.parse_args()
    
    # If no command provided, default to run once
    if not args.command:
        args.command = 'run'
        args.mode = 'once'
    
    app = EmailCRMSyncApp()
    
    try:
        # Initialize application for commands that need it
        if args.command in ['run', 'health', 'discover']:
            if not app.initialize():
                logger.error("❌ Failed to initialize application")
                sys.exit(1)
        
        # Handle commands
        if args.command == 'run':
            if args.mode == 'once':
                app.process_emails_once()
            elif args.mode == 'monitor':
                logger.info("🔄 Starting monitor mode (interval: %d seconds)", args.interval)
                try:
                    while True:
                        app.process_emails_once()
                        logger.info("😴 Waiting %d seconds before next run...", args.interval)
                        time.sleep(args.interval)
                except KeyboardInterrupt:
                    logger.info("⏹️ Monitor mode stopped by user")
        
        elif args.command == 'token':
            if args.token_action == 'refresh':
                if app.refresh_tokens():
                    logger.info("✅ Token refresh completed successfully")
                else:
                    logger.error("❌ Token refresh failed")
                    sys.exit(1)
            elif args.token_action == 'exchange':
                if app.exchange_authorization_code(args.code):
                    logger.info("✅ Token exchange completed successfully")
                else:
                    logger.error("❌ Token exchange failed")
                    sys.exit(1)
        
        elif args.command == 'setup':
            if args.setup_action == 'verify-gmail':
                if app.verify_gmail_setup():
                    logger.info("✅ Gmail setup verification completed successfully")
                else:
                    logger.error("❌ Gmail setup verification failed")
                    sys.exit(1)
        
        elif args.command == 'health':
            health_status = app.run_health_check()
            if health_status['overall']:
                logger.info("✅ All health checks passed")
            else:
                logger.error("❌ Some health checks failed")
                sys.exit(1)
        
        elif args.command == 'discover':
            app.discover_modules()
            logger.info("✅ Module discovery completed")
        
    except KeyboardInterrupt:
        logger.info("⏹️ Application interrupted by user")
        sys.exit(0)
    except CrmSyncError as e:
        logger.error("❌ Application error: %s", str(e))
        sys.exit(1)
    except (ValueError, TypeError, FileNotFoundError, PermissionError) as e:
        logger.error("💥 System error: %s", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
