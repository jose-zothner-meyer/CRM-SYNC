import yaml
import os
from pathlib import Path
from typing import Optional

class ConfigLoader:
    """
    Singleton ConfigLoader to ensure consistent configuration across the application.
    
    This class implements the singleton pattern to prevent multiple instances
    from loading configuration multiple times, which improves performance and
    ensures consistency across the application.
    """
    _instance = None
    _initialized = False
    def __new__(cls, path: Optional[str] = None):
        """Implement singleton pattern"""
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, path: Optional[str] = None):
        """Load configuration from YAML file or environment variables"""
        # Only initialize once
        if self._initialized:
            return
            
        # Try to load from YAML file first
        if path is None:
            path = self._find_config_file()
            
        if path and Path(path).exists():
            self._load_from_yaml(path)
        else:
            self._load_from_env()
            
        # Validate required configuration
        self._validate_config()
        
        # Mark as initialized
        self._initialized = True
    
    def _find_config_file(self) -> Optional[str]:
        """Find the configuration file in common locations"""
        possible_paths = [
            'config/api_keys.yaml',
            'email_crm_sync/config/api_keys.yaml',
            'api_keys.yaml',
            '.env.yaml'
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return path
        return None
    
    def _load_from_yaml(self, path: str):
        """Load configuration from YAML file"""
        with open(path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        
        # OpenAI API key and model settings
        self.openai_key = config.get('openai_api_key')
        openai_cfg = config.get('openai', {})
        self.chat_model = openai_cfg.get('chat_model', 'gpt-4o-mini')
        self.semantic_model = openai_cfg.get('semantic_model', 'gpt-4')
        self.openai_max_tokens = openai_cfg.get('max_tokens', 800)
        self.openai_temperature = openai_cfg.get('temperature', 0.1)
        
        # Zoho configuration
        self.zoho_token = config.get('zoho_access_token')
        self.zoho_refresh_token = config.get('zoho_refresh_token')
        self.zoho_client_id = config.get('zoho_client_id')
        self.zoho_client_secret = config.get('zoho_client_secret')
        self.zoho_data_center = config.get('zoho_data_center', 'com')
        
        # Gmail configuration
        self.gmail_credentials = config.get('gmail_credentials_path')
        
        # Optional settings
        self.zoho_base_url = config.get('zoho_base_url', 'https://www.zohoapis.com/crm/v2')
        self.zoho_developments_module = config.get('zoho_developments_module', 'Developments')
        self.email_batch_size = config.get('email_batch_size', 10)
        self.log_level = config.get('log_level', 'INFO')
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        self.openai_key = os.getenv('OPENAI_API_KEY')
        # OpenAI model settings
        self.chat_model = os.getenv('OPENAI_CHAT_MODEL', 'gpt-4o-mini')
        self.semantic_model = os.getenv('OPENAI_SEMANTIC_MODEL', 'gpt-4')
        self.openai_max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', '800'))
        self.openai_temperature = float(os.getenv('OPENAI_TEMPERATURE', '0.1'))
        
        # Zoho configuration
        self.zoho_token = os.getenv('ZOHO_ACCESS_TOKEN')
        self.zoho_refresh_token = os.getenv('ZOHO_REFRESH_TOKEN')
        self.zoho_client_id = os.getenv('ZOHO_CLIENT_ID')
        self.zoho_client_secret = os.getenv('ZOHO_CLIENT_SECRET')
        self.zoho_data_center = os.getenv('ZOHO_DATA_CENTER', 'com')
        
        # Gmail configuration
        self.gmail_credentials = os.getenv('GMAIL_CREDENTIALS_PATH')
        
        # Optional settings
        self.zoho_base_url = os.getenv('ZOHO_BASE_URL', 'https://www.zohoapis.com/crm/v2')
        self.zoho_developments_module = os.getenv('ZOHO_DEVELOPMENTS_MODULE', 'Developments')
        self.email_batch_size = int(os.getenv('EMAIL_BATCH_SIZE', '10'))
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    def _validate_config(self):
        """Validate that required configuration is present"""
        required_fields = [
            ('openai_key', 'OpenAI API key'),
            ('zoho_token', 'Zoho access token'),
            ('gmail_credentials', 'Gmail credentials path')
        ]
        
        missing = []
        for field, description in required_fields:
            if not getattr(self, field):
                missing.append(description)
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        # Validate Gmail credentials file exists
        if self.gmail_credentials and not Path(self.gmail_credentials).exists():
            raise FileNotFoundError(f"Gmail credentials file not found: {self.gmail_credentials}")
    
    def get_zoho_config(self) -> dict:
        """Get Zoho configuration as a dictionary"""
        return {
            'access_token': self.zoho_token,
            'refresh_token': getattr(self, 'zoho_refresh_token', None),
            'client_id': getattr(self, 'zoho_client_id', None),
            'client_secret': getattr(self, 'zoho_client_secret', None),
            'data_center': self.zoho_data_center,
            'developments_module': self.zoho_developments_module,
            'base_url': self.zoho_base_url
        }
    
    def get_openai_config(self) -> dict:
        """Get OpenAI model settings from configuration"""
        return {
            'chat_model': getattr(self, 'chat_model', 'gpt-4o-mini'),
            'semantic_model': getattr(self, 'semantic_model', 'gpt-4'),
            'max_tokens': getattr(self, 'openai_max_tokens', 800),
            'temperature': getattr(self, 'openai_temperature', 0.1)
        }
