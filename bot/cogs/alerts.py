import json
import time

import discord
from discord.ext import commands
from selenium import webdriver

from bot.config import load_config
from bot.utils import scrape_listings, match_filters


def scrap_website(url: str):
    print("Start Scrapping")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new") # Use new headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled") # Disable automation detection
    options.add_experimental_option("excludeSwitches", ["enable-automation"]) # Disable automation info bar
    options.add_experimental_option("useAutomationExtension", False) # Disable automation extension
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36") # Set a common user-agent

    with webdriver.Chrome(options=options) as driver:
        driver.implicitly_wait(10) # Implicitly wait for elements to appear
        driver.get(url)
        print("Waiting for page to load and Cloudflare to resolve...")
        time.sleep(15) # Give extra time for JavaScript to execute

        html = driver.page_source

    print("Start Scrapping HTML")
    list_car = scrape_listings(html)
    return list_car


class Alerts(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config = load_config()
        self.seen_listings_file = "seen_listings.json"
        self.bot

    def load_seen_listings(self):
        try:
            with open(self.seen_listings_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_seen_listings(self, listings):
        with open(self.seen_listings_file, 'w') as f:
            json.dump(listings, f, indent=2)

    async def scheduled_scrap(self, guild_id: str, guild_config: dict):
        urls = guild_config.get("urls", [])
        filters = guild_config.get("filters", {})
        seen_listings = self.load_seen_listings()

        for url in urls:
            result = await self.bot.loop.run_in_executor(None, scrap_website, url)

            if isinstance(result, str):  # This means it’s an error message
                print(result)
            else:
                new_listings = []
                for car in result:
                    print(f"Scraped car: {car}")
                    if car['link'] not in seen_listings and match_filters(car, filters):
                        new_listings.append(car)
                        seen_listings.append(car['link'])

                channel_id = guild_config["channel_id"]
                channel = self.bot.get_channel(channel_id)
                if channel:
                    for car in new_listings:
                        embed = discord.Embed(title=car['title'], url=car['link'], color=discord.Color.blue())
                        embed.set_image(url=car['image'])
                        embed.add_field(name="Price", value=car['price'], inline=True)
                        embed.add_field(name="Location", value=car['location'], inline=True)
                        embed.add_field(name="Year", value=car['year'], inline=True)
                        embed.add_field(name="Mileage", value=car['km'], inline=True)
                        embed.add_field(name="Engine Size", value=car['engine_size'], inline=True)
                        embed.add_field(name="Fuel Type", value=car['engine_type'], inline=True)

                        try:
                            await channel.send(embed=embed)
                        except discord.RateLimited:
                            print("Discord Rate Limit")
                            time.sleep(300)

                    self.save_seen_listings(seen_listings)
                    print(f"Scraped {len(new_listings)} new matching cars from {url}")
                    print(f"data posted in {channel.mention}")

    @commands.hybrid_command(name="scrap")
    async def scrap(self, ctx: commands.Context):
        await ctx.defer()
        guild_id = str(ctx.guild.id)
        if guild_id in self.config:
            await self.scheduled_scrap(guild_id, self.config[guild_id])
            await ctx.send(f"Manual scrap initiated for this server. Check {self.bot.get_channel(self.config[guild_id]["channel_id"]).mention} for updates.")
        else:
            await ctx.send("No configuration found for this server.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Alerts(bot=bot))