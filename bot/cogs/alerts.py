import discord
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from bot.config import load_config
from bot.utils import scrape_listings


def scrap_website(url: str, filters: dict):
    print("Start Scrapping")
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    with webdriver.Chrome(options=options) as driver:
        driver.get(url)
        print("Waiting for Cloudflare challenge...")
        
        try:
            # Wait for the iframe to be available and switch to it
            WebDriverWait(driver, 20).until(
                EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[starts-with(@src, 'https://challenges.cloudflare.com')]"))
            )
            
            # Wait for the checkbox to be clickable and click it
            checkbox = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "label.ctp-checkbox-label > input[type='checkbox']"))
            )
            checkbox.click()
            
            print("Clicked the Cloudflare checkbox.")
            
            # Switch back to the main content
            driver.switch_to.default_content()
            
            # Wait for the redirect to complete
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "body:not(.no-js)"))
            )

        except Exception as e:
            print(f"Could not find or click the Cloudflare checkbox: {e}")

        html = driver.page_source
        with open("listing_data.html", "w", encoding="utf-8") as f:
            f.write(html)

    print("Start Scrapping HTML")
    list_car = scrape_listings(html)
    # for listing in list_car:
    #     print(f"- Title: {listing['title']}, Price: {listing['price']}, Link: {listing['link']}")
    return list_car


class Alerts(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config = load_config()

    @commands.hybrid_command(name="scrap")
    async def scrap(self, ctx: commands.Context):
        await ctx.defer()
        guild_id = str(ctx.guild.id)
        if guild_id in self.config:
            config = self.config[guild_id]
            urls = config.get("urls", [])
            filters = config.get("filters", {})

            for url in urls:
                result = scrap_website(url, filters)

                if isinstance(result, str):  # This means it’s an error message
                    print(result)
                    await ctx.send(result)
                else:
                    for car in result:
                        embed = discord.Embed(title=car['title'], url=car['link'], color=discord.Color.blue())
                        embed.set_image(url=car['image'])
                        embed.add_field(name="Price", value=car['price'], inline=True)
                        embed.add_field(name="Location", value=car['location'], inline=True)
                        embed.add_field(name="Year", value=car['year'], inline=True)
                        embed.add_field(name="Mileage", value=car['km'], inline=True)
                        embed.add_field(name="Engine Size", value=car['engine_size'], inline=True)
                        embed.add_field(name="Fuel Type", value=car['engine_type'], inline=True)
                        await ctx.send(embed=embed)
                    await ctx.send(f"Scraped {len(result)} matching cars from {url}")
        else:
            await ctx.send("No configuration found for this server.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Alerts(bot=bot))