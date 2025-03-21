
import requests
from lib.config import Config

class RAMWS:
    def __init__(self):
        pass
    
    @property
    def url(self):
        return Config.get("RAMWS", "ramws_url", fallback="localhost")
    
    @property
    def port(self):
        return Config.get("RAMWS", "ramws_port", fallback="80")
    
    @property
    def password(self):
        return Config.get("RAMWS", "ramws_password", fallback="")
    
    @property
    def password_enabled(self):
        return Config.get("RAMWS", "ramws_password_enabled", fallback="0") == "1"
    
    @property
    def ramws_full_url(self):
        return f"http://{self.url}:{self.port}"
    
    @property
    def ramws_password(self):
        if self.password_enabled:
            return f"Password={self.password}"
        else:
            return ""
    
    def test_connection(self):
        """Testa conexão com o RAM Webserver"""

        url = f"{self.ramws_full_url}/GetAccounts?{self.ramws_password}"
        print(f"Testing connection to {url}")

        try:
            response = requests.get(url, timeout=5)
            print(f"Response: {response}")
            return response.status_code == 200
        except requests.RequestException:
            return False
        
    def test(self):
        
        pass

    def get_accounts(self, password=None):
        pass
    
RAMWS = RAMWS()
        