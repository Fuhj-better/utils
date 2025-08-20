# Configuration Manager Usage Examples

This document provides examples of how to use the `config_manager.py` module.

## 1. Basic Usage with Defaults

```python
from config_manager import get_config

# Load configuration with default values only
config = get_config()
print(f"App Name: {config.app_name}")
print(f"Debug Mode: {config.debug}")
```

## 2. Using Environment Variables

Create a `.env` file in your project root:

```env
MYAPP_DEBUG=true
MYAPP_API_KEY=your_secret_api_key
MYAPP_MAX_WORKERS=10
```

Then load the configuration:

```python
from config_manager import get_config

# Load configuration from defaults and environment variables
config = get_config()
print(f"Debug Mode: {config.debug}")  # True
print(f"API Key: {config.api_key}")    # your_secret_api_key
print(f"Max Workers: {config.max_workers}")  # 10
```

## 3. Using a Configuration File (YAML)

Create a `config.yaml` file:

```yaml
app_name: "MyProductionApp"
debug: false
database_url: "postgresql://user:password@localhost/prod_db"
max_workers: 16
```

Then load the configuration:

```python
from config_manager import get_config

# Load configuration from a YAML file
config = get_config(config_file_path="config.yaml")
print(f"App Name: {config.app_name}")  # MyProductionApp
print(f"Debug Mode: {config.debug}")   # False
print(f"Database URL: {config.database_url}")
print(f"Max Workers: {config.max_workers}")  # 16
```

## 4. Combining Environment Variables and Configuration File

You can use both environment variables and a configuration file together. Environment variables will override settings from the file.

With `.env`:
```env
MYAPP_DEBUG=true
```

And `config.yaml`:
```yaml
app_name: "MyApp"
debug: false
max_workers: 4
```

Code:
```python
from config_manager import get_config

# Load configuration from both file and environment variables
config = get_config(config_file_path="config.yaml")
print(f"App Name: {config.app_name}")  # MyApp (from file)
print(f"Debug Mode: {config.debug}")   # True (from env, overrides file)
print(f"Max Workers: {config.max_workers}")  # 4 (from file)
```

## 5. Overriding with Keyword Arguments

You can also override any setting using keyword arguments:

```python
from config_manager import get_config

# Override settings with keyword arguments
config = get_config(debug=True, api_key="overridden_key")
print(f"Debug Mode: {config.debug}")  # True
print(f"API Key: {config.api_key}")    # overridden_key
```