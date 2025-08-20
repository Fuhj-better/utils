import sys
import os

# Add the parent directory to the path so we can import universal_config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import os
from universal_config import load_config


def test_universal_config():
    """Test the universal configuration loader."""
    print("Testing universal configuration loader...")

    # Load configuration from file, .env, and kwargs
    config = load_config(
        config_file_path="test_config.yaml",
        app_name="OverriddenAppName",
        new_key="new_value",
    )

    # Test getting values
    print(f"App name: {config.get('app.name')}")  # From YAML file
    print(f"APP_ENV: {config.get('APP_ENV')}")
    print(f"App version: {config.get('app.version')}")  # From YAML file
    print(f"Debug mode: {config.get_as('DEBUG', bool)}")  # From .env file (as boolean)
    print(
        f"Database host: {config.get('DATABASE_HOST')}"
    )  # From .env file (overrides YAML)
    print(
        f"Database port: {config.get_as('DATABASE_PORT', int)}"
    )  # From .env file (as integer)
    print(f"API key: {config.get('API_KEY')}")  # From .env file
    print(f"API timeout: {config.get_as('api.timeout', int)}")  # From YAML file
    print(f"Features: {config.get('features')}")  # From YAML file (list)
    print(f"Nested value: {config.get('nested.level1.level2.value')}")  # From YAML file
    print(f"Overridden app name: {config.get('app_name')}")  # From kwargs
    print(f"New key: {config.get('new_key')}")  # From kwargs

    # Test default values
    print(
        f"Non-existent key with default: {config.get('non.existent.key', 'default_value')}"
    )
    print(
        f"Non-existent key as int with default: {config.get_as('non.existent.key', int, 42)}"
    )

    # Test existence check
    print(f"Check if 'app.name' exists: {config.exists('app.name')}")
    print(f"Check if 'non.existent.key' exists: {config.exists('non.existent.key')}")

    # Test getting dictionary with prefix
    db_config = config.get_dict("database")
    print(f"Database config: {db_config}")

    # Test getting dictionary without prefix (all config)
    all_config = config.get_dict()
    print(f"Number of config items: {all_config}")

    print("Universal configuration loader test passed.")


if __name__ == "__main__":
    test_universal_config()
