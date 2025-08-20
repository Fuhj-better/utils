test_content = '''import os
import tempfile
import yaml
from config_manager import get_config


def test_defaults():
    """Test loading configuration with defaults only."""
    print("Testing defaults...")
    config = get_config()
    print(f"  App Name: {config.app_name}")
    print(f"  Debug: {config.debug}")
    print(f"  Database URL: {config.database_url}")
    print("  Defaults test passed.\n")


def test_with_yaml_file():
    """Test loading configuration from a YAML file."""
    print("Testing with YAML file...")
    
    # Create a temporary YAML file
    yaml_data = {
        "app_name": "TestApp",
        "debug": True,
        "database_url": "postgresql://localhost/testdb",
        "max_workers": 10
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(yaml_data, f)
        yaml_file_path = f.name
    
    try:
        config = get_config(config_file_path=yaml_file_path)
        assert config.app_name == "TestApp"
        assert config.debug is True
        assert config.database_url == "postgresql://localhost/testdb"
        assert config.max_workers == 10
        print(f"  App Name: {config.app_name}")
        print(f"  Debug: {config.debug}")
        print(f"  Database URL: {config.database_url}")
        print(f"  Max Workers: {config.max_workers}")
        print("  YAML file test passed.\n")
    finally:
        # Clean up the temporary file
        os.unlink(yaml_file_path)


def test_with_env_vars():
    """Test loading configuration from environment variables."""
    print("Testing with environment variables...")
    
    # Set environment variables
    os.environ["MYAPP_DEBUG"] = "true"
    os.environ["MYAPP_API_KEY"] = "my_secret_key"
    os.environ["MYAPP_MAX_WORKERS"] = "20"
    
    try:
        config = get_config()
        assert config.debug is True
        assert config.api_key == "my_secret_key"
        assert config.max_workers == 20
        print(f"  Debug: {config.debug}")
        print(f"  API Key: {config.api_key}")
        print(f"  Max Workers: {config.max_workers}")
        print("  Environment variables test passed.\n")
    finally:
        # Clean up environment variables
        del os.environ["MYAPP_DEBUG"]
        del os.environ["MYAPP_API_KEY"]
        del os.environ["MYAPP_MAX_WORKERS"]


def test_precedence():
    """Test that keyword arguments take precedence over files and env vars."""
    print("Testing precedence (kwargs > env vars > file > defaults)...")
    
    # Set environment variables
    os.environ["MYAPP_DEBUG"] = "false"
    os.environ["MYAPP_MAX_WORKERS"] = "15"
    
    # Create a temporary YAML file
    yaml_data = {
        "app_name": "PrecedenceTestApp",
        "debug": True,  # This should be overridden by env var, then by kwarg
        "max_workers": 5  # This should be overridden by env var, then by kwarg
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(yaml_data, f)
        yaml_file_path = f.name
    
    try:
        # Load config with file, env vars, and kwargs
        config = get_config(
            config_file_path=yaml_file_path,
            debug=True,  # Override env var
            max_workers=25  # Override env var
        )
        
        # Check that kwargs took precedence
        assert config.app_name == "PrecedenceTestApp"  # From file
        assert config.debug is True   # From kwarg (highest precedence)
        assert config.max_workers == 25  # From kwarg (highest precedence)
        
        print(f"  App Name: {config.app_name} (from file)")
        print(f"  Debug: {config.debug} (from kwargs)")
        print(f"  Max Workers: {config.max_workers} (from kwargs)")
        print("  Precedence test passed.\n")
    finally:
        # Clean up
        os.unlink(yaml_file_path)
        del os.environ["MYAPP_DEBUG"]
        del os.environ["MYAPP_MAX_WORKERS"]


if __name__ == "__main__":
    print("Running simple configuration manager tests...\n")
    test_defaults()
    test_with_yaml_file()
    test_with_env_vars()
    test_precedence()
    print("All tests completed successfully!")
'''

with open('simple_config_test.py', 'w') as f:
    f.write(test_content)