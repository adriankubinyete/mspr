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
            
    def launch_account(self, account, placeid, jobid, follow_user=False, join_vip=False, callback=None):
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
