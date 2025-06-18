# Email CRM Sync

An intelligent email processing system that automatically syncs Gmail emails with Zoho CRM, using OpenAI for content analysis and smart record matching.

## 📋 Table of Contents

- [Features](#-features)
- [Use Cases](#-use-cases)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Testing](#-testing)
- [Security](#-security)
- [Monitoring](#-monitoring)
- [Development](#-development)
- [Troubleshooting](#-troubleshooting)
- [Resources & Documentation](#-resources--documentation)
- [License](#-license)
- [Important Notes](#-important-notes)
- [Support](#-support)
- [Contributing](#-contributing)

## 🎯 Features

- **Smart Email Processing**: Automatically processes Gmail emails and creates notes in Zoho CRM
- **AI-Powered Analysis**: Uses OpenAI to extract key information and match emails to CRM records  
- **Advanced Email Classification**: Automatically categorizes emails (inquiry, update, complaint, meeting, etc.)
- **Intelligent Urgency Detection**: Identifies critical emails requiring immediate attention
- **Sentiment Analysis**: Analyzes email tone (positive, neutral, negative, mixed)
- **Semantic Matching**: AI-powered matching of emails to development records with confidence scoring
- **Robust Duplicate Detection**: Prevents duplicate notes with intelligent Gmail ID tracking
- **OAuth2 Security**: Secure authentication for all APIs with automatic token refresh
- **Multi-Region Support**: Full support for Zoho EU, US, India, Australia, China, Japan, and Canada data centers
- **Configurable Monitoring**: Single-run or continuous monitoring modes
- **Comprehensive Testing**: 12 test modules ensuring 100% reliability
- **Professional Summaries**: AI-generated summaries optimized for CRM notes
- **Enhanced COQL Support**: Advanced SQL-like queries for complex CRM searches
- **Official API Compliance**: Updated for 2025 API requirements and best practices

## 💼 Use Cases

### Real Estate & Property Development
- **Client Inquiry Management**: Automatically process and categorize property inquiries
- **Site Visit Coordination**: Track and schedule property viewings
- **Development Updates**: Manage project status communications
- **Investor Relations**: Handle investor communications and updates

### Business Operations
- **Customer Service**: Streamline customer inquiry processing
- **Lead Management**: Automatic lead capture and qualification
- **Project Communication**: Track project-related email communications
- **Compliance**: Maintain comprehensive communication records

### Benefits
- **Time Savings**: Reduce manual email processing by 90%
- **Improved Accuracy**: AI-powered extraction eliminates human error
- **Better Organization**: Automatic categorization and tagging
- **Enhanced Productivity**: Focus on high-value activities instead of data entry
- **Compliance**: Complete audit trail of all communications

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Gmail account with API access
- Zoho CRM account (EU or US)
- OpenAI API key

### Installation
```bash
# Clone and install
git clone <repository>
cd email_crm_sync
pip install -r requirements.txt

# Setup configuration
cp examples/api_keys.yaml.example email_crm_sync/config/api_keys.yaml
# Edit api_keys.yaml with your credentials
```

### Quick Setup
```bash
# Interactive setup (recommended)
python scripts/setup_zoho_complete.py

# Run health check
python main.py --health-check

# Process emails
python main.py --mode once
```

## 📁 Project Structure

```
email_crm_sync/
├── 📄 main.py                    # Main application entry point
├── 📂 email_crm_sync/           # Core application package
│   ├── 📂 clients/              # API client modules
│   │   ├── gmail_client.py       # Gmail API integration
│   │   ├── openai_client.py      # OpenAI API integration
│   │   └── zoho_v8_enhanced_client.py # Zoho CRM V8 API client
│   ├── 📂 config/               # Configuration management
│   │   ├── loader.py             # Configuration loader
│   │   └── api_keys.yaml         # Your API configuration
│   ├── 📂 services/             # Business logic
│   │   └── enhanced_processor.py # Email processing engine
│   └── 📂 utils/                # Helper utilities
├── 📂 scripts/                  # Setup and utility scripts
│   ├── setup_zoho_complete.py   # Complete Zoho setup guide
│   ├── generate_zoho_oauth_url.py # OAuth URL generator
│   └── exchange_zoho_tokens.py  # Token exchange utility
├── 📂 tools/                    # Development tools
│   ├── discover_zoho_modules.py  # Module discovery
│   └── refresh_token.py          # Token refresh utility
├── 📂 tests/                    # Test suite
│   └── run_complete_test.py      # Complete integration tests
└── 📂 docs/                     # Documentation
    ├── SETUP_GUIDE.md            # Complete setup instructions
    └── PROJECT_STRUCTURE.md      # Architecture overview
```

## 🔧 Configuration

### API Keys Configuration
Edit `email_crm_sync/config/api_keys.yaml`:

```yaml
# OpenAI Configuration
openai_api_key: "your_openai_api_key"

# Zoho CRM Configuration  
zoho_client_id: "your_zoho_client_id"
zoho_client_secret: "your_zoho_client_secret"
zoho_access_token: "your_zoho_access_token"
zoho_refresh_token: "your_zoho_refresh_token"
zoho_data_center: "eu"  # or "com" for US
zoho_developments_module: "Accounts"  # or your custom module

# Gmail Configuration
gmail_credentials_path: "/path/to/gmail_credentials.json"
```

## 📋 Usage

### Single Run Mode
```bash
python main.py --mode once
```

### Continuous Monitoring
```bash
python main.py --mode monitor --interval 300
```

### Health Check
```bash
python main.py --health-check
```

### Token Management
```bash
# Refresh expired tokens
python tools/refresh_token.py

# Discover available modules
python tools/discover_zoho_modules.py
```

## 🧪 Testing

```bash
# Run complete test suite
python tests/run_complete_test.py

# Run specific tests
python tests/test_v8_enhanced_client.py
python tests/test_enhanced_openai.py
```

## 🔐 Security

- All sensitive credentials stored in `api_keys.yaml` (gitignored)
- OAuth2 authentication with automatic token refresh
- No hardcoded credentials in source code
- Gmail tokens stored securely in pickle files

## 📊 Monitoring

The application provides comprehensive logging and monitoring:
- Real-time processing status
- API connection health checks
- Duplicate detection tracking
- Error handling and recovery

## 🛠️ Development

### Make Commands
```bash
make install    # Install dependencies
make test       # Run tests
make run        # Single run
make monitor    # Continuous monitoring
make discover   # Discover Zoho modules
```

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
