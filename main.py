import discord

from bot.config import Bot
from dotenv import load_dotenv
import os

load_dotenv()

token = os.getenv("DISCORD_BOT_TOKEN")

if not token:
    raise ValueError("DISCORD_BOT_TOKEN is not set in the environment variables.")

if __name__ == "__main__":
    bot = Bot(command_prefix="n!", intents=discord.Intents.all(), help_command=None)
    bot.run(token=token)

