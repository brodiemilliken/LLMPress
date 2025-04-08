"""
Configuration Loader for LLMPress

Loads and provides access to configuration settings from YAML files
"""
import os
import yaml
import logging

logger = logging.getLogger(__name__)

class ConfigLoader:
    """
    Configuration loader for LLMPress

    Loads configuration from YAML files and provides access to settings
    """

    def __init__(self, config_file=None, model_name=None):
        """
        Initialize configuration loader

        Args:
            config_file (str, optional): Path to specific config file
            model_name (str, optional): Name of model preset to use
        """
        self.config = {}

        # Load default configuration first
        self._load_default_config()

        # If model preset was specified, load it
        if model_name:
            self._load_model_preset(model_name)

        # If specific config file provided, load it (overrides defaults)
        if config_file and os.path.exists(config_file):
            self._load_config_file(config_file)

    def _get_config_dir(self):
        """Get the configuration directory path, handling different environments"""
        # First check if we're in a Docker container by checking if /app exists
        if os.path.exists('/app/Backend/config'):
            return '/app/Backend/config'

        # Otherwise use the default relative path
        return os.path.dirname(__file__)

    def _load_default_config(self):
        """Load the default configuration"""
        config_dir = self._get_config_dir()
        default_config_path = os.path.join(config_dir, 'default.yaml')

        if os.path.exists(default_config_path):
            self._load_config_file(default_config_path)
        else:
            logger.warning(f"Default config file not found: {default_config_path}")
            # Set some basic defaults
            self.config = {
                'model': {
                    'name': 'default'
                },
                'compression': {
                    'window_size': 64,
                    'min_chunk_size': 100,
                    'max_chunk_size': 500
                },
                'system': {
                    'log_level': 'quiet'
                }
            }

    def _load_model_preset(self, model_name):
        """
        Load a preset configuration for a specific model

        Args:
            model_name (str): Name of the model
        """
        config_dir = self._get_config_dir()
        model_config_path = os.path.join(config_dir, 'models', f"{model_name}.yaml")

        if os.path.exists(model_config_path):
            self._load_config_file(model_config_path)
        else:
            logger.warning(f"Model config not found for {model_name}: {model_config_path}")

    def _load_config_file(self, config_file):
        """
        Load configuration from YAML file

        Args:
            config_file (str): Path to the YAML config file
        """
        try:
            with open(config_file, 'r') as f:
                new_config = yaml.safe_load(f)

            if new_config:
                # Deep update the current config
                self._deep_update(self.config, new_config)
                logger.debug(f"Loaded configuration from {config_file}")

        except Exception as e:
            logger.error(f"Failed to load config file {config_file}: {e}")

    def _deep_update(self, target, source):
        """
        Recursively update a dictionary

        Args:
            target (dict): The dictionary to update
            source (dict): The dictionary with updates
        """
        for key, value in source.items():
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                self._deep_update(target[key], value)
            else:
                target[key] = value

    def get(self, key, default=None, section=None):
        """
        Get configuration value

        Args:
            key (str): Configuration key
            default: Default value if key is not found
            section (str, optional): Configuration section (can be nested with dots, e.g., 'model.parameters')

        Returns:
            Configuration value
        """
        if not section:
            return self.config.get(key, default)

        # Handle nested sections (e.g., 'model.parameters')
        sections = section.split('.')
        config_section = self.config

        # Navigate through the nested sections
        for sec in sections:
            if sec not in config_section:
                return default
            config_section = config_section[sec]

        # Get the value from the final section
        return config_section.get(key, default)

    def get_all(self):
        """
        Get the entire configuration

        Returns:
            dict: Complete configuration dictionary
        """
        return self.config

    # Model configuration methods
    def model_name(self):
        """Get the model name"""
        return self.get('name', 'default', section='model')

    # Compression configuration methods
    def window_size(self):
        """Get the window size for compression"""
        return self.get('window_size', 64, section='compression')

    def min_chunk_size(self):
        """Get the minimum chunk size for compression"""
        return self.get('min_chunk_size', 100, section='compression')

    def max_chunk_size(self):
        """Get the maximum chunk size for compression"""
        return self.get('max_chunk_size', 500, section='compression')

    # System configuration methods
    def log_level(self):
        """Get the logging level"""
        return self.get('log_level', 'quiet', section='system')