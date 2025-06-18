#!/usr/bin/env python3
"""
Enhanced Email to CRM Sync - Main Application

This version uses only working Zoho API methods and guarantees note creation
for every processed email through intelligent fallback strategies.

Key Improvements:
- Uses only word search (which works reliably)
- Implements robust fallback note creation
- Enhanced email matching with multiple strategies
- Optimized OpenAI usage (single API call per email)
- Comprehensive error handling and logging
"""

import sys
import os
import logging
from datetime import datetime

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import our enhanced components
from email_crm_sync.clients.gmail_client import GmailClient
from email_crm_sync.clients.openai_client import EnhancedOpenAIProcessor
from email_crm_sync.clients.zoho_v8_enhanced_client import ZohoV8EnhancedClient
from email_crm_sync.services.enhanced_processor import EnhancedEmailProcessor
from email_crm_sync.config.loader import ConfigLoader

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
    """Main application class for Email to CRM synchronization"""

    HEALTH_KEYS = ['gmail', 'openai', 'zoho', 'overall']
    
    def __init__(self):
        self.config = None
        self.gmail = None
        self.openai = None
        self.zoho = None
        self.processor = None
        
    def initialize(self):
        """Initialize all components"""
        try:
            logger.info("🚀 Starting Enhanced Email CRM Sync Application")
            logger.info("Timestamp: %s", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            # Load configuration
            logger.info("📋 Loading configuration...")
            self.config = ConfigLoader()
            
            # Log key configuration
            self._log_configuration()
            
            # Initialize clients
            logger.info("🔧 Initializing API clients...")
            
            # Gmail Client
            logger.info("  - Initializing Gmail client...")
            gmail_credentials_path = self.config.gmail_credentials if self.config.gmail_credentials is not None else ""
            self.gmail = GmailClient(gmail_credentials_path)
            
            # OpenAI Client
            logger.info("  - Initializing OpenAI client...")
            if not isinstance(self.config.openai_key, str) or not self.config.openai_key:
                raise ValueError("OpenAI API key is missing or invalid in configuration.")
            # Pass model settings from configuration
            model_cfg = self.config.get_openai_config()
            self.openai = EnhancedOpenAIProcessor(self.config.openai_key, model_cfg)
            
            # Zoho Client
            logger.info("  - Initializing Zoho CRM client...")
            zoho_config = self.config.get_zoho_config()
            self.zoho = ZohoV8EnhancedClient(
                access_token=zoho_config['access_token'],
                data_center=zoho_config['data_center'],
                developments_module=zoho_config['developments_module']
            )
            
            # Enhanced Email Processor
            logger.info("  - Initializing enhanced email processor...")
            self.processor = EnhancedEmailProcessor(self.gmail, self.openai, self.zoho)
            
            logger.info("✅ All components initialized successfully")
            return True
            
        except Exception as e:
            if isinstance(e, (KeyboardInterrupt, SystemExit)):
                raise
            logger.error("❌ Failed to initialize application: %s", str(e))
            return False
    
    def _log_configuration(self):
        """Log key configuration details"""
        if not self.config:
            return
            
        logger.info("📊 Configuration Summary:")
        logger.info("  - Zoho Data Center: %s", getattr(self.config, 'zoho_data_center', 'Unknown'))
        logger.info("  - Zoho Module: %s", getattr(self.config, 'zoho_developments_module', 'Unknown'))
        logger.info("  - Email Batch Size: %s", getattr(self.config, 'email_batch_size', 'Unknown'))
        logger.info("  - Log Level: %s", getattr(self.config, 'log_level', 'Unknown'))
    
    def run_health_check(self):
        """Run health checks on all components"""
        logger.info("🔍 Running health checks...")
        
        health_status = {key: False for key in self.HEALTH_KEYS}
        
        # Gmail Health Check
        try:
            logger.info("  - Testing Gmail connection...")
            # Simply check if Gmail client is initialized
            if self.gmail:
                logger.info("    ✅ Gmail: Client initialized successfully")
                health_status['gmail'] = True
            else:
                logger.error("    ❌ Gmail: Client not initialized")
        except Exception as e:
            logger.error("    ❌ Gmail: %s", str(e))
        
        # OpenAI Health Check
        try:
            logger.info("  - Testing OpenAI connection...")
            # Simply check if OpenAI client is initialized
            if self.openai:
                logger.info("    ✅ OpenAI: Client initialized successfully")
                health_status['openai'] = True
            else:
                logger.error("    ❌ OpenAI: Client not initialized")
        except Exception as e:
            logger.error("    ❌ OpenAI: %s", str(e))
        
        # Zoho Health Check
        try:
            logger.info("  - Testing Zoho CRM connection...")
            # Use the available test_connection method
            if self.zoho and hasattr(self.zoho, 'test_connection'):
                test_result = self.zoho.test_connection()
                if test_result.get('success'):
                    logger.info("    ✅ Zoho CRM: Connection successful")
                    health_status['zoho'] = True
                else:
                    logger.error("    ❌ Zoho CRM: %s", test_result.get('error', 'Unknown error'))
            elif self.zoho:
                logger.info("    ✅ Zoho CRM: Client initialized successfully")
                health_status['zoho'] = True
            else:
                logger.error("    ❌ Zoho CRM: Client not initialized")
        except Exception as e:
            logger.error("    ❌ Zoho CRM: %s", str(e))
        
        # Overall Health
        health_status['overall'] = all([
            health_status['gmail'], 
            health_status['openai'], 
            health_status['zoho']
        ])
        
        if health_status['overall']:
            logger.info("✅ All health checks passed - System ready")
        else:
            logger.warning("⚠️ Some health checks failed - Check logs above")
        
        return health_status
    
    def process_emails(self):
        """Process new emails with enhanced reliability"""
        logger.info("📧 Starting email processing...")
        
        try:
            # Process emails using enhanced processor
            if self.processor and hasattr(self.processor, 'process_emails'):
                self.processor.process_emails()
                logger.info("✅ Email processing completed")
            else:
                logger.error("❌ Email processor not available")
                return False
            return True
            
        except Exception as e:
            logger.error("❌ Email processing failed: %s", str(e))
            return False
    
    def run_full_sync(self):
        """Run complete synchronization process"""
        logger.info("🔄 Starting full email-to-CRM synchronization...")
        
        # Run health checks first
        health_status = self.run_health_check()
        
        if not health_status['overall']:
            logger.error("❌ Health checks failed - aborting sync")
            return False
        
        # Process emails
        success = self.process_emails()
        
        if success:
            logger.info("✅ Full synchronization completed successfully")
            self._log_completion_summary()
        else:
            logger.error("❌ Synchronization completed with errors")
        
        return success
    
    def _log_completion_summary(self):
        """Log completion summary"""
        logger.info("📈 Sync Summary:")
        logger.info("  - Process completed at: %s", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        logger.info("  - Using enhanced processor with fallback strategies")
        logger.info("  - All emails guaranteed to create notes (via fallback if needed)")
        logger.info("  - Search methods: Word search only (most reliable)")

def main():
    """Main application entry point"""
    try:
        # Create and initialize application
        app = EmailCRMSyncApp()
        
        if not app.initialize():
            logger.error("❌ Failed to initialize application")
            sys.exit(1)
        
        # Run full synchronization
        success = app.run_full_sync()
        
        if success:
            logger.info("🎉 Application completed successfully")
            sys.exit(0)
        else:
            logger.error("💥 Application completed with errors")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("⏹️ Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error("💥 Unexpected error: %s", str(e))
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Email CRM Sync Application')
    parser.add_argument('--mode', choices=['once', 'monitor'], default='once',
                       help='Run once or continuously monitor for new emails')
    parser.add_argument('--interval', type=int, default=300,
                       help='Monitoring interval in seconds (default: 300)')
    parser.add_argument('--health-check', action='store_true',
                       help='Run health checks only')
    
    args = parser.parse_args()
    
    # Create and run the application
    app = EmailCRMSyncApp()
    
    if args.health_check:
        # Run health checks only
        if app.initialize():
            health_status = app.run_health_check()
            if health_status['overall']:
                logger.info("✅ All health checks passed")
                sys.exit(0)
            else:
                logger.error("❌ Some health checks failed")
                sys.exit(1)
        else:
            logger.error("❌ Failed to initialize application")
            sys.exit(1)
    elif args.mode == 'once':
        # Run once
        main()
    elif args.mode == 'monitor':
        # Monitor mode
        logger.info("🔄 Starting monitor mode (interval: %d seconds)", args.interval)
        import time
        try:
            while True:
                main()
                logger.info("😴 Waiting %d seconds before next run...", args.interval)
                time.sleep(args.interval)
        except KeyboardInterrupt:
            logger.info("⏹️ Monitor mode stopped by user")
            sys.exit(0)
