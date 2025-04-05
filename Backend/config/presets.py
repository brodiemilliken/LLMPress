"""
Configuration Presets for LLMPress

Provides easy access to model-specific configuration presets
"""
import os
from .config_loader import ConfigLoader

# Dictionary of available presets
AVAILABLE_PRESETS = {
    'gpt2': 'GPT2',
    'default': 'Default'
}

def get_preset(preset_name=None):
    """
    Get configuration for a specific preset
    
    Args:
        preset_name (str, optional): Name of the preset to load (default will use default config)
        
    Returns:
        ConfigLoader: Configuration loader with preset loaded
    """
    if preset_name and preset_name.lower() in AVAILABLE_PRESETS:
        return ConfigLoader(model_name=preset_name.lower())
    
    # If not found or not specified, return default config
    return ConfigLoader()