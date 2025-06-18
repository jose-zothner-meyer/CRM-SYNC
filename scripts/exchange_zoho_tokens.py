#!/usr/bin/env python3
"""
Zoho CRM OAuth2 Token Exchange Script

This script exchanges an authorization code for access and refresh tokens,
then updates your configuration file with the new tokens.

Usage:
    python scripts/exchange_zoho_tokens.py
    
Prerequisites:
    Run scripts/generate_zoho_oauth_url.py first to generate the authorization URL
    and obtain an authorization code.
"""

import sys
import json
import requests
import yaml
from pathlib import Path
from datetime import datetime, timedelta

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def load_temp_credentials():
    """Load temporary credentials saved by the URL generator script."""
    temp_file = project_root / "temp_zoho_credentials.py"
    
    if not temp_file.exists():
        print("❌ Temporary credentials file not found!")
        print("   Please run 'python scripts/generate_zoho_oauth_url.py' first.")
        sys.exit(1)
    
    # Parse the temporary credentials file manually for security
    credentials = {}
    with open(temp_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('DATA_CENTER = '):
                credentials['data_center'] = line.split('"')[1]
            elif line.startswith('CLIENT_ID = '):
                credentials['client_id'] = line.split('"')[1]
            elif line.startswith('CLIENT_SECRET = '):
                credentials['client_secret'] = line.split('"')[1]
            elif line.startswith('REDIRECT_URI = '):
                credentials['redirect_uri'] = line.split('"')[1]
    
    required_keys = ['data_center', 'client_id', 'client_secret', 'redirect_uri']
    missing = [key for key in required_keys if key not in credentials]
    if missing:
        raise ValueError(f"Missing credentials in temp file: {missing}")
    
    return credentials

def get_authorization_code():
    """Get the authorization code from user input."""
    print("📋 Authorization Code")
    print("After visiting the authorization URL and accepting the permissions,")
    print("you should have been redirected to a localhost URL with a 'code' parameter.")
    print("Example: http://localhost?code=1000.abc123...")
    print()
    
    while True:
        auth_code = input("Enter the authorization code: ").strip()
        if not auth_code:
            print("❌ Authorization code cannot be empty!")
            continue
        
        # Basic validation - Zoho codes typically start with "1000."
        if not auth_code.startswith("1000."):
            print("⚠️  Warning: Zoho authorization codes typically start with '1000.'")
            confirm = input("Are you sure this is correct? (y/n): ").strip().lower()
            if confirm != 'y':
                continue
        
        return auth_code

def exchange_code_for_tokens(credentials, auth_code):
    """Exchange authorization code for access and refresh tokens."""
    
    # Data center URL mapping
    token_urls = {
        "eu": "https://accounts.zoho.eu/oauth/v2/token",
        "com": "https://accounts.zoho.com/oauth/v2/token",
        "in": "https://accounts.zoho.in/oauth/v2/token",
        "com.au": "https://accounts.zoho.com.au/oauth/v2/token"
    }
    
    data_center = credentials['data_center']
    if data_center not in token_urls:
        raise ValueError(f"Unsupported data center: {data_center}")
    
    token_endpoint = token_urls[data_center]
    
    payload = {
        "code": auth_code,
        "client_id": credentials['client_id'],
        "client_secret": credentials['client_secret'],
        "redirect_uri": credentials['redirect_uri'],
        "grant_type": "authorization_code"
    }
    
    print("🔄 Exchanging authorization code for tokens...")
    
    try:
        response = requests.post(token_endpoint, data=payload, timeout=30)
        response.raise_for_status()
        
        token_data = response.json()
        
        if 'access_token' not in token_data:
            print("❌ Token exchange failed!")
            print(f"Response: {json.dumps(token_data, indent=2)}")
            return None
        
        print("✅ Successfully obtained tokens!")
        return token_data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error during token exchange: {e}")
        if hasattr(e, 'response') and e.response:
            try:
                error_data = e.response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except json.JSONDecodeError:
                print(f"Error response: {e.response.text}")
        return None

def update_config_file(credentials, token_data):
    """Update the configuration file with new OAuth2 tokens."""
    
    config_file = project_root / "email_crm_sync" / "config" / "api_keys.yaml"
    
    if not config_file.exists():
        print(f"❌ Configuration file not found: {config_file}")
        return False
    
    # Load existing configuration
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f) or {}
    
    # Calculate token expiration time
    expires_in = token_data.get('expires_in', 3600)  # Default 1 hour
    expires_at = datetime.now() + timedelta(seconds=expires_in)
    
    # Update with OAuth2 tokens and credentials
    config.update({
        'zoho_client_id': credentials['client_id'],
        'zoho_client_secret': credentials['client_secret'],
        'zoho_access_token': token_data['access_token'],
        'zoho_refresh_token': token_data.get('refresh_token', ''),
        'zoho_token_expires_at': expires_at.isoformat(),
        'zoho_data_center': credentials['data_center']
    })
    
    # Remove old simple token field if present
    config.pop('zoho_access_token_simple', None)
    
    # Write back to file
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    print(f"✅ Updated configuration file: {config_file}")
    return True

def cleanup_temp_files():
    """Remove temporary credential files."""
    temp_file = project_root / "temp_zoho_credentials.py"
    if temp_file.exists():
        temp_file.unlink()
        print("✅ Cleaned up temporary files")

def test_token(token_data, data_center):
    """Test the new access token by making a simple API call."""
    
    api_urls = {
        "eu": "https://www.zohoapis.eu/crm/v8",
        "com": "https://www.zohoapis.com/crm/v8",
        "in": "https://www.zohoapis.in/crm/v8", 
        "com.au": "https://www.zohoapis.com.au/crm/v8"
    }
    
    if data_center not in api_urls:
        print(f"⚠️  Cannot test token - unsupported data center: {data_center}")
        return
    
    base_url = api_urls[data_center]
    test_url = f"{base_url}/org"
    
    headers = {
        'Authorization': f'Zoho-oauthtoken {token_data["access_token"]}',
        'Content-Type': 'application/json'
    }
    
    print("🧪 Testing new access token...")
    
    try:
        response = requests.get(test_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        org_data = response.json()
        org_name = org_data.get('org', [{}])[0].get('company_name', 'Unknown')
        
        print(f"✅ Token test successful! Connected to: {org_name}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Token test failed: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response status: {e.response.status_code}")
            try:
                error_data = e.response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except json.JSONDecodeError:
                print(f"Response text: {e.response.text}")
        return False

def main():
    """Main function to exchange tokens and update configuration."""
    print("🔐 Zoho CRM OAuth2 Token Exchange")
    print("=" * 50)
    
    try:
        # Step 1: Load temporary credentials
        credentials = load_temp_credentials()
        print(f"✅ Loaded credentials for {credentials['data_center']} data center")
        
        # Step 2: Get authorization code from user
        auth_code = get_authorization_code()
        
        # Step 3: Exchange code for tokens
        token_data = exchange_code_for_tokens(credentials, auth_code)
        if not token_data:
            sys.exit(1)
        
        # Step 4: Test the new token
        if test_token(token_data, credentials['data_center']):
            # Step 5: Update configuration file
            if update_config_file(credentials, token_data):
                print("\n" + "=" * 50)
                print("🎉 OAuth2 Setup Complete!")
                print("=" * 50)
                print("Your Zoho CRM API is now configured with OAuth2 tokens.")
                print("The access token will be automatically refreshed when needed.")
                print("\nToken details:")
                print(f"  • Access Token: {token_data['access_token'][:20]}...")
                if token_data.get('refresh_token'):
                    print(f"  • Refresh Token: {token_data['refresh_token'][:20]}...")
                print(f"  • Data Center: {credentials['data_center']}")
                print(f"  • Expires: ~{token_data.get('expires_in', 3600)} seconds")
                print("\nYou can now run: python main.py --mode once")
            else:
                print("❌ Failed to update configuration file")
                sys.exit(1)
        else:
            print("❌ Token test failed - please check your setup")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled by user")
        sys.exit(1)
    except (ValueError, KeyError, FileNotFoundError) as e:
        print(f"❌ Setup error: {e}")
        sys.exit(1)
    finally:
        # Always cleanup temp files
        cleanup_temp_files()

if __name__ == "__main__":
    main()
