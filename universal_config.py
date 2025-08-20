import os
from pathlib import Path
from typing import Any, Dict, Optional, Union, List
import yaml
import json
import toml
import configparser
from dotenv import load_dotenv


class UniversalConfig:
    """
    A universal configuration loader that can handle various file formats
    (YAML, JSON, TOML, INI) and environment variables.
    """

    def __init__(self):
        self._config = {}

    def load_file(self, file_path: Union[str, Path]) -> "UniversalConfig":
        """
        Load configuration from a file.

        Args:
            file_path: Path to the configuration file.

        Returns:
            Self for method chaining.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

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
                    raise ValueError(
                        f"Unsupported configuration file format: {path.suffix}"
                    )

                self._merge_dict(self._config, data)
        except Exception as e:
            raise RuntimeError(f"Failed to load configuration from {path}: {e}")

        return self

    def load_env(
        self, dotenv_path: Optional[Union[str, Path]] = None
    ) -> "UniversalConfig":
        """
        Load configuration from environment variables or .env file.

        Args:
            dotenv_path: Path to the .env file. If None, looks for .env in current directory.

        Returns:
            Self for method chaining.
        """
        # Load .env file if specified or if .env exists in current directory
        if dotenv_path:
            load_dotenv(dotenv_path)
        else:
            env_path = Path(".env")
            if env_path.exists():
                load_dotenv(env_path)

        # Load all environment variables
        env_vars = dict(os.environ)
        self._merge_dict(self._config, env_vars)
        return self

    def load_dict(self, data: Dict[str, Any]) -> "UniversalConfig":
        """
        Load configuration from a dictionary.

        Args:
            data: Configuration data as a dictionary.

        Returns:
            Self for method chaining.
        """
        self._merge_dict(self._config, data)
        return self

    def set(self, key: str, value: Any) -> "UniversalConfig":
        """
        Set a configuration value.

        Args:
            key: Configuration key (can use dot notation for nested keys, e.g., 'database.host').
            value: Configuration value.

        Returns:
            Self for method chaining.
        """
        self._set_nested_value(self._config, key, value)
        return self

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key (can use dot notation for nested keys, e.g., 'database.host').
            default: Default value to return if key is not found.

        Returns:
            Configuration value or default.
        """
        return self._get_nested_value(self._config, key, default)

    def get_as(self, key: str, as_type: type, default: Any = None) -> Any:
        """
        Get a configuration value and convert it to the specified type.

        Args:
            key: Configuration key.
            as_type: Type to convert the value to.
            default: Default value to return if key is not found or conversion fails.

        Returns:
            Configuration value converted to the specified type, or default.
        """
        value = self.get(key, default)
        if value is default:
            return default

        try:
            # Special handling for boolean values from strings
            if as_type is bool and isinstance(value, str):
                return value.lower() in ("true", "1", "yes", "on")
            return as_type(value)
        except (ValueError, TypeError):
            return default

    def get_dict(self, prefix: str = "") -> Dict[str, Any]:
        """
        Get a dictionary of all configuration values with an optional key prefix.

        Args:
            prefix: Optional key prefix to filter values.

        Returns:
            Dictionary of configuration values.
        """
        if not prefix:
            return self._config.copy()

        result = {}
        prefix_with_dot = prefix + "."
        for key, value in self._config.items():
            if key.startswith(prefix_with_dot):
                result[key[len(prefix_with_dot) :]] = value
            elif key == prefix:
                result[""] = value
        return result

    def exists(self, key: str) -> bool:
        """
        Check if a configuration key exists.

        Args:
            key: Configuration key.

        Returns:
            True if the key exists, False otherwise.
        """
        return self._get_nested_value(self._config, key, None) is not None

    def _merge_dict(self, target: Dict, source: Dict) -> None:
        """Recursively merge source dictionary into target dictionary."""
        for key, value in source.items():
            if (
                key in target
                and isinstance(target[key], dict)
                and isinstance(value, dict)
            ):
                self._merge_dict(target[key], value)
            else:
                target[key] = value

    def _set_nested_value(self, data: Dict, key: str, value: Any) -> None:
        """Set a nested value using dot notation."""
        keys = key.split(".")
        for k in keys[:-1]:
            if k not in data or not isinstance(data[k], dict):
                data[k] = {}
            data = data[k]
        data[keys[-1]] = value

    def _get_nested_value(self, data: Dict, key: str, default: Any) -> Any:
        """Get a nested value using dot notation."""
        keys = key.split(".")
        for k in keys:
            if isinstance(data, dict) and k in data:
                data = data[k]
            else:
                return default
        return data


def load_config(
    config_file_path: Optional[Union[str, Path]] = None,
    dotenv_path: Optional[Union[str, Path]] = None,
    **kwargs,
) -> UniversalConfig:
    """
    A convenient function to load configuration from various sources.

    Args:
        config_file_path: Path to the configuration file.
        dotenv_path: Path to the .env file.
        **kwargs: Additional configuration values.

    Returns:
        An instance of UniversalConfig with all settings loaded.
    """
    config = UniversalConfig()

    # Load from configuration file
    if config_file_path:
        config.load_file(config_file_path)

    # Load from .env file and environment variables
    config.load_env(dotenv_path)

    # Load from keyword arguments
    if kwargs:
        config.load_dict(kwargs)

    return config
