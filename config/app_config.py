"""
Configuration management for the Code Review Application.

This module handles application settings, environment variables,
and provides a centralized configuration interface.
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


class ApplicationConfig:
    """Centralized configuration management for the application."""
    
    # Default configuration values
    DEFAULTS = {
        'ollama_api_url': 'http://localhost:11434/api/chat',
        'model_name': 'qwen2.5-coder',
        'buffer_size': 20,
        'flush_interval_ms': 100,
        'max_conversation_length': 50000,  # characters
        'request_timeout': 30.0,  # seconds
        'max_retries': 3,
        'ui_theme': 'light',
        'window_width': 1200,
        'window_height': 800,
        'log_level': 'INFO'
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration with optional config file."""
        self._config: Dict[str, Any] = {}
        self._config_file = config_file or self._get_default_config_path()
        self._load_configuration()
    
    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        home_dir = Path.home()
        config_dir = home_dir / '.code_review_app'
        config_dir.mkdir(exist_ok=True)
        return str(config_dir / 'config.json')
    
    def _load_configuration(self) -> None:
        """Load configuration from file and environment variables."""
        # Start with defaults
        self._config = self.DEFAULTS.copy()
        
        # Load from file if exists
        if os.path.exists(self._config_file):
            try:
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    self._config.update(file_config)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load config file {self._config_file}: {e}")
        
        # Override with environment variables
        self._load_from_environment()
        
        # Setup logging
        self._setup_logging()
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            'OLLAMA_API_URL': 'ollama_api_url',
            'MODEL_NAME': 'model_name',
            'BUFFER_SIZE': ('buffer_size', int),
            'FLUSH_INTERVAL_MS': ('flush_interval_ms', int),
            'MAX_CONVERSATION_LENGTH': ('max_conversation_length', int),
            'REQUEST_TIMEOUT': ('request_timeout', float),
            'MAX_RETRIES': ('max_retries', int),
            'UI_THEME': 'ui_theme',
            'WINDOW_WIDTH': ('window_width', int),
            'WINDOW_HEIGHT': ('window_height', int),
            'LOG_LEVEL': 'log_level'
        }
        
        for env_var, config_key in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                if isinstance(config_key, tuple):
                    key, converter = config_key
                    try:
                        self._config[key] = converter(env_value)
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Invalid value for {env_var}: {env_value}. {e}")
                else:
                    self._config[config_key] = env_value
    
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        log_level = getattr(logging, self._config['log_level'].upper(), logging.INFO)
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('code_review_app.log')
            ]
        )
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self._config[key] = value
    
    def save(self) -> None:
        """Save current configuration to file."""
        try:
            os.makedirs(os.path.dirname(self._config_file), exist_ok=True)
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save config file: {e}")
    
    @property
    def ollama_api_url(self) -> str:
        return self._config['ollama_api_url']
    
    @property
    def model_name(self) -> str:
        return self._config['model_name']
    
    @property
    def buffer_size(self) -> int:
        return self._config['buffer_size']
    
    @property
    def flush_interval_ms(self) -> int:
        return self._config['flush_interval_ms']
    
    @property
    def max_conversation_length(self) -> int:
        return self._config['max_conversation_length']
    
    @property
    def request_timeout(self) -> float:
        return self._config['request_timeout']
    
    @property
    def max_retries(self) -> int:
        return self._config['max_retries']
    
    @property
    def ui_theme(self) -> str:
        return self._config['ui_theme']
    
    @property
    def window_size(self) -> tuple[int, int]:
        return (self._config['window_width'], self._config['window_height'])


# Global configuration instance
config = ApplicationConfig()