import os
import json
import time
import psutil
import asyncio
import logging
from urllib.parse import urlparse, parse_qs # for private server links
from datetime import datetime
from pathlib import Path
from .system import System
from .discord import Discord

class RobloxApplication:
    def __init__(self):
        self.processes = []
        self.log_name = "mspr.Roblox."
        self.LOGFILE_DETECTION_METHOD = 'accesstime' # accesstime | filename
        
    def __getLogger(self, name):
        return logging.getLogger(f"{self.log_name}{name}")
    
    def find_active_processes(self):
        result = {"active": [], "lazy": []}

        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if "RobloxPlayerBeta" in proc.info['name'] or "RobloxGameClient" in proc.info['name']:
                    children = proc.children()

                    if children:
                        result["active"].append({"pid": proc.pid, "name": proc.info['name']})
                    else:
                        result["lazy"].append({"pid": proc.pid, "name": proc.info['name']})

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return result
    
    
    async def _kill_lazy_processes(self, delay=0):
        '''
        Assume the game has PID 10000 "master". 
        Whenever we do a forced join, it will create a new PID 10001 "lazy", but the game will still be running at PID 10000 "master". 
        I am calling that "useless" process "lazy". # Those "Lazy" processes doesn't consume much resource, but overtime it builds up
        and leads to memory clogging up.
        
        This function will find every Roblox named process, and kill everything except the "master" process.
        '''
        l = self.__getLogger('kill_lazy_processes')
        
        if delay > 0:
            l.trace(f'Waiting for {delay} seconds before killing lazy processes...')
            await asyncio.sleep(delay)
            l.trace("Done waiting.")
        
        l.trace("Killing lazy processes...")
        processes = self.find_active_processes()
        for proc in processes["lazy"]:
            try:
                await System._taskkill(proc["pid"])
                l.debug(f"Killed lazy process {proc['pid']} ({proc['name']})")
            except Exception as e:
                l.error(f"Failed to kill process {proc['pid']} ({proc['name']}): {e}")
        l.debug(f"Killed {len(processes['lazy'])} lazy processes.")
                
    def is_running(self):
        l = self.__getLogger('is_running')
        procs = self.find_active_processes()
        return bool(procs.get("active"))
    
    async def join(self, url, forced=False):
        l = self.__getLogger('join')
        
        if not url: 
            #TODO: Stop application if this happens: throw error?
            l.error("No URL provided.")
            return
        
        if not forced and self.is_running():
            l.warning("Roblox is already running.")
            return
        
        #TODO: Make compatibility with privateServerLinkCode AND share links. Make an option to decide if we decode share links or not
        LINK_CODE = parse_qs(urlparse(url).query).get("privateServerLinkCode", [None])[0]
        FINAL_URL = f"roblox://placeID=15532962292&linkCode={LINK_CODE}"
        
        l.info("Joining game")
        await System._start(url=FINAL_URL)
        
        if forced:
            l.trace('Cleaning up...')
            asyncio.create_task(self._kill_lazy_processes(delay=5))
        
    
RobloxApplication = RobloxApplication()