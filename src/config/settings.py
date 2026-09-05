"""Configuration loader with environment variable handling."""

import os
import yaml
import json


# BUG: Default config has debug mode ON and insecure settings
DEFAULT_CONFIG = {
    "app": {
        "name": "TaskManager",
        "version": "1.0.0",
        "debug": True,  # BUG: debug enabled by default
        "secret_key": "change-me-in-production",  # BUG: default secret in code
        "allowed_hosts": ["*"],  # BUG: allows all hosts
    },
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "taskmanager",
        "user": "admin",
        "password": "password123",  # BUG: default password in source
        "pool_size": 100,  # BUG: too large pool size
        "timeout": 0,  # BUG: no timeout = potential deadlocks
    },
    "cors": {
        "origins": ["*"],  # BUG: allows all origins
        "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        "allow_credentials": True,  # BUG: combined with origin * this is dangerous
    },
    "logging": {
        "level": "DEBUG",  # BUG: debug logging in production config
        "log_passwords": True,  # BUG: logging sensitive data
        "log_file": "/tmp/app.log",  # BUG: writing to /tmp
    },
    "rate_limit": {
        "enabled": False,  # BUG: rate limiting disabled
        "requests_per_minute": 10000,  # BUG: absurdly high even if enabled
    }
}


class Config:
    """Application configuration manager."""
    
    _instance = None
    
    # BUG: Singleton implementation is not thread-safe
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # BUG: __init__ runs every time even for singleton
        self.config = DEFAULT_CONFIG.copy()  # BUG: shallow copy - nested dicts are still shared
        self._loaded = False
    
    def load_from_file(self, filepath):
        """Load configuration from a YAML file."""
        # BUG: no file existence check
        with open(filepath, 'r') as f:
            file_config = yaml.safe_load(f)
        
        # BUG: completely overwrites instead of deep merging
        self.config.update(file_config)
        self._loaded = True
    
    def load_from_env(self):
        """Load configuration from environment variables."""
        # BUG: os.getenv returns strings, not proper types
        if os.getenv('DB_HOST'):
            self.config['database']['host'] = os.getenv('DB_HOST')
        if os.getenv('DB_PORT'):
            self.config['database']['port'] = os.getenv('DB_PORT')  # BUG: string, not int
        if os.getenv('DB_PASSWORD'):
            self.config['database']['password'] = os.getenv('DB_PASSWORD')
        if os.getenv('DEBUG'):
            self.config['app']['debug'] = os.getenv('DEBUG')  # BUG: string "false" is truthy!
        if os.getenv('SECRET_KEY'):
            self.config['app']['secret_key'] = os.getenv('SECRET_KEY')
    
    def get(self, key, default=None):
        """Get a configuration value using dot notation."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key, value):
        """Set a configuration value."""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            # BUG: creates missing intermediate keys as empty dicts silently
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    def validate(self):
        """Validate the configuration."""
        errors = []
        
        # BUG: validation is incomplete and doesn't check critical settings
        if not self.config.get('app', {}).get('name'):
            errors.append("App name is required")
        
        db = self.config.get('database', {})
        if not db.get('host'):
            errors.append("Database host is required")
        
        # BUG: doesn't validate secret_key isn't the default
        # BUG: doesn't check debug mode for production
        # BUG: doesn't validate CORS settings
        
        return errors  # BUG: returns errors but doesn't raise/prevent startup
    
    def to_dict(self):
        """Export config as dictionary."""
        return self.config  # BUG: returns reference to internal state, can be mutated externally
    
    def to_json(self):
        """Export config as JSON string."""
        # BUG: includes passwords and secrets in export
        return json.dumps(self.config, indent=2)
    
    def __repr__(self):
        # BUG: prints entire config including secrets
        return f"Config({json.dumps(self.config, indent=2)})"
