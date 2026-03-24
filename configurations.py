"""Configuration management for Azure DevOps and Rado API settings."""

import yaml
from pathlib import Path
import os

# Path to the configuration file containing environment settings
CONFIG_FILE = Path(__file__).parents[0] / 'config.yaml'


def read_yml_file(file):
    """
    Reads and parses a YAML configuration file.

    Args:
        file: Path object pointing to the YAML file

    Returns:
        Dictionary containing the parsed YAML content
    """
    with file.open(mode='r') as file:
        return yaml.safe_load(file)

def deep_merge(base: dict, override: dict) -> dict:
    """deep merge on dicts"""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result

class AppSettings:
    """
    Loads and manages application configuration settings from YAML file.
    
    Reads environment-specific settings such as API URLs, organization names,
    and authentication tokens from the configuration file.
    """

    def __init__(self, config_yml,env: str | None = None):
        """
        Initialize application settings by reading the configuration file.

        Args:
            config_yml: Path object pointing to the config.yaml file
        """
        # Get the environment variable that defines which environment the application will run in
        self.env = env or os.getenv("APP_ENV", "default")
        config = read_yml_file(config_yml)
        settings = config.get("settings", {})

        if self.env not in settings:
            raise ValueError(f"Environment '{self.env}' not found in config.yaml")

        default_config = settings.get("default", {})
        temp_config = settings[self.env]

        #merge configurations to get the data that would be needed
        env_settings = deep_merge(default_config, temp_config)


        # Azure DevOps application URL
        self.application_url = env_settings['application_url']

        # Azure DevOps organization name
        self.azure_organization = env_settings['azure_organization']

        # API version for Azure DevOps (e.g., '7.0')
        self.api_version = env_settings['api_version']

        # Rado extension name (defaults to 'requirements' if not specified)
        self.extension_name = env_settings.get('extension_name', 'requirements')

        # Personal Access Token (PAT) for Azure DevOps authentication
        self.azure_auth_token = env_settings['azure_pat']


# Global instance of AppSettings loaded from config.yaml
TEST_ENV = AppSettings(config_yml=CONFIG_FILE)
