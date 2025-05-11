import threading
import time
from collections import defaultdict
from pathlib import Path
from lib.cache import Cache
import requests
import logging
import re

c = Cache()

class FileWatcher(threading.Thread):
    def __init__(self, file_path, callback):
        super().__init__(daemon=True)
        self.file_path = file_path
        self.callback = callback
        self._running = True

        # Define a posição inicial como o tamanho atual do arquivo,
        # para ignorar tudo que já existe nele
        try:
            with open(self.file_path, "r", encoding="utf-8", errors="ignore") as f:
                f.seek(0, 2)  # vai para o fim do arquivo
                self._position = f.tell()
        except FileNotFoundError:
            self._position = 0

    def stop(self):
        self._running = False

    def run(self):
        while self._running:
            try:
                with open(self.file_path, "r", encoding="utf-8", errors="ignore") as f:
                    f.seek(self._position)
                    new_lines = f.readlines()
                    if new_lines:
                        for line in new_lines:
                            try:
                                # Adiciona o nome do arquivo na linha de log
                                self.callback(self.file_path, line.rstrip("\n"))
                            except Exception as cb_err:
                                logging.getLogger("mpsr.Callback").error(
                                    f"Erro na callback para {self.file_path}:\n{cb_err}"
                                )
                    self._position = f.tell()
            except Exception as file_err:
                logging.getLogger("mpsr.FileWatcher").error(
                    f"Erro ao ler o arquivo {self.file_path}: {file_err}"
                )
                raise file_err
            time.sleep(0.1)



class RoLogReader:
    def __init__(self):
        self.LOG_NAME = "mpsr.RoLogReader"
        self._accounts = defaultdict(list)
        self.RUNNING = False
        self.LOG_DIRECTORY = Path.home() / "AppData" / "Local" / "Roblox" / "Logs" # where is roblox logs located
        self.USERID_PATTERN = re.compile(r"FLog::GameJoinLoadTime.*userid:(\d+),") # pattern to identify user id
        self._watching = {}  # file path -> FileWatcher

    # public methods

    def start(self):
        if self.RUNNING:
            return
        self.RUNNING = True
        threading.Thread(target=self._watch_loop, daemon=True).start()

    def stop(self):
        self.RUNNING = False
        for watcher in self._watching.values():
            watcher.stop()
        self._watching.clear()
        
    def set_callback(self, username, callback):
        self._accounts[username.lower()].append(callback)
    
    def del_callback(self, username):
        if username.lower() in self._accounts:
            del self._accounts[username.lower()]

    # private methods (should not be called directly; internal components)
    
    def __getLogger(self, name):
        return logging.getLogger(f"{self.LOG_NAME}.{name}")

    def _watch_loop(self):
        logger = self.__getLogger("_watch_loop")
        logger.debug("Starting log watcher loop.")
        FLAG_ALREADY_REPORTED = False # to send "No accounts to monitor" only once
        while self.RUNNING:
            
            # checking if there are callbacks registered, else, its useless to keep running
            if not self._accounts:
                if not FLAG_ALREADY_REPORTED:
                    FLAG_ALREADY_REPORTED = True
                    logger.debug("No accounts to monitor.")
                time.sleep(5)
                continue
            FLAG_ALREADY_REPORTED = False
            
            for file in self._get_log_files():
                if file not in self._watching and file not in c.get("deadlogs", fallback=[]):
                    logger.debug(f"Starting monitor {file.name} : {self._identify_username_from_log_file(file)}")
                    c.set("usernameFromLog:"+file.name, self._identify_username_from_log_file(file))
                    
                    watcher = FileWatcher(file, self._dispatch_line)
                    self._watching[file] = watcher
                    watcher.start()
                else:
                    # already being monitored
                    pass
                
            time.sleep(5)  # checa por novos arquivos a cada 5s

    def _dispatch_line(self, logfile_path, line):
        logger = self.__getLogger("_dispatch_line")
        
        logfile_name = logfile_path.name
        # Aqui você trata a linha nova, incluindo o nome do arquivo
        # ignore lines that contain FLog::WndProcessCheck
        IGNORE_LINES = ["FLog::WndProcessCheck"]
        if any(ignore in line for ignore in IGNORE_LINES):
            return
        
        username = c.get(f"usernameFromLog:{logfile_name}", fallback=None)
        if username is None:
            logger.warning(f"No username found for {logfile_name}")
            
            # stop the file watcher
            watcher = self._watching.pop(logfile_path)
            watcher.stop()
            
            # mark as a dead file (so we dont watch it again)
            deadlogs = c.get("deadlogs", fallback=[])
            deadlogs.append(logfile_path)
            c.set("deadlogs", deadlogs)
            
            return
        
        # check if theres a callback for that username: if theres a callback, call it
        if username in self._accounts:
            # self.__getLogger(f"_dispatch_line.live.{username}").info(f"{line}")
            for callback in self._accounts[username]:
                callback(line)
            return
        
        # self.__getLogger(f"_dispatch_line.dead.{username}").debug(f"{line}")
        

    def _get_log_files(self):
        return [
            file for file in self.LOG_DIRECTORY.glob("*.log")
            if "Player" in file.name and file.name.endswith("_last.log")
        ]

    def _identify_username_from_log_file(self, file_name):
        logger = self.__getLogger("_identify_username_from_log_file")
        
        userid = self._identify_userid_from_log_file(file_name)
        if userid is None:
            return None

        return self._get_username_from_userid(userid)
            

    def _identify_userid_from_log_file(self, file_name):
        logger = self.__getLogger("_identify_userid_from_log_file")
        with open(file_name, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                match = self.USERID_PATTERN.search(line)
                if match:
                    return match.group(1)
        logger.warning(f"Failed to identify userid from {file_name}")
        return None
    
    def _get_username_from_userid(self, userid):
        """
        Receives an userid and returns the username, requesting through Roblox's API.
        Stores in cache.
        PS: Probably can't handle username changes. Hopefully you don't change your username while using the app.
        """
        logger = self.__getLogger("_get_username_from_userid")

        # Verifica no cache com TTL
        cached = c.get("usernameFromUserid:"+userid)
        if cached is not None:
            return cached

        try:
            logger.debug(f"Requesting username for userid {userid}")
            url = f"https://users.roblox.com/v1/users/{userid}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                username = data.get("name")
                if username:
                    c.set("useridFromUsername:"+username, userid)
                    c.set("usernameFromUserid:"+userid, username)
                    return username
                else:
                    logger.warning(f"Response without name for userid {userid}: {data}")
            else:
                logger.warning(f"Failed to find username of userid {userid}: {response.status_code}")
        except Exception as e:
            logger.error(f"Error trying to search username of userid {userid}: {e}")

        return None

