import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
import yaml
import json
import toml  # You might need to install 'toml' package: pip install toml
import configparser
from dotenv import load_dotenv
from loguru import logger


class ConfigManager(BaseSettings):
    """
    A unified configuration manager that loads settings from various sources:
    1. Environment variables (highest priority)
    2. Dotenv files (.env)
    3. Configuration files (YAML, JSON, TOML, INI)
    4. Default values (lowest priority)

    This class uses Pydantic Settings for validation and type conversion.
    """

    # Example settings - you should define your own based on your project's needs
    app_name: str = Field(default="MyApp", description="Name of the application")
    debug: bool = Field(default=False, description="Enable debug mode")
    database_url: str = Field(
        default="sqlite:///./test.db", description="Database connection string"
    )
    api_key: Optional[str] = Field(
        default=None, description="API key for external services"
    )
    max_workers: int = Field(
        default=4, description="Maximum number of worker threads/processes"
    )

    # Pydantic Settings configuration
    model_config = SettingsConfigDict(
        # Load environment variables with a prefix
        env_prefix="MYAPP_",
        # Case sensitivity for environment variables
        case_sensitive=False,
        # Extra fields not specified in the model will be ignored
        extra="ignore",
    )

    @classmethod
    def load_from_file(cls, file_path: Union[str, Path], **kwargs) -> "ConfigManager":
        """
        Load configuration from a file.

        Args:
            file_path: Path to the configuration file.
            **kwargs: Additional keyword arguments passed to the ConfigManager constructor.

        Returns:
            An instance of ConfigManager with settings loaded from the file.
        """
        path = Path(file_path)
        if not path.exists():
            logger.warning(
                f"Configuration file {path} does not exist. Loading with defaults and environment variables only."
            )
            return cls(**kwargs)

        try:
            with open(path, "r", encoding="utf-8") as f:
                if path.suffix.lower() in [".yml", ".yaml"]:
                    data = yaml.safe_load(f) or {}
                elif path.suffix.lower() == ".json":
                    data = json.load(f)
                elif path.suffix.lower() == ".toml":
                    data = toml.load(f)
                elif path.suffix.lower() in [".ini", ".cfg"]:
                    config = configparser.ConfigParser()
                    config.read_file(f)
                    data = {
                        k: v
                        for section in config.sections()
                        for k, v in config.items(section)
                    }
                else:
                    logger.error(
                        f"Unsupported configuration file format: {path.suffix}"
                    )
                    raise ValueError(
                        f"Unsupported configuration file format: {path.suffix}"
                    )

            # Merge file data with any additional kwargs
            data.update(kwargs)
            return cls(**data)
        except Exception as e:
            logger.error(f"Failed to load configuration from {path}: {e}")
            raise

    @classmethod
    def load_from_env_and_defaults(
        cls, dotenv_path: Optional[Union[str, Path]] = None, **kwargs
    ) -> "ConfigManager":
        """
        Load configuration from environment variables and defaults.
        Optionally loads a .env file first.

        Args:
            dotenv_path: Path to the .env file. If None, looks for .env in current directory.
            **kwargs: Additional keyword arguments passed to the ConfigManager constructor.

        Returns:
            An instance of ConfigManager.
        """
        if dotenv_path:
            load_dotenv(dotenv_path)
        else:
            # Try to load .env from current directory
            env_path = Path(".env")
            if env_path.exists():
                load_dotenv(env_path)

        return cls(**kwargs)

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Custom validator for database URL."""
        if not v:
            return v
        # Simple check for common prefixes
        valid_prefixes = ("sqlite://", "postgresql://", "mysql://", "mongodb://")
        if not any(v.startswith(prefix) for prefix in valid_prefixes):
            logger.warning(
                f"Database URL '{v}' does not start with a recognized prefix."
            )
        return v


def get_config(
    config_file_path: Optional[Union[str, Path]] = None,
    dotenv_path: Optional[Union[str, Path]] = None,
    **kwargs,
) -> ConfigManager:
    """
    A convenient function to get the application configuration.

    The loading order is:
    1. Default values
    2. Configuration file (if provided)
    3. .env file (if provided or .env exists in current dir)
    4. Environment variables
    5. Keyword arguments (highest priority)

    Args:
        config_file_path: Path to the configuration file (YAML, JSON, TOML, INI).
        dotenv_path: Path to the .env file.
        **kwargs: Additional settings to override all other sources.

    Returns:
        An instance of ConfigManager with all settings loaded.
    """
    # Start with default values
    config_data = {}

    # 1. Load from configuration file if provided
    if config_file_path:
        try:
            file_path = Path(config_file_path)
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    if file_path.suffix.lower() in [".yml", ".yaml"]:
                        file_data = yaml.safe_load(f) or {}
                    elif file_path.suffix.lower() == ".json":
                        file_data = json.load(f)
                    elif file_path.suffix.lower() == ".toml":
                        file_data = toml.load(f)
                    elif file_path.suffix.lower() in [".ini", ".cfg"]:
                        config = configparser.ConfigParser()
                        config.read_file(f)
                        file_data = {
                            k: v
                            for section in config.sections()
                            for k, v in config.items(section)
                        }
                    else:
                        logger.error(
                            f"Unsupported configuration file format: {file_path.suffix}"
                        )
                        raise ValueError(
                            f"Unsupported configuration file format: {file_path.suffix}"
                        )
                config_data.update(file_data)
            else:
                logger.warning(f"Configuration file {config_file_path} does not exist.")
        except Exception as e:
            logger.error(f"Error loading config from file {config_file_path}: {e}")
            raise

    # 2. Load .env file if provided or .env exists in current directory
    if dotenv_path:
        load_dotenv(dotenv_path)
    else:
        env_path = Path(".env")
        if env_path.exists():
            load_dotenv(env_path)

    # 3. Update with any additional kwargs (highest priority)
    config_data.update(kwargs)

    # Create ConfigManager instance, which will automatically load from env vars
    return ConfigManager(**config_data)
