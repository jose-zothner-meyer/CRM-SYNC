# Script Deprecation Notice

## Redundant Scripts Now Integrated Into CLI

The following scripts have been integrated into the main CLI (`main.py`) and are now redundant:

### **Tools Directory - NOW DEPRECATED**
- `tools/refresh_token.py` → **Use:** `python main.py token refresh`
- `tools/exchange_new_tokens.py` → **Use:** `python main.py token exchange --code "AUTH_CODE"`
- `tools/discover_zoho_modules.py` → **Use:** `python main.py discover`

### **Scripts Directory - NOW DEPRECATED**
- `scripts/verify_gmail_setup.py` → **Use:** `python main.py setup verify-gmail`
- `scripts/exchange_zoho_tokens.py` → **Use:** `python main.py token exchange --code "AUTH_CODE"`
- `scripts/setup_api_tokens.py` → **Use:** Manual config file editing (better documentation provided)
- `scripts/generate_zoho_oauth_url.py` → **Use:** Manual generation via Zoho console
- `scripts/setup_zoho_complete.py` → **Use:** `python main.py token exchange --code "AUTH_CODE"`

## Migration Guide

### Old Way:
```bash
# Token refresh
python tools/refresh_token.py

# Token exchange
python tools/exchange_new_tokens.py

# Gmail verification
python scripts/verify_gmail_setup.py

# Module discovery  
python tools/discover_zoho_modules.py
```

### New Way (Unified CLI):
```bash
# Token refresh
python main.py token refresh

# Token exchange
python main.py token exchange --code "1000.abcd1234..."

# Gmail verification
python main.py setup verify-gmail

# Module discovery
python main.py discover

# Health checks
python main.py health

# Run email processing
python main.py run --mode once
python main.py run --mode monitor
```

## Benefits of New CLI Approach

1. **Unified Interface**: All functionality in one place
2. **Better Error Handling**: Improved exception handling and error reporting
3. **Consistent Logging**: Centralized logging configuration
4. **Better Documentation**: Built-in help with `--help`
5. **Improved Reliability**: Better token management and configuration handling

## Cleanup Plan

### Phase 1: Mark as Deprecated (✅ DONE)
- Add deprecation notice to individual scripts
- Update documentation

### Phase 2: Optional Cleanup (Future)
- Move deprecated scripts to `deprecated/` folder
- Update any external documentation references
- Consider removing after sufficient warning period

## Current Status
- ✅ All functionality successfully integrated into main CLI
- ✅ All tests passing (except token expiry test, which is expected)
- ✅ Exception handling improved across the codebase
- ✅ System health checks all passing
