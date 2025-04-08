# LLMPress Configuration System

This directory contains the configuration system for LLMPress. The configuration system is designed to be flexible and extensible, allowing you to customize various aspects of the system.

## Configuration Files

- `default.yaml`: Default configuration settings for all components
- `models/*.yaml`: Model-specific configuration presets

## Configuration Structure

The configuration is organized into the following sections:

### Model Configuration

```yaml
model:
  name: "default"                  # Model identifier
  path: null                       # Path to local model (null for API-based)
  api_key: null                    # API key (null to use environment variable)
  api_endpoint: null               # API endpoint (null for default)
  parameters:
    temperature: 0.7               # Controls randomness (0.0-2.0)
    top_p: 0.9                     # Nucleus sampling parameter (0.0-1.0)
    max_tokens: 1024               # Maximum tokens to generate
    stop_sequences: []             # List of sequences that stop generation
```

### Compression Settings

```yaml
compression:
  window_size: 64                  # Sliding context window size
  min_chunk_size: 100              # Minimum chunk size in bytes/tokens
  max_chunk_size: 500              # Maximum chunk size in bytes/tokens
  chunk_strategy: "fixed"          # Chunking strategy (fixed, semantic)
  break_token_frequency: 500       # How often to insert break tokens
```

### Performance Optimization

```yaml
performance:
  cache:
    enabled: true                  # Whether to use caching
    size: 1000                     # Maximum cache size
    ttl: 3600                      # Time-to-live for cached items (seconds)
  parallel_processing: true        # Whether to use parallel processing
  max_workers: 4                   # Maximum number of worker threads/processes
```

### System Settings

```yaml
system:
  log_level: "quiet"               # Logging level (quiet, normal, verbose, debug)
  output_format: "binary"          # Format for output files
  temp_directory: "./temp"         # Directory for temporary files
  retry:
    max_retries: 3                 # Maximum retry attempts
    retry_delay: 1                 # Initial delay between retries (seconds)
    backoff_factor: 2              # Exponential backoff factor
```

### Integration Settings

```yaml
integration:
  celery:
    broker_url: "redis://redis:6379/0"    # URL for Celery broker
    backend_url: null                     # URL for Celery result backend (null = same as broker)
  database:
    db_type: "sqlite"                     # Database type
    db_path: "./data/llmpress.db"         # Database path or connection string
```

## Using the Configuration System

### Basic Usage

```python
from Backend.config import ConfigLoader

# Load default configuration
config = ConfigLoader()

# Access configuration values
window_size = config.window_size()
log_level = config.log_level()
```

### Using Model Presets

```python
from Backend.config import get_preset

# Load configuration for a specific model
gpt3_config = get_preset("gpt3")

# Access model-specific configuration values
window_size = gpt3_config.window_size()
temperature = gpt3_config.temperature()
```

### Custom Configuration Files

```python
from Backend.config import ConfigLoader

# Load a custom configuration file
custom_config = ConfigLoader(config_file="path/to/custom_config.yaml")

# Access configuration values
window_size = custom_config.window_size()
```

## Creating Custom Configuration Files

You can create custom configuration files to override specific settings. You only need to include the settings you want to override:

```yaml
# custom_config.yaml
compression:
  window_size: 128

system:
  log_level: "verbose"
```

This will use the default values for all other settings.

## Rank Token System

Note that the rank token system is designed with a fixed 6-bit payload, supporting ranks 0-63. This is a static design choice and not configurable through the configuration system.
