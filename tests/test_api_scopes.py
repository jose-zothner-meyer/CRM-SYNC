#!/usr/bin/env python3
"""
Check required Zoho CRM v8 API scopes for COQL and other operations.
Based on Zoho CRM API v8 documentation.
"""

def check_zoho_scopes():
    """Check what scopes are required for different Zoho CRM v8 operations."""
    
    print("🔍 Zoho CRM v8 API Required Scopes Analysis")
    print("=" * 60)
    print()
    
    # Based on Zoho CRM v8 API documentation
    scope_requirements = {
        "Basic Module Operations": [
            "ZohoCRM.modules.READ",     # Read records from modules
            "ZohoCRM.modules.CREATE",   # Create records
            "ZohoCRM.modules.UPDATE",   # Update records
            "ZohoCRM.modules.DELETE"    # Delete records (if needed)
        ],
        
        "Advanced Search (COQL)": [
            "ZohoCRM.coql.READ",        # COQL queries (this is crucial!)
            "ZohoCRM.modules.READ"      # Also needs module read access
        ],
        
        "Notes Operations": [
            "ZohoCRM.modules.notes.READ",   # Read notes
            "ZohoCRM.modules.notes.CREATE", # Create notes
            "ZohoCRM.modules.notes.UPDATE"  # Update notes
        ],
        
        "Organization & Settings": [
            "ZohoCRM.settings.READ",    # Read org settings
            "ZohoCRM.org.READ",        # Read org info
            "ZohoCRM.users.READ"       # Read user info
        ],
        
        "Search Operations": [
            "ZohoCRM.modules.READ",     # Basic search
            "ZohoCRM.search.READ"       # Advanced search
        ]
    }
    
    print("📋 Current scopes we're using:")
    current_scopes = [
        "ZohoCRM.modules.ALL",
        "ZohoCRM.settings.READ", 
        "ZohoCRM.org.READ",
        "ZohoCRM.users.READ"
    ]
    
    for scope in current_scopes:
        print(f"   ✅ {scope}")
    
    print()
    print("🎯 Recommended scopes for full functionality:")
    
    all_needed_scopes = set()
    
    for category, scopes in scope_requirements.items():
        print(f"\n{category}:")
        for scope in scopes:
            print(f"   • {scope}")
            all_needed_scopes.add(scope)
    
    print()
    print("🔧 Complete scope list needed:")
    recommended_scopes = sorted(list(all_needed_scopes))
    
    for scope in recommended_scopes:
        is_covered = any(scope in current or "ALL" in current for current in current_scopes)
        status = "✅" if is_covered else "❌ MISSING"
        print(f"   {status} {scope}")
    
    print()
    print("🚨 LIKELY ISSUES:")
    missing_scopes = []
    
    # Check for specific missing scopes that could cause our errors
    critical_scopes = [
        "ZohoCRM.coql.READ",           # For COQL queries
        "ZohoCRM.modules.notes.CREATE", # For creating notes
        "ZohoCRM.search.READ"          # For advanced search
    ]
    
    for scope in critical_scopes:
        is_covered = any(scope in current or "ALL" in current for current in current_scopes)
        if not is_covered:
            missing_scopes.append(scope)
            print(f"   ❌ Missing: {scope}")
    
    if missing_scopes:
        print()
        print("💡 SOLUTION:")
        print("   The 'ZohoCRM.modules.ALL' scope might not include COQL and advanced features.")
        print("   You may need to explicitly request these scopes:")
        print()
        
        updated_scopes = current_scopes + [scope for scope in missing_scopes if scope not in current_scopes]
        for scope in updated_scopes:
            print(f"      {scope}")
    else:
        print("   ✅ All critical scopes appear to be covered by ZohoCRM.modules.ALL")

if __name__ == "__main__":
    check_zoho_scopes()
