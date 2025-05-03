
import configparser
import logging
import copy
from pathlib import Path

class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.config = configparser.ConfigParser()
        self.cached_config = None
        self.config_file = "config.ini"
        self.logger = logging.getLogger("mpsr.ConfigManager")
        
        # Create config file if it doesn't exist
        if not Path(self.config_file).exists():
            self.logger.info("Config file not found, creating new one")
            self._create_default_config()
        else:
            self.load()
            
    def _create_default_config(self):
        """Creates a new config file with default values"""
        self.config["General"] = {
            "url_webhook": "",
            "url_private_server": ""
        }
        self.save()
        
    def load(self):
        """Loads configuration from file"""
        self.logger.debug("Loading configuration")
        self.config.read(self.config_file)
        self.logger.debug("Configuration loaded successfully: %s", self.config.sections())
        self.cached_config = copy.deepcopy(self.config)
        
    def save(self):
        """Saves configuration to file if changes detected"""
        if self.cached_config and self.cached_config == self.config:
            self.logger.debug("No changes detected in configuration, skipping save")
            return
            
        self.logger.info("Saving configuration to file")
        with open(self.config_file, "w") as configfile:
            self.config.write(configfile)
            self.cached_config = copy.deepcopy(self.config)
            
    def get(self, section, key=None, fallback=None):
        """Gets a value from config or entire section"""
        if key is None:
            return self.config[section] if self.has_section(section) else fallback
        return self.config.get(section, key, fallback=fallback)
    
    def set(self, section, key, value):
        """Sets a value in config"""
        if not self.config.has_section(section):
            self.logger.debug(f"Creating new section: {section}")
            self.config.add_section(section)
            
        self.config.set(section, key, str(value))
    
    def remove_section(self, section):
        """Removes a section"""
        if self.has_section(section):
            self.config.remove_section(section)
        
    def has_section(self, section):
        """Checks if section exists"""
        return self.config.has_section(section)
    
    def get_sections(self):
        """Returns list of all sections"""
        return self.config.sections()
    

# Create singleton instance
Config = ConfigManager()
