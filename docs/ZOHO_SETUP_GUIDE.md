# 🚀 Zoho CRM Setup Guide

**Zoho CRM API Configuration for Email-to-CRM Sync**

This guide will help you configure Zoho CRM API access for the email sync system.

## 📋 **Overview**

This setup enables:
- ✅ Secure API access to your Zoho CRM
- ✅ Automatic token management and refresh
- ✅ Multi-region support (EU, US, India, Australia)
- ✅ Direct integration with Developments module

---

## 🎯 **Prerequisites**

- **Zoho CRM Account** (any data center)
- **Admin access** to create API applications
- **Basic terminal/command line familiarity**

---

## 🔧 **Step 1: Verify Your Data Center**

1. Log into your Zoho CRM account
2. Check the URL in your browser:
   - `https://crm.zoho.eu` = **EU Data Center** 
   - `https://crm.zoho.com` = **US Data Center**
   - `https://crm.zoho.in` = **India Data Center**
   - `https://crm.zoho.au` = **Australia Data Center**

> **Important**: The system automatically detects your region and uses the correct API endpoints.

---

## 🔐 **Step 2: Create Self Client Application**

### Navigate to Developer Console

Choose based on your data center:
- **EU**: [https://api-console.zoho.eu](https://api-console.zoho.eu)
- **US**: [https://api-console.zoho.com](https://api-console.zoho.com)
- **India**: [https://api-console.zoho.in](https://api-console.zoho.in)
- **Australia**: [https://api-console.zoho.au](https://api-console.zoho.au)

### Create Application

1. **Sign in** with your Zoho CRM account
2. **Click "Add Client"**
3. **Select "Self Client"** (perfect for automated background processes)
4. **Click "CREATE NOW"**

### Fill Application Details

```
Client Name: Email CRM Sync
Homepage URL: http://localhost
Authorized Redirect URIs: http://localhost
```

### Save Your Credentials

- Copy **Client ID** 
- Copy **Client Secret**
- Keep these secure!

---

## 🔑 **Step 3: Configure API Scopes**

### Required Scopes

```
ZohoCRM.modules.ALL
ZohoCRM.settings.READ
ZohoCRM.org.READ
```

### Generate Authorization URL

Replace `YOUR_CLIENT_ID` with your actual Client ID:

**For EU Data Center:**
```
https://accounts.zoho.eu/oauth/v2/auth?scope=ZohoCRM.modules.ALL,ZohoCRM.settings.READ,ZohoCRM.org.READ&client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost&access_type=offline
```

**For US Data Center:**
```
https://accounts.zoho.com/oauth/v2/auth?scope=ZohoCRM.modules.ALL,ZohoCRM.settings.READ,ZohoCRM.org.READ&client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost&access_type=offline
```

**For Other Data Centers:** Replace the domain accordingly (.in, .au, etc.)

---

## 🚀 **Step 4: Complete OAuth Setup**

### Automatic Setup (Recommended)

Run the complete setup script:

```bash
python scripts/setup_zoho_complete.py
```

This will:
- ✅ Generate the correct authorization URL for your region
- ✅ Guide you through the OAuth flow step-by-step
- ✅ Exchange authorization code for tokens automatically
- ✅ Test the API connection
- ✅ Validate module access
- ✅ Save everything to your config file

### Manual Setup (Fallback)

If the automatic script doesn't work:

1. **Open the authorization URL** in your browser
2. **Authorize the application**
3. **Copy the `code` parameter** from the redirect URL
4. **Exchange for tokens** using curl or the token exchange script

---

## ⚙️ **Step 5: Update Configuration**

Update your `email_crm_sync/config/api_keys.yaml`:

```yaml
# Zoho CRM Configuration
zoho:
  # From Developer Console
  client_id: "your_zoho_client_id"
  client_secret: "your_zoho_client_secret"
  
  # Will be generated automatically by setup script
  access_token: ""
  refresh_token: ""
  token_expires_at: ""
  
  # Your CRM module settings
  developments_module: "Developments"  # Adjust to your module name
  data_center: "eu"  # Options: "eu", "com", "in", "au"
```

### Data Center Endpoints

The system automatically maps your data center to the correct API endpoint:

- `eu` → `https://www.zohoapis.eu/crm/v8`
- `com` → `https://www.zohoapis.com/crm/v8`  
- `in` → `https://www.zohoapis.in/crm/v8`
- `au` → `https://www.zohoapis.au/crm/v8`

---

## 🧪 **Step 6: Test Your Setup**

### Quick Connection Test

```bash
python -c "
from email_crm_sync.clients.zoho_v8_enhanced_client import ZohoV8EnhancedClient
from email_crm_sync.config.loader import ConfigLoader

config = ConfigLoader('email_crm_sync/config/api_keys.yaml').config
client = ZohoV8EnhancedClient(config['zoho'])
result = client.health_check()
print('Health check:', 'PASSED' if result['success'] else 'FAILED')
"
```

### Comprehensive Test

```bash
python tests/run_complete_test.py
```

This verifies:
- ✅ Client initialization with proper endpoints
- ✅ Token management and refresh
- ✅ API connectivity to your region
- ✅ Module access and discovery
- ✅ Search functionality
- ✅ Note creation capability

---

## 🛠️ **Troubleshooting**

### Common Issues

#### "Invalid Client" Error
- **Cause**: Wrong data center endpoints
- **Solution**: Use correct developer console URL for your region

#### "CRM Does Not Exist" Error  
- **Cause**: Account not in expected data center
- **Solution**: Verify your account region in Zoho CRM URL

#### "Token Expired" Error
- **Cause**: Access token needs refresh
- **Solution**: System should auto-refresh, or run setup script again

#### "Module Not Found" Error
- **Cause**: Incorrect module name in configuration
- **Solution**: Check available modules:
  ```bash
  python tools/discover_zoho_modules.py
  ```

### Debug Mode

Enable detailed logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now all API calls will be logged
```

---

## 📋 **Setup Checklist**

- [ ] **Data center identified** (EU, US, India, Australia)
- [ ] **Developer Console accessed** (correct region)
- [ ] **Self Client created** with proper details
- [ ] **Client ID and Secret saved** securely
- [ ] **Authorization URL generated** correctly
- [ ] **Setup script completed** successfully
- [ ] **Configuration file updated** with tokens
- [ ] **Health check passed** ✅
- [ ] **Module access verified** ✅

---

## 🎉 **Success!**

Once all items are checked, your Zoho CRM integration is ready!

**Next Steps**:
1. Complete Gmail and OpenAI setup (see [SETUP_GUIDE.md](SETUP_GUIDE.md))
2. Run the full email sync system
3. Monitor token refresh in production

Your Zoho CRM API is now configured and production-ready! 🚀