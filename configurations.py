"""Configuration management for Azure DevOps and Rado API settings."""

import yaml
from pathlib import Path

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
        return yaml.load(file, Loader=yaml.FullLoader)


class AppSettings:
    """
    Loads and manages application configuration settings from YAML file.
    
    Reads environment-specific settings such as API URLs, organization names,
    and authentication tokens from the configuration file.
    """

    def __init__(self, config_yml):
        """
        Initialize application settings by reading the configuration file.

        Args:
            config_yml: Path object pointing to the config.yaml file
        """
        obj = read_yml_file(config_yml)
        env_settings = obj['settings']['env']
        
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
