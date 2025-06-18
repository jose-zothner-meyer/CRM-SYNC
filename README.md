# Email CRM Sync

A production-ready Python application that automatically processes emails from Gmail, uses OpenAI to extract property information, and creates notes in Zoho CRM. Simply star emails in Gmail and the system will process them into organized CRM notes.

## 🎯 What This Application Does

1. **📧 Monitors starred emails** in your Gmail account
2. **🤖 Uses AI** to extract property details and create summaries
3. **🔍 Matches emails** to existing properties in your Zoho CRM
4. **📝 Creates organized notes** in the CRM with email content and AI analysis
5. **📊 Tracks activity** and provides reports on which properties received emails

## 🚀 Quick Start (First Time Setup)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Set Up Your API Keys (One-time setup)
```bash
python scripts/setup_zoho_complete.py
```
This interactive script will guide you through:
- Setting up OpenAI API keys
- Configuring Zoho CRM access
- Setting up Gmail integration
- Testing all connections

### Step 3: Verify Everything Works
```bash
python -m pytest tests/ -v
```
Should show: **✅ All tests passing**

## 📱 Daily Usage (What You Actually Run)

### 🎯 Main Usage - Process Your Emails

**Star some emails in Gmail first**, then run:

```bash
# Process emails once (most common usage)
python main.py --mode once
```

**That's it!** The system will:
- Find all starred emails in Gmail
- Analyze them with AI 
- Match them to properties in your CRM
- Create detailed notes
- Show you a summary of what was processed

### 📊 Check What Happened - View Activity Report

```bash
# See which properties got emails in the last 7 days
python examples/demo_property_report.py

# Check different time periods by modifying the script
```

### 🔄 Continuous Monitoring (Optional)

If you want automatic processing:
```bash
# Monitor for new emails every 5 minutes
python main.py --mode monitor
```

Press `Ctrl+C` to stop monitoring.

## 🛠️ Maintenance Commands

### When Tokens Expire (Usually monthly)
```bash
python tools/refresh_token.py
```

### If You Need New Authorization Tokens
```bash
# Generate new OAuth URL
python scripts/generate_zoho_oauth_url.py

# Exchange authorization code for tokens (secure method)
python tools/exchange_new_tokens.py "your_auth_code_here"
```

### If Something Seems Broken
```bash
# Run diagnostics
python -m pytest tests/ -v

# Test specific components
python tests/test_authentication.py
python tests/test_client_initialization.py
```

## 📁 Key Files You Need to Know

### Files You'll Run Regularly:
- **`main.py`** - ⭐ **Main application** - processes your starred emails
- **`examples/demo_property_report.py`** - 📊 **View reports** of email activity

### Setup Files (Run Once):
- **`scripts/setup_zoho_complete.py`** - 🔧 **Initial setup** guide
- **`scripts/setup_api_tokens.py`** - 🔑 **API token setup**

### Maintenance Files (Run When Needed):
- **`tools/refresh_token.py`** - 🔄 **Fix token issues**
- **`tools/exchange_new_tokens.py`** - 🔐 **Exchange authorization codes securely**
- **`tools/discover_zoho_modules.py`** - 🔍 **Discover available Zoho modules**
- **`tests/`** - 🧪 **Test everything is working**

### Configuration Files (Edit as Needed):
- **`config/api_keys.yaml`** - 🔑 **Your API keys and settings**
- **`email_crm_sync/config/api_keys.yaml`** - 🔑 **Alternative config location**

## 📋 Typical Workflow

### Daily/Weekly Routine:
1. **Star emails** in Gmail that relate to your properties
2. **Run**: `python main.py --mode once`
3. **Check results** in the terminal output
4. **View activity**: `python examples/demo_property_report.py`

### Monthly Maintenance:
1. **Refresh tokens**: `python tools/refresh_token.py`
2. **Run tests**: `python -m pytest tests/ -v`

## 🎯 Real Examples

### Example 1: Process Today's Emails
```bash
# You starred 3 emails in Gmail about different properties
python main.py --mode once

# Output will show:
# ✅ Found 3 emails to process
# ✅ Email 1: Matched to "Glengall Rd, Southwark" - Note created
# ✅ Email 2: Matched to "71 Atheldene Rd" - Note created  
# ✅ Email 3: Created new property "New Development Site" - Note created
# 📊 Summary: 3 emails processed, 3 notes created
```

### Example 2: Check Available Modules
```bash
python tools/discover_zoho_modules.py

# Output will show:
# 🔍 Discovering Zoho CRM Modules...
# ✅ Found 67 modules:
# 📋 Accounts, Deals, Contacts, Leads...
# 🧪 Testing Module Access...
# ✅ Can access 'Accounts' - Found sample records
```

## 🆘 Troubleshooting

### "No emails found to process"
- ⭐ **Star some emails** in Gmail first
- Check you're logged into the right Gmail account

### "Invalid token" or "Authentication failed" 
```bash
python tools/refresh_token.py
```

### "Module not found" or import errors
```bash
# Make sure you're in the right directory
cd "/Users/jomeme/Documents/AiCore/CRM SYNC/CRM-SYNC"
pip install -r requirements.txt
```

### "INVALID_MODULE" or Zoho module errors
```bash
# Discover available modules
python tools/discover_zoho_modules.py

# Update your config with correct module name
```

### General "Something's broken"
```bash
# Run full diagnostics
python -m pytest tests/ -v

# Test specific functionality
python tests/run_complete_test.py
```

## 📚 Advanced Options

### Different Processing Modes:
```bash
# Process once (default)
python main.py --mode once

# Monitor continuously 
python main.py --mode monitor

# Monitor with custom interval (10 minutes)
python main.py --mode monitor --interval 600
```

### Token Management:
```bash
# Refresh expired tokens
python tools/refresh_token.py

# Exchange new authorization code (secure)
python tools/exchange_new_tokens.py "1000.your_auth_code.here"

# Or use environment variable
export ZOHO_AUTH_CODE="1000.your_auth_code.here"
python tools/exchange_new_tokens.py
```

### Advanced Configuration:
```bash
# Discover available Zoho modules
python tools/discover_zoho_modules.py

# Test API scopes and permissions
python tests/test_api_scopes.py

# Check authentication status
python tests/test_authentication.py
```

## 🔧 Configuration

Your main configuration file is:
**`config/api_keys.yaml`**

It contains:
- OpenAI API key
- Zoho CRM credentials and tokens
- Gmail settings
- Processing preferences
- Module configurations

**⚠️ Keep this file secure!** Never share it or commit it to version control.

Key settings:
- `zoho_developments_module`: Currently set to "Accounts"
- `zoho_data_center`: Set to "eu" 
- `gmail_query_starred`: Filter for starred emails
- `email_batch_size`: Number of emails to process at once

## ✅ You Know It's Working When...

- ✅ `python main.py --mode once` processes your starred emails
- ✅ You see notes created in your Zoho CRM
- ✅ `python examples/demo_property_report.py` shows recent activity
- ✅ `python -m pytest tests/ -v` shows tests passing
- ✅ `python tools/discover_zoho_modules.py` shows available modules

## 📝 Need Help?

1. **First**: Run `python -m pytest tests/ -v` to check system health
2. **Check**: Make sure you've starred emails in Gmail
3. **Try**: `python tools/refresh_token.py` if you get authentication errors
4. **Discover**: `python tools/discover_zoho_modules.py` to see available modules
5. **Review**: The terminal output usually explains what went wrong

---

**🎉 Ready to use!** Star some emails in Gmail and run `python main.py --mode once` to get started.

## 📋 Quick Reference Card

### 🎯 Daily Commands:
```bash
python main.py --mode once                           # Process starred emails
python examples/demo_property_report.py             # View recent activity
```

### 🔧 Setup Commands (Run Once):
```bash
pip install -r requirements.txt                     # Install dependencies
python scripts/setup_zoho_complete.py              # Interactive setup
```

### 🛠️ Maintenance Commands:
```bash
python tools/refresh_token.py                       # Fix token issues
python tools/discover_zoho_modules.py              # Discover available modules
python -m pytest tests/ -v                          # Check system health
```

### 🔐 Security Commands:
```bash
python tools/exchange_new_tokens.py "auth_code"     # Exchange authorization code securely
python scripts/generate_zoho_oauth_url.py          # Generate new OAuth URL
```

### 📊 Reporting Commands:
```bash
python examples/demo_property_report.py            # View property activity
python tests/run_complete_test.py                  # Run comprehensive tests
```

### 🔄 Monitoring Commands:
```bash
python main.py --mode monitor                       # Continuous monitoring
python main.py --mode monitor --interval 600        # Check every 10 minutes
```

**📍 Location**: `/Users/jomeme/Documents/AiCore/CRM SYNC/CRM-SYNC/`

## 📁 Project Structure

```
CRM-SYNC/
├── 📄 main.py                               # 🎯 MAIN FILE - Run this to process emails
├── 📄 requirements.txt                      # Python dependencies
├── 📄 Makefile                              # Build and development commands
├── 📂 email_crm_sync/                       # Core application package
│   ├── 📂 clients/                          # API connections
│   │   ├── gmail_client.py                  # Gmail integration
│   │   ├── openai_client.py                 # OpenAI integration
│   │   ├── zoho_client_factory.py           # Zoho client factory
│   │   └── zoho_v8_enhanced_client.py       # Enhanced Zoho client
│   ├── 📂 config/                           
│   │   ├── api_keys.yaml                    # 🔑 Package config location
│   │   └── loader.py                        # Configuration loader
│   ├── 📂 services/                         # Email processing logic
│   │   └── enhanced_processor.py            # Main processing service
│   └── 📂 utils/                            # Helper functions
│       └── email_utils.py                   # Email utility functions
├── 📂 config/                               # 🔑 Main configuration directory
│   └── api_keys.yaml                        # 🔑 Your API keys (keep secure!)
├── 📂 scripts/                              # 🚀 Setup and utility scripts
│   ├── setup_zoho_complete.py               # 🔧 Complete Zoho setup
│   ├── setup_api_tokens.py                  # 🔑 API token setup
│   ├── generate_zoho_oauth_url.py           # 🔗 Generate OAuth URLs
│   ├── exchange_zoho_tokens.py              # 🔄 Token exchange
│   └── verify_gmail_setup.py                # ✅ Gmail verification
├── 📂 tools/                                # 🛠️ Maintenance tools
│   ├── refresh_token.py                     # 🔄 Refresh expired tokens
│   ├── exchange_new_tokens.py               # 🔐 Secure token exchange
│   └── discover_zoho_modules.py             # 🔍 Module discovery
├── 📂 tests/                                # 🧪 System health checks
│   ├── run_complete_test.py                 # 🧪 Comprehensive testing
│   ├── test_authentication.py               # 🔐 Auth testing
│   ├── test_client_initialization.py        # 🚀 Client testing
│   └── [other test files]                   # Various component tests
├── 📂 examples/                             # 📊 Example scripts and configs
│   ├── demo_property_report.py              # 📊 Property activity report
│   └── api_keys.yaml.example                # 📝 Configuration template
└── 📂 docs/                                 # 📚 Documentation
    ├── SECURITY_IMPROVEMENTS.md             # 🔒 Security documentation
    ├── IMPORT_ANALYSIS.md                   # 🔍 Import analysis
    └── [other documentation]                # Additional docs
```

## ⚡ Features

- 🔄 **Simple workflow**: Star emails → Run command → Get CRM notes
- 🤖 **AI-powered analysis**: OpenAI extracts property details automatically
- 🔍 **Smart matching**: Finds the right property in your CRM
- 📝 **Guaranteed notes**: Creates notes even if property matching fails
- 📊 **Activity tracking**: See which properties are getting emails
- 🛡️ **Production-ready**: Robust error handling and recovery
- 🔐 **Secure token management**: Safe handling of authorization codes
- 🔍 **Module discovery**: Automatically discover available Zoho modules

## 🔒 Security Features

- **No hard-coded credentials**: All sensitive data in config files
- **Automatic token refresh**: Handles expired tokens automatically
- **Secure authorization code handling**: Multiple secure input methods
- **Config file validation**: Ensures proper configuration setup
- **Comprehensive testing**: Full test suite for reliability
