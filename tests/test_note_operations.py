#!/usr/bin/env python3
"""
Test note creation and operations in Zoho CRM.
"""

import sys
import os
import yaml
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from email_crm_sync.clients.zoho_v8_enhanced_client import ZohoV8EnhancedClient

def load_config():
    """Load configuration from YAML file."""
    config_path = "email_crm_sync/config/api_keys.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def test_note_creation():
    """Test note creation and retrieval to debug visibility issues."""
    print("🧪 Testing Zoho CRM Note Creation")
    print("=" * 50)
    
    # Load configuration
    config = load_config()
    
    # Initialize Zoho client
    zoho = ZohoV8EnhancedClient(
        access_token=config['zoho_access_token'],
        data_center=config['zoho_data_center'],
        developments_module=config['zoho_developments_module']
    )
    
    print(f"✅ Connected to Zoho CRM ({config['zoho_data_center']})")
    print(f"📁 Using module: {config['zoho_developments_module']}")
    print()
    
    # Test 1: Get first account to create note for
    print("🔍 Finding a test account...")
    search_url = f"{zoho.base_url}/{config['zoho_developments_module']}/search"
    response = zoho.session.get(search_url, params={"per_page": 1}, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("data"):
            test_account = data["data"][0]
            account_id = test_account["id"]
            account_name = test_account.get("Account_Name", "Unknown")
            print(f"✅ Found test account: {account_name} (ID: {account_id})")
        else:
            print("❌ No accounts found!")
            return
    else:
        print(f"❌ Failed to get accounts: {response.status_code}")
        return
    
    print()
    
    # Test 2: Create a test note
    print("📝 Creating test note...")
    test_content = "This is a test note created by the email CRM sync system for debugging purposes."
    test_title = "Test Note - Debug Email Sync"
    
    result = zoho.create_note(
        parent_id=account_id,
        content=test_content,
        title=test_title,
        parent_module=config['zoho_developments_module']
    )
    
    if result.get("success"):
        note_id = result.get("note_id")
        print(f"✅ Note created successfully!")
        print(f"   Note ID: {note_id}")
        print(f"   Details: {result.get('details', {})}")
    else:
        print(f"❌ Note creation failed: {result.get('error')}")
        return
    
    print()
    
    # Test 3: Try to retrieve the note we just created
    print("📖 Retrieving notes for this account...")
    notes_result = zoho.get_notes(parent_id=account_id, parent_module=config['zoho_developments_module'])
    
    if notes_result.get("success"):
        notes = notes_result.get("notes", [])
        print(f"✅ Found {len(notes)} notes for this account:")
        for i, note in enumerate(notes[:5], 1):  # Show first 5 notes
            print(f"   {i}. {note.get('Note_Title', 'No Title')} (ID: {note.get('id')})")
            if note.get('id') == note_id:
                print("      ⭐ This is the note we just created!")
    else:
        print(f"❌ Failed to retrieve notes: {notes_result.get('error')}")
    
    print()
    
    # Test 4: Try to get all notes (admin access)
    print("📚 Attempting to get all notes (admin access)...")
    all_notes_result = zoho.get_notes()
    
    if all_notes_result.get("success"):
        all_notes = all_notes_result.get("notes", [])
        print(f"✅ Found {len(all_notes)} total notes in the system")
        # Look for our note
        our_note = next((n for n in all_notes if n.get('id') == note_id), None)
        if our_note:
            print(f"   ⭐ Found our test note in the global list!")
        else:
            print(f"   ⚠️ Our test note not found in global list")
    else:
        print(f"❌ Failed to get all notes: {all_notes_result.get('error')}")
    
    print()
    
    # Test 5: Check specific note by ID
    print(f"🔎 Getting specific note by ID: {note_id}")
    specific_note_result = zoho.get_notes(note_id=note_id)
    
    if specific_note_result.get("success"):
        notes = specific_note_result.get("notes", [])
        if notes:
            note = notes[0]
            print(f"✅ Retrieved note successfully!")
            print(f"   Title: {note.get('Note_Title')}")
            print(f"   Content: {note.get('Note_Content', '')[:100]}...")
            print(f"   Parent ID: {note.get('Parent_Id')}")
            print(f"   Module: {note.get('$se_module')}")
        else:
            print("❌ Note not found by ID")
    else:
        print(f"❌ Failed to get note by ID: {specific_note_result.get('error')}")
    
    print()
    print("🎯 DIAGNOSIS:")
    print("If notes are being created successfully but you can't see them in the CRM UI:")
    print("1. Notes might be created in a different module than expected")
    print("2. User permissions might restrict note visibility")
    print("3. Notes might be in a 'Notes' module rather than attached to accounts")
    print("4. UI filters might be hiding the notes")

if __name__ == "__main__":
    test_note_creation()
