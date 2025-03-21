import time
import asyncio
import logging
from discord_webhook import DiscordWebhook, DiscordEmbed

class Discord:
    def __init__(self):
        self.webhook_url = None
        pass

    def __getLogger(self, name):
        return logging.getLogger(f'mspr.Discord.{name}')

    def setWebhook(self, url):
        """Separa a string de URLs por vírgulas e armazena como lista."""
        self.webhook_url = [u.strip() for u in url.split(",") if u.strip()]


    def create_embed(self, description=None, title=None, color="3498db", footer=None, timestamp=None):
        l = self.__getLogger('create_embed')
        embed = DiscordEmbed(description=description, color=color)
        if title:
            embed.set_title(title)
        if footer:
            embed.set_footer(text=footer)
        if timestamp:
            embed.set_timestamp()
        return embed

    def send(self, content=None, embed=None):
        l = self.__getLogger('send')
        
        if not self.webhook_url: l.trace("No webhook URL to send message to."); return
         
        responses = []
        for url in self.webhook_url:
            try:
                webhook = DiscordWebhook(url=url, content=content)
                if embed:
                    webhook.add_embed(embed)
                responses.append(webhook.execute())
            except Exception as e:
                l.error(f"Error sending message to Discord: {e}")
        return responses

Discord = Discord()