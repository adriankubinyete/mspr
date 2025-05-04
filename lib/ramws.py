import requests
import threading
import time
import logging
from collections import defaultdict
from lib.config import Config

class RAMWS:
    def __init__(self):
        self.keepalive_running = False  # Flag para parar o keepalive
        self.last_status = None  # Guarda o último status da conexão
    
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
        return f"Password={self.password}" if self.password_enabled else ""
    
    def __getLogger(self, name):
        return logging.getLogger("mpsr.lib:RAMWS." + name)
    
    def test_connection(self, timeout=3):
        """Testa conexão com o RAM Webserver (bloqueante)"""
        url = f"{self.ramws_full_url}/GetAccounts?{self.ramws_password}"
        try:
            response = requests.get(url, timeout=timeout)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def test_connection_async(self, callback, timeout=5):
        """Executa test_connection em uma thread separada e chama callback(status)"""
        def run():
            status = self.test_connection(timeout)
            callback(status)  # Chama a função passada com o resultado
        
        threading.Thread(target=run, daemon=True).start()

    def start_connection_checker(self, callback, interval=10):
        """Inicia um keepalive, verificando a conexão a cada 'interval' segundos"""
        l = self.__getLogger("ConnectionChecker")
        l.debug("Starting...")
        def run():
            self.keepalive_running = True
            while self.keepalive_running:
                status = self.test_connection()
                
                l.trace("WebServer is %s", "online" if status else "offline")
                
                # Só chama o callback se o status mudar
                if status != self.last_status:
                    self.last_status = status
                    callback(status)

                time.sleep(interval)

        threading.Thread(target=run, daemon=True).start()

    def stop_connection_checker(self):
        """Para o keepalive"""
        l = self.__getLogger("ConnectionChecker")
        l.debug("Stopping...")
        self.keepalive_running = False
        
    # --------------------------------------------
    # RAM API Methods

    def list_accounts(self, callback, timeout=5):
        """Lista as contas do usuário a partir do endpoint /GetAccounts."""
        l = self.__getLogger("list_accounts")
        l.debug("Listing accounts...")
        url = f"{self.ramws_full_url}/GetAccounts?{self.ramws_password}"
        
        try:
            # Tenta fazer a requisição
            response = requests.get(url, timeout=timeout)
            
            # Verifica o status da resposta
            if response.status_code == 200:
                # Se a resposta for texto, processamos como uma string
                accounts_text = response.text
                l.trace(f"Accounts: {accounts_text}")
                
                # Processa o texto em uma lista de contas, quebrando por vírgula
                accounts = accounts_text.split(',')
                
                # Retorna as contas para o callback
                callback(accounts)
            else:
                l.error(f"Error while listing accounts: {response.status_code}")
                callback([])  # Se a resposta não for 200, retorna uma lista vazia
                
        except requests.RequestException as e:
            # Caso ocorra uma exceção (como timeout, falha na rede, etc.)
            l.error(f"Error while listing accounts: {str(e)}")
            callback([])  # Caso ocorra uma exceção, retorna uma lista vazia
    
    
    def get_field(self, account, field, timeout=5):
        l = self.__getLogger("get_field")
        # l.debug(f"Getting field for account: {account}")

        url = f"{self.ramws_full_url}/GetField?{self.ramws_password}&Account={account}&Field={field}"

        return_data = None
        
        try:
            response = requests.get(url, timeout=timeout)
            ws_error = response.headers.get("ws-error", "")

            if not ws_error:
                return_data = response.text
            else:
                l.error(f"WS Error while getting field")
                return_data = None
        except requests.RequestException as e:
            l.error(f"Error while getting field: {str(e)}")
        
        return return_data
    
    
    def set_field(self, account, field, value, timeout=5):
        l = self.__getLogger("set_field")
        # l.debug(f"Setting field for account: {account}")
        
        url = f"{self.ramws_full_url}/SetField?{self.ramws_password}&Account={account}&Field={field}&Value={value}"
        
        return_data = None
        
        try:
            response = requests.get(url, timeout=timeout)
            ws_error = response.headers.get("ws-error", "")

            if not ws_error:
                return_data = True
            else:
                l.error(f"WS Error while setting field")
                return_data = False
        except requests.RequestException as e:
            l.error(f"Error while setting field: {str(e)}")
        
        return return_data
            
            
    def remove_field(self, account, field, timeout=5):
        l = self.__getLogger("remove_field")
        # l.debug(f"Removing field for account: {account}")

        url = f"{self.ramws_full_url}/RemoveField?{self.ramws_password}&Account={account}&Field={field}"

        return_data = None

        try:
            response = requests.get(url, timeout=timeout)
            ws_error = response.headers.get("ws-error", "")
            
            if not ws_error:
                return_data = True
            else:
                l.error(f"WS Error while removing field")
                return_data = False
        except requests.RequestException as e:
            l.error(f"Error while removing field: {str(e)}")

        return return_data


    def get_account_info(self, account, timeout=10):
        l = self.__getLogger("get_account_info")
        # l.debug(f"Getting account info for account: {account}")
            
            
    # Dangerous! Needs "Configuration > Developer > Allow GetCookie Method" to be enabled on RAM
    def get_cookie(self, account):
        l = self.__getLogger("get_cookie")
        #l.debug(f"Getting cookie for account: {account}")
        
        url = f"{self.ramws_full_url}/GetCookie?{self.ramws_password}&Account={account}"
        
        return_data = None
        
        try:
            response = requests.get(url, timeout=10)
            ws_error = response.headers.get("ws-error", "")

            if not ws_error:
                # success
                return_data = response.text
            else:
                # error
                l.error(f"WS Error while getting cookie")
        except requests.RequestException as e:
            l.error(f"Error while getting cookie: {str(e)}")
        
        return return_data
        
        
    # Dangerous! (i think it) Needs "Configuration > Developer > Allow GetCookie Method" to be enabled on RAM
    def get_csrf_token(self, account):
        """Obtains the CSRF token for the given account."""
        l = self.__getLogger("get_csrf_token")
        # l.debug(f"Getting CSRF token for account: {account}")
        
        url = f"{self.ramws_full_url}/GetCSRFToken?{self.ramws_password}&Account={account}"
        
        return_data = None
        
        try:
            response = requests.get(url, timeout=10)
            ws_error = response.headers.get("ws-error", "")
            
            if not ws_error:
                # success
                l.trace(f"{account}'s CSRF Token: {response.text[0]}{'*' * (len(response.text) - 2)}{response.text[-1]}")
                # return_data["success"] = True
                return_data = response.text
            else:
                # failed
                # return_data["error"] = ws_error
                l.error(f"WS Error while getting CSRF Token")
                pass
        except requests.RequestException as e:
            l.error(f"{account} : Failed to get CSRF Token: {str(e)}")
            # return_data["error"] = str(e)

        return return_data
          
          
    # This is a custom, utilitary method that does not exist in RAMWS as of now.
    # Converts a roblox.com/share link into a privateServerCode, using a csrf_token.
    def resolve_share_link(self, resolver_account, url, timeout=10):
        """Converts a roblox.com/share link into a privateServerCode, through an account that will be "sessioned" to resolve our link.

        Args:
            resolver_account (string): Account that will be used to resolve the link. (will use the account's cookies and csrf token, obtained through RAMWS)
            url (string): The link to be resolved.
            timeout (int, optional): Maximum time (in seconds) to wait for link-resolving request. Defaults to 10.

        Raises:
            ValueError: If the shared_link is not a valid roblox.com/share link.

        Returns:
            _type_: _description_
        """
        l = self.__getLogger("shareLinkResolver")
        l.debug(f"Extracting server code from shared link: {url}")
        
        # validate it is a valid link:
        if not str(url).lower().startswith("https://www.roblox.com/share?code=") and not str(url).lower().endswith("&type=server"):
            raise ValueError(f"Invalid share link: {url}")
        
        # authenticated session to make the request
        session = requests.Session()
        session.cookies.set(
            name=".ROBLOSECURITY",
            value=self.get_cookie(resolver_account),
            domain=".roblox.com"
        )
        
        headers = {
            "X-CSRF-TOKEN": self.get_csrf_token(resolver_account),
            "Content-Type": "application/json"
        }
        payload = {
            "linkId": url.split("code=")[1].split("&")[0], # https://www.roblox.com/share?code=00e1ce0a27ab7142bde4aec006b57f01&type=Server
            "linkType": "Server"
        }
        
        
        try:
            response = session.post("https://apis.roblox.com/sharelinks/v1/resolve-link", headers=headers, json=payload, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            l.trace(f"\"{url}\": {data}")
            
            server_data = data.get("privateServerInviteData")
            if server_data and server_data.get("status") == "Valid":
                l.test("Link is valid")
                return server_data.get("linkCode")
            else:
                l.test("Link is invalid")
                return None

        except Exception as e:
            l.error(f"Error while extracting server code: {str(e)}")
            return None
    
        
    def launch_account(self, account, placeid, jobid, return_server_code=False, follow_user=False, join_vip=False, callback=None):
        """Inicia uma conta a partir do endpoint /LaunchAccount."""
        l = self.__getLogger("launch_account")
        l.debug(f"Launching account: {account}")

        url = f"{self.ramws_full_url}/LaunchAccount?{self.ramws_password}&Account={account}&PlaceID={placeid}&JobID={jobid}&FollowUser={follow_user}&JoinVIP={join_vip}"

        return_data = {
            "account": account,
            "placeid": placeid,
            "jobid": jobid,
            "follow_user": follow_user,
            "join_vip": join_vip,
            "success": False,  # Assume falha por padrão
            "error": None
        }

        try:
            # Tenta fazer a requisição
            response = requests.get(url, timeout=10)

            # Verifica se há um erro no cabeçalho "ws-error"
            ws_error = response.headers.get("ws-error", "")
            
            if not ws_error:
                # Se "ws-error" estiver vazio, a operação foi bem-sucedida
                l.info(f"Successfully launched account: {account}")
                return_data["success"] = True
            else:
                # Se houver erro, loga e adiciona ao return_data
                l.error(f"Failed to launch account {account}. Server error: {ws_error}")
                return_data["error"] = ws_error

        except requests.RequestException as e:
            # Captura falhas de conexão, timeout, etc.
            l.error(f"Error while launching account {account}: {str(e)}")
            return_data["error"] = str(e)

        # Se houver callback, passa os dados
        if callback:
            callback(return_data)

        return return_data

RAMWS = RAMWS()
