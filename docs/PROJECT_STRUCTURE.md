# Project Structure Guide

## 📁 Directory Organization

The Email CRM Sync project follows Python best practices with a clean, modular structure:

```
email_crm_sync/
├── 📄 main.py                          # Main application entry point
├── 📄 requirements.txt                 # Python dependencies
├── 📄 Makefile                         # Common development commands
├── 📄 README.md                        # Quick start guide
├── 📄 .gitignore                       # Git ignore patterns
├── 📄 .env.example                     # Environment variables template
│
├── 📂 email_crm_sync/                  # 🎯 Core application package
│   ├── 📄 __init__.py                  
│   ├── 📂 clients/                     # External API integrations
│   │   ├── 📄 __init__.py
│   │   ├── 📄 gmail_client.py          # Gmail API wrapper
│   │   ├── 📄 openai_client.py         # OpenAI API wrapper
│   │   ├── 📄 simple_gmail_client.py   # Simplified Gmail client
│   │   ├── 📄 zoho_client_factory.py   # Zoho client factory
│   │   ├── 📄 zoho_eu_enhanced_client.py # Zoho EU enhanced client
│   │   └── 📄 zoho_v8_enhanced_client.py # Zoho V8 enhanced client (recommended)
│   ├── 📂 config/                      # Configuration management
│   │   ├── 📄 __init__.py
│   │   ├── 📄 api_keys.yaml            # Your API configuration
│   │   ├── 📄 api_keys.yaml.example    # Configuration template
│   │   └── 📄 loader.py                # Config file and env var loader
│   ├── 📂 services/                    # Business logic
│   │   ├── 📄 __init__.py
│   │   └── 📄 processor.py             # Main email processing workflow
│   └── 📂 utils/                       # Helper utilities
│       ├── 📄 __init__.py
│       └── 📄 email_utils.py           # Email parsing utilities
│
├── 📂 scripts/                         # 🛠️ Setup and maintenance scripts
│   ├── 📄 __init__.py
│   ├── 📄 setup_zoho_complete.py       # Complete Zoho CRM setup guide
│   ├── 📄 generate_zoho_oauth_url.py   # OAuth2 authorization URL generator
│   ├── 📄 exchange_zoho_tokens.py      # OAuth2 token exchange
│   ├── 📄 verify_gmail_setup.py        # Gmail setup verification
│   └── 📄 setup_api_tokens.py          # API tokens setup utility
│
├── 📂 tools/                          # 🔧 Development and diagnostic tools
│   ├── 📄 __init__.py
│   ├── 📄 discover_zoho_modules.py     # Zoho CRM module discovery
│   ├── 📄 exchange_new_tokens.py       # Token exchange utility
│   └── 📄 refresh_token.py             # Token refresh utility
│
├── 📂 tests/                          # 🧪 Comprehensive testing suite
│   ├── 📄 __init__.py
│   ├── 📄 run_complete_test.py         # Complete system test suite
│   ├── 📄 test_api_scopes.py           # API scopes testing
│   ├── 📄 test_authentication.py       # Authentication testing
│   ├── 📄 test_client_initialization.py # Client initialization testing
│   ├── 📄 test_developments_module.py  # Developments module specific tests
│   ├── � test_enhanced_openai.py      # Enhanced OpenAI client testing
│   ├── 📄 test_note_operations.py      # Note operations testing
│   ├── 📄 test_search_diagnostics.py   # Search diagnostics testing
│   ├── 📄 test_search_functionality.py # Search functionality testing
│   ├── 📄 test_token.py                # Token management testing
│   └── 📄 test_v8_enhanced_client.py   # V8 enhanced client testing
│
├── 📂 examples/                       # 📋 Example configurations and templates
│   └── 📄 api_keys.yaml.example        # Configuration template
│
└── 📂 docs/                          # 📚 Documentation
    ├── 📄 README.md                    # Detailed documentation
    ├── 📄 SETUP_GUIDE.md               # Quick setup guide
    ├── 📄 PROJECT_STRUCTURE.md         # This structure guide
    ├── 📄 ZOHO_SETUP_GUIDE.md         # Zoho CRM setup guide
    ├── 📄 ENHANCED_OPENAI_CLIENT.md    # Enhanced OpenAI client documentation
    └── 📄 PROJECT_RUNNING_STATUS.md    # Project running status
```

## 🎯 Core Components

### **Application Core (`email_crm_sync/`)**
The main package containing all business logic:

- **`clients/`** - API wrappers for external services
- **`config/`** - Configuration loading and validation
- **`services/`** - Email processing business logic
- **`utils/`** - Helper functions and utilities

### **Development Tools (`scripts/`, `tools/`, `tests/`)**
Supporting scripts for development and maintenance:

- **`scripts/`** - Setup and installation helpers for API configuration
- **`tools/`** - Diagnostic and discovery utilities for development
- **`tests/`** - Comprehensive testing suite with 11 test modules

### **Configuration (`email_crm_sync/config/`, `examples/`)**
Configuration management:

- **`email_crm_sync/config/`** - Your actual configuration and templates
- **`examples/`** - Additional templates and examples for setup

### **Documentation (`docs/`)**
Project documentation and guides

## 🚀 Key Files

| File | Purpose |
|------|---------|
| `main.py` | Application entry point - run this to start processing |
| `Makefile` | Common commands (`make help` to see all) |
| `scripts/setup_zoho_complete.py` | Complete Zoho CRM setup guide |
| `tools/discover_zoho_modules.py` | Discover your Zoho CRM modules |
| `tests/run_complete_test.py` | Test entire system |
| `email_crm_sync/config/api_keys.yaml` | Your API configuration |
| `email_crm_sync/clients/zoho_v8_enhanced_client.py` | Primary Zoho client |
| `docs/SETUP_GUIDE.md` | Quick setup guide |

## 🛠️ Development Workflow

### **Initial Setup**
```bash
make install          # Install dependencies
make setup            # Interactive API setup
```

### **Development**
```bash
make status           # Check project status
make test             # Run tests
make discover         # Discover Zoho modules
```

### **Usage**
```bash
make run              # Process emails once
make monitor          # Continuous monitoring
```

### **Maintenance**
```bash
make clean            # Clean temporary files
make format           # Format code
make lint             # Check code quality
```

## 📦 Import Structure

The project uses relative imports within the package:

```python
# From main.py
from email_crm_sync.config.loader import ConfigLoader
from email_crm_sync.clients.gmail_client import GmailClient

# From within package
from .config.loader import ConfigLoader
from .clients.gmail_client import GmailClient
```

## 🔒 Security

### **Protected Files (in .gitignore)**
- `email_crm_sync/config/api_keys.yaml` - Your actual API keys
- `*.json` - Credential files
- `*.log` - Log files
- `__pycache__/` - Python cache
- `.env` - Environment variables

### **Safe to Commit**
- `email_crm_sync/config/api_keys.yaml.example` - Template file
- `examples/api_keys.yaml.example` - Additional template
- All source code
- Documentation
- Requirements and setup files

## 🎯 Benefits of This Structure

✅ **Separation of Concerns** - Clear boundaries between components
✅ **Easy Testing** - Tests isolated from main code
✅ **Configuration Management** - Centralized config with examples
✅ **Development Tools** - Helpers for setup and debugging
✅ **Documentation** - All guides in one place
✅ **Security** - Sensitive files properly excluded
✅ **Maintainability** - Clear structure for future changes
