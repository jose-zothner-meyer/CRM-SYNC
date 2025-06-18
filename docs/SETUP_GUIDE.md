# Complete Setup Guide

This guide will walk you through setting up the Email CRM Sync application from scratch.

## 📋 Prerequisites

- **Python 3.8+** installed on your system
- **Gmail account** with emails you want to sync
- **Zoho CRM account** (EU or US data center)
- **OpenAI API account** with available credits

## 🔧 Step 1: Basic Setup

### 1.1 Clone and Install
```bash
git clone <repository-url>
cd email_crm_sync
pip install -r requirements.txt
```

### 1.2 Create Configuration File
```bash
cp examples/api_keys.yaml.example email_crm_sync/config/api_keys.yaml
```

## 🔑 Step 2: API Credentials Setup

### 2.1 OpenAI API Key
1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new secret key
3. Copy the key to your configuration:
```yaml
openai_api_key: "sk-proj-your-key-here"
```

### 2.2 Gmail API Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API
4. Create credentials → OAuth 2.0 Client ID → Desktop Application
5. Download the JSON file as `gmail_credentials.json`
6. Place it in `email_crm_sync/config/gmail_credentials.json`

### 2.3 Zoho CRM API Setup

#### **Multi-Data Center Support**

**Based on [official documentation](https://www.zoho.com/crm/developer/docs/api/v8/multi-dc.html):**

| Your CRM URL | Data Center | API Console |
|--------------|-------------|-------------|
| https://crm.zoho.eu | EU | https://api-console.zoho.eu |
| https://crm.zoho.com | US | https://api-console.zoho.com |  
| https://crm.zoho.in | India | https://api-console.zoho.in |
| https://crm.zoho.com.au | Australia | https://api-console.zoho.com.au |
| https://crm.zoho.com.cn | China | https://api-console.zoho.com.cn |
| https://crm.zoho.jp | Japan | https://api-console.zoho.jp |
| https://crm.zohocloud.ca | Canada | https://api-console.zohocloud.ca |

#### **Required OAuth Scopes**
Per [official scopes documentation](https://www.zoho.com/crm/developer/docs/api/v8/scopes.html):
```
ZohoCRM.modules.ALL        # Full module access
ZohoCRM.settings.READ      # Metadata access  
ZohoCRM.org.READ          # Organization info
ZohoCRM.coql.READ         # Advanced search (optional)
```

#### Create Zoho Self Client
1. Go to your Zoho Developer Console:
   - **EU**: [https://api-console.zoho.eu](https://api-console.zoho.eu)
   - **US**: [https://api-console.zoho.com](https://api-console.zoho.com)
   - **India**: [https://api-console.zoho.in](https://api-console.zoho.in)

2. Click **"Add Client"** → **"Self Client"** → **"CREATE NOW"**

3. Fill in details:
   ```
   Client Name: Email CRM Sync
   Homepage URL: http://localhost
   Authorized Redirect URIs: http://localhost
   ```

4. Save your **Client ID** and **Client Secret**

## 🚀 Step 3: Automated Setup (Recommended)

Run the interactive setup script:
```bash
python scripts/setup_zoho_complete.py
```

This will:
- Guide you through OAuth2 setup
- Generate authorization URLs
- Exchange codes for tokens
- Update your configuration file

## 🔧 Step 4: Manual Configuration

If you prefer manual setup, edit `email_crm_sync/config/api_keys.yaml`:

```yaml
# OpenAI Configuration
openai_api_key: "your_openai_api_key_here"

# Zoho CRM Configuration  
zoho_client_id: "your_zoho_client_id"
zoho_client_secret: "your_zoho_client_secret"
zoho_access_token: ""  # Will be generated
zoho_refresh_token: ""  # Will be generated
zoho_data_center: "eu"  # or "com", "in", etc.
zoho_developments_module: "Accounts"  # or your custom module

# Gmail Configuration
gmail_credentials_path: "/full/path/to/gmail_credentials.json"
gmail_query_starred: "is:starred -label:Processed"
gmail_query_unread: "is:unread -label:Processed"

# Application Settings
email_batch_size: 5
max_emails_per_run: 20
log_level: "INFO"
```

### Manual Token Generation

1. **Generate OAuth URL**:
```bash
python scripts/generate_zoho_oauth_url.py
```

2. **Visit the URL**, authorize the app, copy the authorization code

3. **Exchange code for tokens**:
```bash
python scripts/exchange_zoho_tokens.py
```

## ✅ Step 5: Verification

### 5.1 Run Health Check
```bash
python main.py --health-check
```

Expected output:
```
✅ Gmail: Client initialized successfully
✅ OpenAI: Client initialized successfully  
✅ Zoho CRM: Connection successful
✅ All health checks passed - System ready
```

### 5.2 Test Gmail Access
```bash
python scripts/verify_gmail_setup.py
```

### 5.3 Discover Zoho Modules
```bash
python tools/discover_zoho_modules.py
```

### 5.4 Run Complete Test Suite
```bash
python tests/run_complete_test.py
```

## 🎯 Step 6: First Run

### Single Email Processing
```bash
python main.py --mode once
```

### Continuous Monitoring
```bash
python main.py --mode monitor --interval 300
```

## 🛠️ Configuration Options

### Email Processing Settings
```yaml
# How many emails to process at once
email_batch_size: 5

# Maximum emails per run (prevents overload)
max_emails_per_run: 20

# Time between monitoring runs (seconds)
monitoring_interval: 300
```

### Gmail Query Customization
```yaml
# Process starred emails
gmail_query_starred: "is:starred -label:Processed"

# Process unread emails  
gmail_query_unread: "is:unread -label:Processed"

# Custom query example
gmail_query_custom: "from:client@example.com -label:Processed"
```

### Zoho Module Configuration
```yaml
# Default module for developments
zoho_developments_module: "Accounts"

# Custom module example
zoho_developments_module: "Custom_Developments"
```

## 🔐 Security Best Practices

### 1. Protect Sensitive Files
Ensure these files are **never** committed to version control:
- `email_crm_sync/config/api_keys.yaml`
- `email_crm_sync/config/gmail_credentials.json`
- `email_crm_sync/config/gmail_token.pickle`

### 2. Use Environment Variables (Alternative)
Instead of YAML, you can use environment variables:
```bash
export OPENAI_API_KEY="your-key"
export ZOHO_ACCESS_TOKEN="your-token"
export GMAIL_CREDENTIALS_PATH="/path/to/credentials.json"
```

### 3. Regular Token Refresh
Tokens expire periodically. Refresh them with:
```bash
python tools/refresh_token.py
```

## 🐛 Common Issues & Solutions

### Issue: "Invalid Token" Error
**Solution**: 
```bash
python tools/refresh_token.py
```

### Issue: "Module Not Found" Error
**Solution**: 
```bash
python tools/discover_zoho_modules.py
# Update zoho_developments_module in config
```

### Issue: Gmail Authentication Error
**Solution**:
1. Re-download `gmail_credentials.json` from Google Cloud Console
2. Delete `gmail_token.pickle` if it exists
3. Run the application again to re-authenticate

### Issue: "CRM Does Not Exist" Error
**Solution**: Verify your Zoho data center setting matches your account region

### Issue: No Emails Found
**Solution**: 
1. Check your Gmail query filters
2. Ensure emails exist that match your criteria
3. Verify Gmail API permissions include read access

## 📊 Monitoring & Logs

### Log Levels
- `DEBUG`: Detailed API calls and responses
- `INFO`: General operation status (recommended)
- `WARNING`: Non-critical issues
- `ERROR`: Serious problems requiring attention

### Log Configuration
```yaml
log_level: "INFO"  # Change to DEBUG for troubleshooting
```

### Monitoring Dashboard
The application provides real-time status updates:
- Email processing progress
- API connection status
- Duplicate detection results
- Error notifications

## 🚀 Production Deployment

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv email_crm_env
source email_crm_env/bin/activate  # Linux/Mac
# or
email_crm_env\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Systemd Service (Linux)
Create `/etc/systemd/system/email-crm-sync.service`:
```ini
[Unit]
Description=Email CRM Sync Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/email_crm_sync
ExecStart=/path/to/python main.py --mode monitor
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable email-crm-sync
sudo systemctl start email-crm-sync
```

### 3. Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py", "--mode", "monitor"]
```

## 📈 Performance Optimization

### 1. Batch Size Tuning
- **Small batches (1-5)**: More responsive, higher API overhead
- **Large batches (10-20)**: More efficient, less responsive

### 2. Monitoring Interval
- **Short intervals (60-300s)**: Near real-time processing
- **Long intervals (600-3600s)**: Reduced API usage

### 3. Query Optimization
Use specific Gmail queries to reduce processing overhead:
```yaml
# Good: Specific sender
gmail_query: "from:important@client.com -label:Processed"

# Better: Date range + sender  
gmail_query: "from:important@client.com after:2025/1/1 -label:Processed"
```

## 🆘 Support

### Getting Help
1. Check this setup guide
2. Review the [Project Structure](PROJECT_STRUCTURE.md) documentation
3. Run health checks and review logs
4. Check common issues section above

### Debug Mode
Enable detailed logging for troubleshooting:
```yaml
log_level: "DEBUG"
debug_mode: true
```

---

**Setup Complete!** 🎉 Your Email CRM Sync application is ready for production use.

## ⚡ What's New - Latest API Updates

### 🔄 **Updated for 2025 API Requirements**

This setup guide has been updated to reflect the latest official API documentation:

#### **Zoho CRM V8 API (Latest)**
- **Multi-region support**: Full support for all 7 global data centers
- **Enhanced COQL queries**: SQL-like advanced search capabilities
- **Official OAuth scopes**: Updated to required scopes per documentation
- **Improved error handling**: Better error codes and troubleshooting

#### **Gmail API (Current)**
- **Minimal scopes**: Using only required permissions for security
- **Latest OAuth flow**: Following current Google best practices
- **Enhanced email processing**: Improved message parsing and filtering

#### **OpenAI API (Latest Models)**
- **GPT-4o-mini**: Cost-effective model for email classification
- **Enhanced prompts**: Optimized for property development workflows
- **Better rate limiting**: Improved handling of API limits
