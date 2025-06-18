#!/usr/bin/env python3
"""
Gmail API Setup Verification Script
Run this to test your Gmail credentials
"""

import json
import os
from pathlib import Path

def verify_gmail_credentials():
    """Verify Gmail credentials file is properly configured."""
    
    creds_path = Path("email_crm_sync/config/gmail_credentials.json")
    
    if not creds_path.exists():
        print("❌ gmail_credentials.json file not found!")
        print("Please download the credentials file from Google Cloud Console")
        print(f"Expected location: {creds_path}")
        return False
    
    try:
        with open(creds_path, 'r') as f:
            creds = json.load(f)
        
        # Check if it's the correct format
        if 'installed' not in creds:
            print("❌ Invalid credentials format!")
            print("Make sure you downloaded the file for 'Desktop Application'")
            return False
        
        installed = creds['installed']
        required_fields = ['client_id', 'client_secret', 'auth_uri', 'token_uri']
        
        missing_fields = []
        for field in required_fields:
            if field not in installed or installed[field] == f"your-{field.replace('_', '-')}-here":
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing or incomplete fields: {', '.join(missing_fields)}")
            print("Please download the complete credentials file from Google Cloud Console")
            return False
        
        print("✅ Gmail credentials file looks good!")
        print(f"   Client ID: {installed['client_id'][:50]}...")
        print(f"   Project ID: {installed.get('project_id', 'Not specified')}")
        
        return True
        
    except json.JSONDecodeError:
        print("❌ Invalid JSON format in credentials file!")
        return False
    except Exception as e:
        print(f"❌ Error reading credentials: {e}")
        return False

def test_gmail_connection():
    """Test Gmail API connection."""
    try:
        from email_crm_sync.clients.gmail_client import GmailClient
        
        print("\n🔄 Testing Gmail API connection...")
        
        client = GmailClient("email_crm_sync/config/gmail_credentials.json")
        
        # Try to get starred emails (this will trigger OAuth flow)
        emails = client.get_starred_emails(max_results=1)
        
        print(f"✅ Successfully connected! Found {len(emails)} starred emails")
        return True
        
    except ImportError:
        print("❌ Gmail client not found. Make sure the project is set up correctly.")
        return False
    except Exception as e:
        print(f"❌ Gmail connection failed: {e}")
        print("\nThis might be normal for first-time setup - you may need to authorize the app")
        return False

if __name__ == "__main__":
    print("🔍 Gmail API Setup Verification")
    print("=" * 40)
    
    # Verify credentials file
    if verify_gmail_credentials():
        # Test connection
        test_gmail_connection()
    
    print("\n📋 Next Steps:")
    print("1. If credentials are missing, download the complete JSON file from Google Cloud Console")
    print("2. If connection fails, run 'python main.py' to complete OAuth authorization")
    print("3. Make sure you have some starred emails in Gmail for testing")
