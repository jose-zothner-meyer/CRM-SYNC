#!/usr/bin/env python3
"""
Zoho CRM Complete Setup Script

This script provides a guided setup for Zoho CRM API integration following 
the official Zoho API v8 documentation:
https://www.zoho.com/crm/developer/docs/api/v8/oauth-overview.html

Supports:
- Multi-region OAuth2 setup (EU, US, India, Australia, etc.)
- Official scope requirements for CRM access
- Self-client configuration for automated processes
- Automatic token refresh with proper error handling

Usage:
    python scripts/setup_zoho_complete.py
"""

import sys
import subprocess
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def print_header():
    """Print the setup header."""
    print("🚀 Zoho CRM Complete Setup Guide")
    print("=" * 50)
    print("This script will help you set up Zoho CRM API integration.")
    print("You can choose between OAuth2 (recommended) or simple token setup.")
    print()

def print_oauth2_benefits():
    """Print the benefits of OAuth2 setup."""
    print("🔐 OAuth2 Setup Benefits:")
    print("  ✅ Automatic token refresh (no manual intervention)")
    print("  ✅ More secure (tokens can be revoked)")
    print("  ✅ Better for production use")
    print("  ✅ Follows OAuth2 best practices")
    print()

def print_simple_token_info():
    """Print information about simple token setup."""
    print("🔑 Simple Token Setup:")
    print("  ⚠️  Requires manual token refresh every ~1 hour")
    print("  ⚠️  Less secure")
    print("  ✅ Faster initial setup")
    print("  ✅ Good for testing")
    print()

def get_user_choice():
    """Get user's preferred setup method."""
    print("Setup Options:")
    print("1. OAuth2 Flow (Recommended)")
    print("2. Simple Token")
    print("3. Show detailed comparison")
    print("4. Exit")
    print()
    
    while True:
        choice = input("Choose setup method (1-4): ").strip()
        if choice in ["1", "2", "3", "4"]:
            return choice
        print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")

def show_detailed_comparison():
    """Show detailed comparison between setup methods."""
    print("\n" + "=" * 60)
    print("📊 DETAILED COMPARISON")
    print("=" * 60)
    
    print("\n🔐 OAuth2 Flow (Recommended)")
    print("-" * 30)
    print("Setup Steps:")
    print("  1. Create Self Client in Zoho API Console")
    print("  2. Run: python scripts/generate_zoho_oauth_url.py")
    print("  3. Visit authorization URL in browser")
    print("  4. Run: python scripts/exchange_zoho_tokens.py")
    print("  5. Done! Tokens auto-refresh")
    print()
    print("Pros:")
    print("  ✅ Set once, works forever")
    print("  ✅ Automatic token refresh")
    print("  ✅ More secure")
    print("  ✅ Production ready")
    print()
    print("Cons:")
    print("  ❌ Slightly more complex initial setup")
    print("  ❌ Requires web browser access")
    
    print("\n🔑 Simple Token")
    print("-" * 15)
    print("Setup Steps:")
    print("  1. Go to Zoho API Console")
    print("  2. Generate access token")
    print("  3. Copy token to config file")
    print("  4. Manually refresh every hour")
    print()
    print("Pros:")
    print("  ✅ Very quick setup")
    print("  ✅ No browser required")
    print("  ✅ Good for testing")
    print()
    print("Cons:")
    print("  ❌ Manual token refresh needed")
    print("  ❌ Tokens expire quickly (~1 hour)")
    print("  ❌ Not suitable for production")
    print("  ❌ Application stops working when token expires")
    
    print("\n" + "=" * 60)
    input("Press Enter to continue...")
    print()

def run_oauth2_setup():
    """Run the OAuth2 setup process."""
    print("\n🔐 Starting OAuth2 Setup...")
    print("=" * 30)
    
    print("\n📋 Prerequisites:")
    print("1. Zoho CRM account (any data center)")
    print("2. Web browser access")
    print("3. Ability to copy/paste URLs")
    print()
    
    confirm = input("Do you have access to these? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ OAuth2 setup requires browser access. Consider using Simple Token instead.")
        return False
    
    print("\n🚀 Step 1: Generate Authorization URL")
    print("Running: python scripts/generate_zoho_oauth_url.py")
    print("-" * 50)
    
    try:
        result = subprocess.run([
            sys.executable, 
            str(project_root / "scripts" / "generate_zoho_oauth_url.py")
        ], cwd=project_root, check=False)
        
        if result.returncode != 0:
            print("❌ Failed to generate authorization URL")
            return False
        
        print("\n🚀 Step 2: Exchange Authorization Code for Tokens")
        print("Running: python scripts/exchange_zoho_tokens.py")
        print("-" * 50)
        
        result = subprocess.run([
            sys.executable,
            str(project_root / "scripts" / "exchange_zoho_tokens.py")
        ], cwd=project_root, check=False)
        
        if result.returncode == 0:
            print("\n✅ OAuth2 setup completed successfully!")
            return True
        else:
            print("❌ Token exchange failed")
            return False
            
    except (FileNotFoundError, OSError) as e:
        print(f"❌ Error during OAuth2 setup: {e}")
        return False

def run_simple_token_setup():
    """Guide user through simple token setup."""
    print("\n🔑 Simple Token Setup Guide")
    print("=" * 30)
    
    print("\n📋 Official Zoho API Console Access:")
    print("Based on official multi-DC documentation:")
    print("https://www.zoho.com/crm/developer/docs/api/v8/multi-dc.html")
    
    # Official data center endpoints per Zoho documentation
    data_centers = {
        "eu": {
            "console": "https://api-console.zoho.eu",
            "crm": "https://crm.zoho.eu",
            "auth": "https://accounts.zoho.eu"
        },
        "com": {
            "console": "https://api-console.zoho.com", 
            "crm": "https://crm.zoho.com",
            "auth": "https://accounts.zoho.com"
        },
        "in": {
            "console": "https://api-console.zoho.in",
            "crm": "https://crm.zoho.in", 
            "auth": "https://accounts.zoho.in"
        },
        "au": {
            "console": "https://api-console.zoho.com.au",
            "crm": "https://crm.zoho.com.au",
            "auth": "https://accounts.zoho.com.au"
        },
        "cn": {
            "console": "https://api-console.zoho.com.cn",
            "crm": "https://crm.zoho.com.cn",
            "auth": "https://accounts.zoho.com.cn"
        },
        "jp": {
            "console": "https://api-console.zoho.jp",
            "crm": "https://crm.zoho.jp",
            "auth": "https://accounts.zoho.jp"
        },
        "ca": {
            "console": "https://api-console.zohocloud.ca",
            "crm": "https://crm.zohocloud.ca",
            "auth": "https://accounts.zohocloud.ca"
        }
    }
    
    print("\nChoose your data center based on your Zoho CRM URL:")
    for dc, urls in data_centers.items():
        print(f"   • If your CRM is {urls['crm']} → Console: {urls['console']}")
    
    print("\n📋 Setup Steps:")
    print("1. Go to your appropriate API Console (above)")
    print("2. Create a 'Self Client' application (recommended for background processes)")
    print("3. For OAuth2 setup, configure these scopes:")
    print("   Required: ZohoCRM.modules.ALL,ZohoCRM.settings.READ,ZohoCRM.org.READ")
    print("   Optional: ZohoCRM.coql.READ (for advanced searches)")
    print("4. For quick testing, use 'Generate Token' with 10-minute duration")
    print("5. Copy the generated access token")
    print()
    
    token = input("Paste your access token here: ").strip()
    if not token:
        print("❌ No token provided!")
        return False
    
    if not token.startswith("1000."):
        print("⚠️  Warning: Zoho tokens typically start with '1000.'")
        confirm = input("Are you sure this is correct? (y/n): ").strip().lower()
        if confirm != 'y':
            return False
    
    # Update config file
    config_file = project_root / "email_crm_sync" / "config" / "api_keys.yaml"
    if not config_file.exists():
        print(f"❌ Configuration file not found: {config_file}")
        return False
    
    try:
        import yaml
        
        # Load existing config
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
        
        # Update with simple token
        config['zoho_access_token'] = token
        
        # Write back
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        print("✅ Updated configuration file with your token")
        print("⚠️  Remember: This token will expire and need manual refresh!")
        return True
        
    except ImportError:
        print("❌ PyYAML not installed. Please run: pip install PyYAML")
        return False
    except (OSError, IOError) as e:
        print(f"❌ Error updating configuration: {e}")
        return False

def test_setup():
    """Test the setup by running a quick API call."""
    print("\n🧪 Testing your setup...")
    
    try:
        # Try to import and test the client
        from email_crm_sync.clients.zoho_v8_enhanced_client import ZohoV8EnhancedClient
        from email_crm_sync.config.loader import ConfigLoader
        
        # Load configuration to get the access token
        config = ConfigLoader()
        
        if not config.zoho_token:
            print("❌ No Zoho access token found in configuration")
            return False
        
        client = ZohoV8EnhancedClient(
            access_token=config.zoho_token,
            data_center=config.zoho_data_center,
            developments_module=config.zoho_developments_module
        )
        result = client.test_connection()
        
        if result.get('success'):
            org_name = result.get('organization', {}).get('company_name', 'Unknown')
            print(f"✅ Setup test successful! Connected to: {org_name}")
            return True
        else:
            print(f"❌ Setup test failed: {result.get('error', 'Unknown error')}")
            return False
            
    except (ImportError, ValueError, FileNotFoundError, AttributeError) as e:
        print(f"❌ Setup test failed: {e}")
        return False

def main():
    """Main setup function."""
    print_header()
    
    while True:
        print_oauth2_benefits()
        print_simple_token_info()
        
        choice = get_user_choice()
        
        if choice == "1":
            # OAuth2 Flow
            if run_oauth2_setup():
                if test_setup():
                    print("\n🎉 Setup completed successfully!")
                    print("You can now run: python main.py --mode once")
                    break
                else:
                    print("❌ Setup completed but test failed. Please check your configuration.")
            else:
                print("❌ OAuth2 setup failed. You can try again or use Simple Token.")
                
        elif choice == "2":
            # Simple Token
            if run_simple_token_setup():
                if test_setup():
                    print("\n✅ Simple token setup completed!")
                    print("⚠️  Remember to refresh your token when it expires!")
                    print("You can now run: python main.py --mode once")
                    break
                else:
                    print("❌ Setup completed but test failed. Please check your token.")
            else:
                print("❌ Simple token setup failed. Please try again.")
                
        elif choice == "3":
            # Show comparison
            show_detailed_comparison()
            continue
            
        elif choice == "4":
            # Exit
            print("👋 Setup cancelled. Run this script again when ready.")
            sys.exit(0)
        
        # Ask if user wants to try again
        print()
        retry = input("Would you like to try a different setup method? (y/n): ").strip().lower()
        if retry != 'y':
            break

if __name__ == "__main__":
    main()
