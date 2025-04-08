"""
Example script demonstrating the use of the LLMPress configuration system
"""
import sys
import os

# Add the parent directory to the path so we can import from Backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Backend.config import ConfigLoader, get_preset

def print_section_header(title):
    """Print a formatted section header"""
    print("\n" + "=" * 50)
    print(f" {title}")
    print("=" * 50)

def main():
    """Main function demonstrating configuration usage"""
    # Load default configuration
    print_section_header("Default Configuration")
    config = ConfigLoader()
    
    print(f"Window Size: {config.window_size()}")
    print(f"Model Name: {config.model_name()}")
    print(f"Temperature: {config.temperature()}")
    print(f"Log Level: {config.log_level()}")
    print(f"Cache Enabled: {config.cache_enabled()}")
    
    # Load model-specific configuration
    print_section_header("GPT-3 Configuration")
    gpt3_config = get_preset("gpt3")
    
    print(f"Window Size: {gpt3_config.window_size()}")
    print(f"Model Name: {gpt3_config.model_name()}")
    print(f"Temperature: {gpt3_config.temperature()}")
    print(f"Log Level: {gpt3_config.log_level()}")
    print(f"Cache Enabled: {gpt3_config.cache_enabled()}")
    
    # Load custom configuration file
    print_section_header("Custom Configuration")
    custom_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                     "Backend", "config", "custom.yaml")
    
    # Create a simple custom config file for demonstration
    os.makedirs(os.path.dirname(custom_config_path), exist_ok=True)
    with open(custom_config_path, 'w') as f:
        f.write("""
# Custom configuration
compression:
  window_size: 256
  
performance:
  parallel_processing: false
  
system:
  log_level: "verbose"
        """)
    
    custom_config = ConfigLoader(config_file=custom_config_path)
    
    print(f"Window Size: {custom_config.window_size()}")
    print(f"Model Name: {custom_config.model_name()}")  # Should use default
    print(f"Temperature: {custom_config.temperature()}")  # Should use default
    print(f"Log Level: {custom_config.log_level()}")
    print(f"Parallel Processing: {custom_config.parallel_processing()}")
    
    # Clean up the custom config file
    os.remove(custom_config_path)

if __name__ == "__main__":
    main()
