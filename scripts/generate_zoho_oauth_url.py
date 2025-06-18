#!/usr/bin/env python3
"""
Zoho CRM OAuth2 Authorization URL Generator

This script generates the authorization URL you need to visit in your browser
to obtain an authorization code for your Zoho CRM API integration.

Usage:
    python scripts/generate_zoho_oauth_url.py
"""

import sys
import urllib.parse
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from email_crm_sync.config.loader import ConfigLoader
except ImportError:
    ConfigLoader = None

def detect_data_center():
    """Detect the data center from existing config or ask user."""
    if ConfigLoader:
        try:
            config = ConfigLoader()
            data_center = config.zoho_data_center
            print(f"✅ Detected data center from config: {data_center}")
            return data_center
        except (ValueError, FileNotFoundError, AttributeError):
            print("❓ Could not detect data center from config.")
    
    print("\nAvailable Zoho data centers:")
    print("1. eu - Europe (https://accounts.zoho.eu)")
    print("2. com - US (https://accounts.zoho.com)")
    print("3. in - India (https://accounts.zoho.in)")
    print("4. com.au - Australia (https://accounts.zoho.com.au)")
    
    while True:
        choice = input("\nEnter your data center (eu/com/in/com.au) [default: eu]: ").strip().lower()
        if not choice:
            choice = "eu"
        if choice in ["eu", "com", "in", "com.au"]:
            return choice
        print("❌ Invalid choice. Please enter: eu, com, in, or com.au")

def get_client_credentials():
    """Get client ID and secret from configuration or user input."""
    # Try to load from existing configuration first
    if ConfigLoader:
        try:
            config = ConfigLoader()
            zoho_config = config.get_zoho_config()
            
            if zoho_config.get('client_id') and zoho_config.get('client_secret'):
                print("\n✅ Found existing Zoho credentials in configuration")
                print(f"   Client ID: {zoho_config['client_id'][:10]}...")
                print(f"   Client Secret: {'*' * len(zoho_config['client_secret'])}")
                return zoho_config['client_id'], zoho_config['client_secret']
                
        except Exception as e:
            print(f"⚠️ Could not load from config: {e}")
    
    # Fall back to user input if not found in config
    print("\n🔑 Zoho Client Credentials")
    print("You can find these in your Zoho API Console:")
    print("- EU: https://api-console.zoho.eu")
    print("- US: https://api-console.zoho.com")
    print("- India: https://api-console.zoho.in")
    print("- Australia: https://api-console.zoho.com.au")
    print("\nGo to your 'Self Client' application to find these values.\n")
    
    client_id = input("Enter your Zoho Client ID: ").strip()
    if not client_id:
        print("❌ Client ID is required!")
        sys.exit(1)
        
    client_secret = input("Enter your Zoho Client Secret: ").strip()
    if not client_secret:
        print("❌ Client Secret is required!")
        sys.exit(1)
    
    return client_id, client_secret

def generate_authorization_url(data_center="eu", client_id=None, redirect_uri="http://localhost"):
    """Generate the Zoho CRM authorization URL."""
    
    # Data center URL mapping
    auth_urls = {
        "eu": "https://accounts.zoho.eu/oauth/v2/auth",
        "com": "https://accounts.zoho.com/oauth/v2/auth", 
        "in": "https://accounts.zoho.in/oauth/v2/auth",
        "com.au": "https://accounts.zoho.com.au/oauth/v2/auth"
    }
    
    if data_center not in auth_urls:
        raise ValueError(f"Unsupported data center: {data_center}")
    
    base_url = auth_urls[data_center]
    
    # Required scopes for email CRM sync - comprehensive list
    scopes = [
        "ZohoCRM.modules.ALL",        # Access to all CRM modules
        "ZohoCRM.coql.READ",          # COQL queries (critical for advanced search)
        "ZohoCRM.search.READ",        # Advanced search operations
        "ZohoCRM.settings.READ",      # Read organization settings  
        "ZohoCRM.org.READ",          # Read organization info
        "ZohoCRM.users.READ",        # Read user info
        "ZohoCRM.modules.notes.ALL"   # Full notes access
    ]
    
    params = {
        "scope": ",".join(scopes),
        "client_id": client_id,
        "response_type": "code",
        "access_type": "offline",     # Required for refresh token
        "redirect_uri": redirect_uri
    }
    
    auth_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    return auth_url

def save_credentials_for_next_step(data_center, client_id, client_secret):
    """Save credentials to a temporary file for the token exchange script."""
    temp_file = project_root / "temp_zoho_credentials.py"
    
    content = f'''# Temporary credentials for token exchange
# This file will be deleted after token generation
DATA_CENTER = "{data_center}"
CLIENT_ID = "{client_id}"
CLIENT_SECRET = "{client_secret}"
REDIRECT_URI = "http://localhost"
'''
    
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Saved credentials to {temp_file}")
    print("   This file will be automatically deleted after token generation.")

def main():
    """Main function to generate authorization URL."""
    print("🚀 Zoho CRM OAuth2 Authorization URL Generator")
    print("=" * 50)
    
    # Step 1: Detect or ask for data center
    data_center = detect_data_center()
    
    # Step 2: Get client credentials
    client_id, client_secret = get_client_credentials()
    
    # Step 3: Generate authorization URL
    try:
        auth_url = generate_authorization_url(
            data_center=data_center,
            client_id=client_id
        )
        
        # Step 4: Save credentials for next script
        save_credentials_for_next_step(data_center, client_id, client_secret)
        
        # Step 5: Display instructions
        print("\n" + "=" * 70)
        print("📋 INSTRUCTIONS")
        print("=" * 70)
        print("1. Copy the URL below and paste it into your web browser")
        print("2. Log in to your Zoho account if prompted")
        print("3. Click 'Accept' to authorize the application")
        print("4. After authorization, you'll be redirected to a localhost URL")
        print("5. Copy the 'code' parameter from the redirected URL")
        print("   Example: http://localhost?code=1000.abc123...")
        print("6. Run the next script to exchange the code for tokens:")
        print("   python scripts/exchange_zoho_tokens.py")
        print("\n" + "🔗 AUTHORIZATION URL:")
        print(auth_url)
        print("\n" + "=" * 70)
        
    except (ValueError, KeyError) as e:
        print(f"❌ Error generating authorization URL: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
