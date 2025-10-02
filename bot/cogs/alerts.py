import json
import time

import discord
from discord.ext import commands
from selenium import webdriver

# from selenium.webdriver.chrome.service import Service
from bot.config import load_config
from bot.utils import scrape_listings, match_filters


def scrap_website(url: str):
    print("Start Scrapping")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")

    # service = Service('/usr/bin/chromedriver')

    try:
        # with webdriver.Chrome(service=service, options=options) as driver:
        with webdriver.Chrome(options=options) as driver:
            driver.implicitly_wait(10)
            driver.get(url)
            print("Waiting for page to load and Cloudflare to resolve...")
            time.sleep(15)

            html = driver.page_source

        # ⚠️ Check for Cloudflare block or error page
        if "cf-browser-verification" in html or "Attention Required!" in html or "Access denied" in html:
            return "Blocked by Cloudflare or site returned error page."

        print("Start Scrapping HTML")
        return scrape_listings(html)

    except Exception as e:
        print(f"Error during scraping: {e}")
        return f"Scraping error: {e}"


from apscheduler.schedulers.asyncio import AsyncIOScheduler


class Alerts(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config = load_config()
        self.seen_listings_file = "seen_listings.json"
        self.scheduler = AsyncIOScheduler()

    async def cog_load(self):
        self.scheduler.add_job(self.scheduled_scraping, 'interval', seconds=10, max_instances=10)
        self.scheduler.start()
        print("Scheduler started in Alerts cog.")

    def cog_unload(self):
        self.scheduler.shutdown()

    def reload_config(self):
        self.config = load_config()
        print("Alerts cog reloaded its configuration.")



    async def scheduled_scraping(self):
        print("Running scheduled scraping...")
        for guild_id, guild_config in self.config.items():
            await self.scheduled_scrap(guild_id, guild_config)

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
                await self.send_log(guild_config, f"Error scraping {url}: {result}")
                continue
            else:
                new_listings = []
                for car in result:
                    print(f"Scraped car: {car}")
                    if car['link'] not in seen_listings and match_filters(car, filters):
                        new_listings.append(car)
                        seen_listings.append(car['link'])

                if not new_listings:
                    await self.send_log(guild_config, f"ℹ️ No new listings matched filters for `{url}`.")
                    continue

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
                            time.sleep(5)  # Add a 2-second delay to avoid rate limiting
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
            await ctx.send(
                f"Manual scrap initiated for this server. Check {self.bot.get_channel(self.config[guild_id]["channel_id"]).mention} for updates.")
        else:
            await ctx.send("No configuration found for this server.")

    async def send_log(self, guild_config: dict, message: str):
        log_channel_id = guild_config.get("log_channel_id")
        if not log_channel_id:
            print("No log channel configured.")
            return

        log_channel = self.bot.get_channel(log_channel_id)
        if log_channel:
            try:
                await log_channel.send(f"📛 **Alert:** {message}")
            except Exception as e:
                print(f"Failed to send log message: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Alerts(bot=bot))