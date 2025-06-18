.PHONY: help install setup test clean run monitor discover lint format status test-v8 analyze-v8 v8-setup

# Default target
help:
	@echo "Email CRM Sync - Available Commands:"
	@echo "  make install     - Install dependencies"
	@echo "  make setup       - Interactive API token setup"
	@echo "  make test        - Run all tests"
	@echo "  make test-v8     - Test enhanced V8 client"
	@echo "  make v8-setup    - Quick V8 client setup guide"
	@echo "  make run         - Process emails once"
	@echo "  make monitor     - Start email monitoring"
	@echo "  make discover    - Discover Zoho CRM modules"
	@echo "  make status      - Show project status"
	@echo "  make analyze-v8  - Analyze V8 API capabilities"
	@echo "  make clean       - Clean temporary files"
	@echo "  make lint        - Run code linting"
	@echo "  make format      - Format code with black"

# Installation and setup
install:
	pip install -r requirements.txt

setup:
	python scripts/setup_api_tokens.py

# Testing
test:
	python tests/run_complete_test.py

test-zoho:
	python tests/test_developments_module.py

test-v8:
	@echo "🧪 Testing Enhanced V8 Client..."
	python tests/test_v8_enhanced_client.py

v8-setup:
	@echo "🚀 Enhanced V8 Client Setup Guide"
	python scripts/v8_setup.py

# Running the application
run:
	python main.py --mode once

monitor:
	python main.py --mode monitor

# Development tools
discover:
	python tools/discover_zoho_modules.py

status:
	python scripts/project_status.py

analyze-v8:
	@echo "📊 Zoho CRM V8 API Analysis"
	@echo "📖 Comprehensive analysis: docs/ZOHO_V8_API_ANALYSIS.md"
	@echo "🧪 Test V8 client: make test-v8"
	@echo "🔍 Enhanced client: email_crm_sync/clients/zoho_v8_enhanced_client.py"
	@echo "🎯 Key improvements:"
	@echo "   - Advanced email search strategies"
	@echo "   - COQL query support for complex searches"
	@echo "   - Enhanced note creation with proper attachment"
	@echo "   - Comprehensive caching and error handling"
	@echo "   - Multiple search fallback strategies"

# Code quality
lint:
	flake8 email_crm_sync/ main.py
	mypy email_crm_sync/ main.py

format:
	black email_crm_sync/ main.py scripts/ tools/ tests/

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -f *.log
	rm -f zoho_modules_discovery.json
