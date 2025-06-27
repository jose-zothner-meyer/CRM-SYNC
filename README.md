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

### Configuration Management

The application uses a **centralized configuration system** that ensures consistent settings across all components:

```python
# Import centralized configuration (recommended)
from email_crm_sync.config import config

# Access configuration values directly
openai_key = config.openai_key
zoho_token = config.zoho_token
zoho_config = config.get_zoho_config()
```

**Benefits:**
- ✅ Configuration loaded only once (better performance)
- ✅ Consistent settings across all modules
- ✅ Singleton pattern prevents duplicate instances
- ✅ Thread-safe configuration access

### Configuration File

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

## 📖 Documentation

- **[Complete Setup Guide](docs/SETUP_GUIDE.md)** - Detailed setup instructions
- **[Project Structure](docs/PROJECT_STRUCTURE.md)** - Architecture overview
- **[Enhanced OpenAI Client](docs/ENHANCED_OPENAI_CLIENT.md)** - AI processing documentation

## 📚 Resources & Documentation

### 🔗 Zoho CRM API Documentation

- **[Zoho CRM API v8 Overview](https://www.zoho.com/crm/developer/docs/api-directory.html)** - Complete API directory
- **[API Console (EU)](https://api-console.zoho.eu)** - Developer console for EU data center
- **[API Console (US)](https://api-console.zoho.com)** - Developer console for US data center
- **[Authentication & Scopes](https://www.zoho.com/crm/developer/docs/api/v8/scopes.html)** - OAuth scopes reference
- **[OAuth 2.0 Setup Guide](https://www.zoho.com/crm/developer/docs/api/v8/oauth-overview.html)** - Complete OAuth setup
- **[Modules API](https://www.zoho.com/crm/developer/docs/api/v8/modules-api.html)** - Properties/Developments management
- **[COQL Query API](https://www.zoho.com/crm/developer/docs/api/v8/Get-Records-through-COQL-Query.html)** - Advanced search queries
- **[Get Notes API](https://www.zoho.com/crm/developer/docs/api/v8/get-notes.html)** - Retrieve record notes
- **[Create Note API](https://www.zoho.com/crm/developer/docs/api/v8/create-notes.html)** - Add notes to records
- **[Attachments API](https://www.zoho.com/crm/developer/docs/api/v8/upload-attachment.html)** - File attachments
- **[Data Centers & Domains](https://www.zoho.com/crm/developer/docs/api/v8/multi-dc.html)** - Multi-region support

### 📧 Gmail API Documentation

- **[Gmail API Overview](https://developers.google.com/gmail/api/guides)** - Complete Gmail API guide
- **[Google Cloud Console](https://console.cloud.google.com/)** - Project and credentials management
- **[Authentication & OAuth 2.0](https://developers.google.com/gmail/api/auth/web-server)** - OAuth setup for Gmail
- **[Messages API](https://developers.google.com/gmail/api/reference/rest/v1/users.messages)** - Email messages reference
- **[Labels API](https://developers.google.com/gmail/api/reference/rest/v1/users.labels)** - Gmail labels management
- **[Gmail API Python Client](https://github.com/googleapis/google-api-python-client)** - Official Python library
- **[Enable Gmail API](https://console.cloud.google.com/apis/library/gmail.googleapis.com)** - Enable API in project
- **[OAuth Consent Screen](https://console.cloud.google.com/apis/credentials/consent)** - Configure consent screen
- **[Scopes Reference](https://developers.google.com/gmail/api/auth/scopes)** - Gmail API scopes

### 🤖 OpenAI API Documentation

- **[OpenAI API Overview](https://platform.openai.com/docs/api-reference)** - Complete API reference
- **[Chat Completions](https://platform.openai.com/docs/api-reference/chat)** - Chat API for email analysis
- **[Authentication](https://platform.openai.com/docs/api-reference/authentication)** - API key authentication
- **[Models Documentation](https://platform.openai.com/docs/models)** - Available AI models
- **[Rate Limits](https://platform.openai.com/docs/guides/rate-limits)** - Usage limits and optimization
- **[Best Practices](https://platform.openai.com/docs/guides/production-best-practices)** - Production deployment
- **[API Keys Management](https://platform.openai.com/api-keys)** - Manage your API keys
- **[Usage Dashboard](https://platform.openai.com/usage)** - Monitor API usage

### 🐍 Python Libraries Used

- **[Google API Python Client](https://github.com/googleapis/google-api-python-client)** - Official Google APIs client
- **[OpenAI Python Library](https://github.com/openai/openai-python)** - Official OpenAI client
- **[Requests](https://docs.python-requests.org/)** - HTTP library for API calls
- **[PyYAML](https://pyyaml.org/wiki/PyYAMLDocumentation)** - YAML configuration parsing
- **[Python Email Utils](https://docs.python.org/3/library/email.html)** - Built-in email processing

### 📖 Setup Guides & Tutorials

- **[Zoho CRM Custom Module Setup](docs/ZOHO_SETUP_GUIDE.md)** - Detailed Zoho configuration
- **[Complete Setup Guide](docs/SETUP_GUIDE.md)** - End-to-end system setup
- **[Gmail API Python Quickstart](https://developers.google.com/gmail/api/quickstart/python)** - Official Gmail setup
- **[OpenAI API Getting Started](https://platform.openai.com/docs/quickstart)** - OpenAI API basics
- **[OAuth 2.0 for Web Applications](https://developers.google.com/identity/protocols/oauth2/web-server)** - OAuth implementation

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Important Notes

### Security Considerations
- **Never commit API keys** to version control
- **Use environment variables** for production deployments
- **Regularly rotate API keys** for security
- **Review OAuth scopes** periodically

### API Limits & Quotas
- **Gmail API**: 1 billion quota units per day
- **OpenAI API**: Varies by tier and model
- **Zoho CRM API**: 5,000 credits per day (sandbox), varies by plan

### Production Deployment
- Monitor email processing volumes
- Set up proper logging and alerting
- Configure automatic token refresh
- Implement proper error handling and retry logic

## 📞 Support

- **Documentation**: [docs/](docs/) directory contains comprehensive guides
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Setup Help**: Follow [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) for detailed instructions

---

**Status**: Production Ready ✅  
**Last Updated**: June 2025

## 🔧 Refactored Architecture (New Features)

### Enhanced Main Application
The project now includes a refactored version with improved architecture:

```bash
# Use the refactored main application
python main_refactored.py run --mode once           # Process emails once
python main_refactored.py run --mode monitor        # Monitor continuously  
python main_refactored.py token refresh             # Refresh expired tokens
python main_refactored.py token exchange --code "..." # Exchange auth code
python main_refactored.py health                    # Run health checks
python main_refactored.py discover                  # Discover Zoho modules
```

### Key Improvements in Refactored Version:
- **Centralized Configuration**: Single configuration instance shared across the application
- **Custom Exceptions**: Application-specific exception handling for better debugging
- **Modular Zoho Client**: Separated into focused components (Notes, Search)
- **Enhanced CLI**: Consolidated command-line interface for all operations
- **Better Error Handling**: Specific exception types instead of generic catches

### Architecture Components:
- `email_crm_sync/config/__init__.py` - Centralized configuration management
- `email_crm_sync/exceptions.py` - Custom exception definitions
- `email_crm_sync/services/base_processor.py` - Abstract base for processors
- `email_crm_sync/clients/zoho/` - Modular Zoho client components
- `main_refactored.py` - Enhanced main application with CLI

## 🏗️ Refactored Architecture

### Modular Zoho Client

The Zoho CRM client has been refactored into focused modular components for better maintainability and extensibility:

```python
from email_crm_sync.clients.zoho_v8_enhanced_client import ZohoV8EnhancedClient
from email_crm_sync.config import config

# Initialize client with modular components
client = ZohoV8EnhancedClient(
    access_token=config.zoho_token,
    data_center=config.zoho_data_center,
    developments_module=config.zoho_developments_module
)

# Use focused components
client.notes.create(parent_id, content, title)        # Note operations
client.search.by_email("test@example.com")            # Search operations
client.modules.discover()                             # Module discovery
client.records.get("record_id")                       # Record operations
client.developments.find_by_address("123 Main St")    # Development-specific
```

### Component Architecture

```
ZohoV8EnhancedClient (Main)
├── 📝 Notes      - Note creation, retrieval, updates
├── 🔍 Search     - Email, word, criteria, COQL queries
├── 📦 Modules    - Module discovery and metadata
├── 📋 Records    - Basic CRUD operations
└── 🏠 Developments - Domain-specific operations
```

**Benefits:**
- ✅ **Single Responsibility** - Each component has one clear purpose
- ✅ **Better Testing** - Components can be tested independently
- ✅ **Easier Maintenance** - Bugs are isolated to specific components
- ✅ **Backward Compatible** - Existing code continues to work
- ✅ **Performance** - Shared resources with intelligent caching

### Migration Examples

```python
# Old way (still works)
client.create_note(parent_id, content, title)
client.discover_modules()
client.find_development_by_email("test@example.com")

# New way (recommended)
client.notes.create(parent_id, content, title)
client.modules.discover()
client.developments.find_by_email("test@example.com")
```

See `docs/ZOHO_CLIENT_REFACTORING.md` for detailed documentation.