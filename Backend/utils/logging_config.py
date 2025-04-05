import logging
import os

# Predefined logging configurations
LOGGING_PRESETS = {
    "quiet": {
        "level": logging.ERROR,
        "keywords": [],
        "loggers": []
    },
    "normal": {
        "level": logging.WARNING,
        "keywords": ["error", "fail"],
        "loggers": []
    },
    "verbose": {
        "level": logging.INFO,
        "keywords": ["error", "fail", "success", "completed"],
        "loggers": ["LLMPress.Compressor", "LLMPress.Decompressor"]
    },
    "debug": {
        "level": logging.DEBUG,
        "keywords": ["error", "fail", "success", "completed", "started", "processed"],
        "loggers": ["LLMPress"]  # Root logger for all LLMPress modules
    }
}

class MessageFilter(logging.Filter):
    """Filter that allows messages containing specific keywords or from specific loggers"""
    
    def __init__(self, allowed_keywords=None, allowed_loggers=None):
        self.allowed_keywords = allowed_keywords or []
        self.allowed_loggers = allowed_loggers or []
        
    def filter(self, record):
        # Always show messages from allowed loggers
        if any(record.name.startswith(logger) for logger in self.allowed_loggers):
            return True
            
        # Show messages containing any of the allowed keywords
        if any(keyword in record.getMessage().lower() for keyword in self.allowed_keywords):
            return True
            
        # Filter out messages below ERROR level that don't match criteria
        return record.levelno >= logging.ERROR

def configure_logging(mode="normal"):
    """
    Configure logging with a single mode parameter
    
    Args:
        mode: Either a string preset name ("quiet", "normal", "verbose", "debug")
              or a boolean (False=quiet, True=verbose)
    
    Returns:
        The configured logger
    """
    # Handle boolean input (convert to preset name)
    if isinstance(mode, bool):
        mode = "verbose" if mode else "quiet"
    
    # Get configuration from preset
    config = LOGGING_PRESETS.get(mode, LOGGING_PRESETS["normal"])
    
    # Configure using detailed function
    return configure_project_logging(
        config["level"], 
        config["keywords"], 
        config["loggers"]
    )

def configure_project_logging(level=logging.WARNING, 
                             show_keywords=None, 
                             show_loggers=None):
    """Configure project-wide logging with filtering options"""
    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add console handler with custom formatter
    console = logging.StreamHandler()
    console.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    
    # Add message filter if keywords or loggers specified
    if show_keywords or show_loggers:
        message_filter = MessageFilter(show_keywords, show_loggers)
        console.addFilter(message_filter)
    
    root_logger.addHandler(console)
    
    return root_logger