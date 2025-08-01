import discord
from discord.ext import commands
import json
from apscheduler.schedulers.asyncio import AsyncIOScheduler

extensions = [
    "bot.cogs.alerts",
    "bot.cogs.config_commands"  # New cog for config management
]


class Bot(commands.Bot):
    def __init__(self, command_prefix: str, intents: discord.Intents, **kwargs):
        super().__init__(command_prefix=command_prefix, intents=intents, **kwargs)
        self.scheduler = AsyncIOScheduler()

    async def on_ready(self):
        for extension in extensions:
            await self.load_extension(extension)
            print(f"{extension} Loaded Successfully")

        tree = await self.tree.sync()
        print(f"Synced {len(tree)} commands")

        # Schedule the scraping task
        self.scheduler.add_job(
            self.scheduled_scraping,
            'interval',
            seconds=10,
            max_instances=10  # or higher if safe
        )
        self.scheduler.start()
        print("Scheduler started.")

    async def scheduled_scraping(self):
        config = load_config()
        for guild_id, guild_config in config.items():
            alerts_cog = self.get_cog("Alerts")
            if alerts_cog:
                await alerts_cog.scheduled_scrap(guild_id, guild_config)


def load_config():
    with open("config.json", "r") as f:
        return json.load(f)


def save_config(config_data):
    with open("config.json", "w") as f:
        json.dump(config_data, f, indent=2)


CONFIG = load_config()
