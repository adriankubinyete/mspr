from collections import defaultdict
from lib.RoLogReader import RoLogReader
from lib.cache import Cache
import json

c = Cache()
rl = RoLogReader()

class SolsBiomeNotifier:
    def __init__(self, autostart=True):
        self.RUNNING = False
        self._biome_callbacks = defaultdict(list)
        
        self.start() if autostart else None

    # public

    def start(self):
        if self.RUNNING:
            return
        self.RUNNING = True
        rl.start()

    def stop(self):
        if not self.RUNNING:
            return
        self.RUNNING = False
        rl.stop()

    def on_biome_change(self, username, callback):
        """
        Callback a function when a biome change happens for a given username

        :param username: str, username to monitor (whose we will search in logs)
        :param callback: function, callback to call when biome changes. needs to accept 2 args:
            current_biome: str, previous_biome: str or None (if it's the first time/log)
        :return: None
        """
        username = username.lower()
        self._biome_callbacks[username].append(callback)
        rl.set_callback(username, self._handle_log_line(username))

    def unmonitor(self, username):
        """
        Stop monitoring a username
        :param username: str, username to stop monitoring
        :return: None
        """
        username = username.lower()
        if username in self._biome_callbacks:
            del self._biome_callbacks[username]
        rl.del_callback(username)

    # private methods 

    def _handle_log_line(self, username):
        def inner(line):
            if "[BloxstrapRPC]" in line:
                content = line.split("[BloxstrapRPC] ")[1].strip()
                command = json.loads(content)
                data = command.get("data", {})
                large_image = data.get("largeImage", {})
                biome = large_image.get("hoverText", None)
                
                previous_biome = c.get(f"biome:{username}", fallback=None)
                
                if biome != previous_biome:
                    # print(f"[TEST] [{username}] Biome changed from {previous_biome} to {biome}")
                    c.set(f"biome:{username}", biome)
                    for cb in self._biome_callbacks.get(username, []):
                        cb(current_biome=biome, previous_biome=previous_biome)
                
        return inner
    
SolsBiomeNotifier = SolsBiomeNotifier(autostart=True)
