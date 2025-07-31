import discord
from discord.ext import commands
import json


extensions = [
    "bot.cogs.alerts"
]

class Bot(commands.Bot):
    def __init__(self, command_prefix: str, intents : discord.Intents, **kwargs):
        super().__init__(command_prefix= command_prefix, intents= intents, **kwargs)


    async def on_ready(self):
        for extension in extensions:
            await self.load_extension(extension)
            print(f"{extension} Loaded Successfully")

        tree = await self.tree.sync()
        print(f"Synced {len(tree)} commands")


def load_config():
    with open("config.json", "r") as f:
        return  json.load(f)

CONFIG = load_config()
    