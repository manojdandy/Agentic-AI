# 🔧 Configuration Guide

## ✅ Everything is Now Configurable!

**NO HARDCODED VALUES** - All configuration comes from the `.env` file!

---

## 📋 Quick Start

### Step 1: Copy the Example File
```bash
cp .env.example .env
```

### Step 2: Edit Your Configuration
```bash
nano .env  # or use your favorite editor
```

### Step 3: Set Your API Key
```bash
GEMINI_API_KEY=your-actual-api-key-here
```

### Step 4: Start the App
```bash
python app.py
```

**That's it!** All changes take effect on restart.

---

## 🎯 All Configurable Values

### 🔑 **API Keys**
```bash
GEMINI_API_KEY=your-gemini-api-key-here
```

### 🤖 **Model Configuration**
```bash
MODEL_NAME=gemini-2.0-flash-exp        # Which Gemini model to use
MODEL_TEMPERATURE=0.0                   # 0.0 = deterministic, 1.0 = creative
MAX_TOKENS=2048                         # Max tokens in response
```

**Available Models:**
- `gemini-2.0-flash-exp` (fastest, recommended)
- `gemini-1.5-pro` (more powerful)
- `gemini-1.5-flash` (balanced)

### 🛡️ **Security Thresholds**
```bash
RISK_THRESHOLD_BLOCK=0.8      # Block if risk score >= 0.8
RISK_THRESHOLD_SANITIZE=0.5   # Sanitize if risk score >= 0.5
RISK_THRESHOLD_MONITOR=0.3    # Monitor if risk score >= 0.3
```

**Risk Scores:**
- `1.0` = Critical (always block)
- `0.8` = High (block by default)
- `0.5` = Medium (sanitize)
- `0.3` = Low (monitor)
- `0.0` = Safe

### ⚡ **Performance Settings**
```bash
MAX_CONTEXT_LENGTH=10000      # Max chars in context
REQUEST_TIMEOUT=30            # Timeout in seconds
MAX_RETRIES=3                 # Retry failed requests
```

### 📝 **Logging Configuration**
```bash
LOG_LEVEL=INFO               # DEBUG, INFO, WARNING, ERROR
LOG_FILE=logs/security.log   # Path to log file
ENABLE_METRICS=true          # Collect performance metrics
```

### 🚦 **Rate Limiting**
```bash
RATE_LIMIT_REQUESTS=100           # Max requests per window
RATE_LIMIT_WINDOW_SECONDS=60      # Time window (seconds)
```

### 💾 **Database**
```bash
DB_TYPE=sqlite              # sqlite or postgresql
DB_PATH=data/security.db    # Path to database
```

### 🛡️ **Large Prompt Defense**
```bash
TIER=free                   # free, starter, pro, enterprise
MAX_CHAR_LIMIT=50000        # Max characters allowed
MAX_TOKEN_LIMIT=2000        # Max tokens allowed
```

**Tier Limits:**
| Tier | Max Chars | Max Tokens | Rate Limit |
|------|-----------|------------|------------|
| free | 50K | 2K | 10 req/s |
| starter | 200K | 8K | 100 req/s |
| pro | 500K | 16K | 500 req/s |
| enterprise | 1M | 32K | 1000 req/s |

### 🌍 **Environment**
```bash
ENVIRONMENT=development     # development, staging, production
DEBUG=false                 # Enable debug mode
```

---

## 🎨 Common Configurations

### Development Mode
```bash
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
MODEL_TEMPERATURE=0.0
```

### Production Mode
```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
RISK_THRESHOLD_BLOCK=0.7   # More strict
RATE_LIMIT_REQUESTS=50     # More conservative
```

### High Security Mode
```bash
RISK_THRESHOLD_BLOCK=0.6   # Block more aggressively
RISK_THRESHOLD_SANITIZE=0.4
RISK_THRESHOLD_MONITOR=0.2
MAX_CHAR_LIMIT=20000       # Smaller inputs
```

### Performance Mode
```bash
MODEL_NAME=gemini-2.0-flash-exp
REQUEST_TIMEOUT=15
MAX_RETRIES=1
ENABLE_METRICS=false
```

---

## 🧪 Testing Configuration

### Test Current Config
```bash
python -c "from src.core.config import settings; print(f'Model: {settings.model_name}')"
```

### Test Specific Value
```bash
python -c "from src.core.config import settings; print(f'Tier: {settings.tier}')"
```

### Show All Settings
```bash
python << 'EOF'
from src.core.config import settings
import json

config = {
    'model_name': settings.model_name,
    'tier': settings.tier,
    'environment': settings.environment,
    'risk_threshold_block': settings.risk_threshold_block,
    'log_level': settings.log_level,
}

print(json.dumps(config, indent=2))
EOF
```

---

## 🔄 Changing Configuration

### Method 1: Edit .env File
```bash
nano .env
# Make changes
# Restart app: python app.py
```

### Method 2: Environment Variables
```bash
export MODEL_NAME=gemini-1.5-pro
export TIER=pro
python app.py
```

### Method 3: Inline
```bash
MODEL_NAME=gemini-1.5-pro TIER=pro python app.py
```

---

## 📚 Configuration Hierarchy

**Priority (highest to lowest):**
1. Environment variables (exported)
2. .env file
3. Default values (fallback)

**Example:**
```bash
# In .env
MODEL_NAME=gemini-2.0-flash-exp

# Override with export
export MODEL_NAME=gemini-1.5-pro

# Final value: gemini-1.5-pro (env var wins)
```

---

## 🚨 Important Notes

### Security
- ✅ **NEVER commit .env** to git (already in .gitignore)
- ✅ **Keep API keys secret**
- ✅ **Use .env.example** as template
- ✅ **Different .env per environment** (dev, staging, prod)

### Best Practices
- ✅ **Always have defaults** (done!)
- ✅ **Document all values** (done!)
- ✅ **Validate on startup** (done!)
- ✅ **Log configuration** (in debug mode)

### Performance
- Configuration loaded once at startup (cached)
- Changes require restart
- No performance impact during runtime

---

## 🎯 Verification

### ✅ Checklist
- [x] No hardcoded values in code
- [x] All values in .env file
- [x] All values have defaults
- [x] All values documented
- [x] .env.example created
- [x] API key configurable
- [x] Model name configurable
- [x] All thresholds configurable
- [x] Environment configurable

### 🧪 Test Commands
```bash
# Test config loads
python -c "from src.core.config import settings; print('✅ OK')"

# Test API key
python -c "from src.core.config import settings; print(f'API Key: {\"SET\" if settings.gemini_api_key else \"NOT SET\"}')"

# Test model name
python -c "from src.core.config import settings; print(f'Model: {settings.model_name}')"

# Test app loads
python -c "from app import app; print('✅ App OK')"
```

---

## 📖 Examples

### Example 1: Change Model
```bash
# Edit .env
MODEL_NAME=gemini-1.5-pro

# Restart app
python app.py
```

### Example 2: Enable Debug Mode
```bash
# Edit .env
DEBUG=true
LOG_LEVEL=DEBUG

# Restart app
python app.py
```

### Example 3: Upgrade Tier
```bash
# Edit .env
TIER=pro
MAX_CHAR_LIMIT=500000
MAX_TOKEN_LIMIT=16000

# Restart app
python app.py
```

### Example 4: Production Setup
```bash
# Create production .env
cp .env.example .env.production

# Edit for production
nano .env.production

# Use production config
ln -sf .env.production .env
python app.py
```

---

## 🎉 Summary

**Before:** ❌ Hardcoded values in code  
**After:** ✅ Everything configurable via .env

**Benefits:**
- ✅ No code changes needed
- ✅ Different configs per environment
- ✅ Easy to customize
- ✅ Secure (API keys not in code)
- ✅ Following best practices

---

## 📞 Need Help?

**Files:**
- `.env` - Your configuration (private)
- `.env.example` - Template (committed)
- `src/core/config.py` - Settings class

**Documentation:**
- This file: `CONFIGURATION-GUIDE.md`
- Pydantic Settings: https://docs.pydantic.dev/latest/concepts/pydantic_settings/

---

**Status: ✅ FULLY CONFIGURABLE!**  
**All values read from .env file!**  
**No hardcoded values!** 🎉




