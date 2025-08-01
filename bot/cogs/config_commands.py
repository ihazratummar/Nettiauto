import discord
from discord.ext import commands
from discord import app_commands

from bot.config import load_config, save_config

class ConfigCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def get_guild_config(self, guild_id: str):
        config = load_config()
        return config.get(guild_id, {})

    async def save_guild_config(self, guild_id: str, guild_config: dict):
        config = load_config()
        config[guild_id] = guild_config
        save_config(config)

    @app_commands.command(name="show_config", description="Shows the current configuration for this server.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def show_config(self, interaction: discord.Interaction):
        await interaction.response.defer()
        guild_id = str(interaction.guild_id)
        guild_config = await self.get_guild_config(guild_id)

        if not guild_config:
            await interaction.followup.send("No configuration found for this server.")
            return

        embed = discord.Embed(title=f"Configuration for {interaction.guild.name}", color=discord.Color.blue())

        # Channel ID
        channel_id = guild_config.get("channel_id")
        if channel_id:
            channel = self.bot.get_channel(channel_id)
            embed.add_field(name="Notification Channel", value=channel.mention if channel else f"ID: {channel_id}", inline=False)

        # URLs
        urls = guild_config.get("urls", [])
        embed.add_field(name="URLs", value="\n".join(urls) if urls else "None", inline=False)

        # Filters
        filters = guild_config.get("filters", {})
        filter_str = []
        for key, value in filters.items():
            if isinstance(value, list):
                filter_str.append(f"{key.replace("_", " ").title()}: {", ".join(value)}")
            else:
                filter_str.append(f"{key.replace("_", " ").title()}: {value}")
        embed.add_field(name="Filters", value="\n".join(filter_str) if filter_str else "None", inline=False)

        # Check Interval
        check_interval = guild_config.get("check_interval")
        if check_interval:
            embed.add_field(name="Check Interval (seconds)", value=check_interval, inline=False)

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="set_channel", description="Sets the Discord channel for notifications.")
    @app_commands.describe(channel="The channel to send notifications to.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def set_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.defer(ephemeral=True)
        guild_id = str(interaction.guild_id)
        guild_config = await self.get_guild_config(guild_id)
        guild_config["channel_id"] = channel.id
        await self.save_guild_config(guild_id, guild_config)
        await interaction.followup.send(f"Notification channel set to {channel.mention}.")

    @app_commands.command(name="add_url", description="Adds a URL to scrape.")
    @app_commands.describe(url="The URL to add.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def add_url(self, interaction: discord.Interaction, url: str):
        await interaction.response.defer(ephemeral=True)
        guild_id = str(interaction.guild_id)
        guild_config = await self.get_guild_config(guild_id)
        urls = guild_config.get("urls", [])
        if url not in urls:
            urls.append(url)
            guild_config["urls"] = urls
            await self.save_guild_config(guild_id, guild_config)
            await interaction.followup.send(f"URL `{url}` added.")
        else:
            await interaction.followup.send(f"URL `{url}` already exists.")

    @app_commands.command(name="remove_url", description="Removes a URL from scraping.")
    @app_commands.describe(url="The URL to remove.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def remove_url(self, interaction: discord.Interaction, url: str):
        await interaction.response.defer(ephemeral=True)
        guild_id = str(interaction.guild_id)
        guild_config = await self.get_guild_config(guild_id)
        urls = guild_config.get("urls", [])
        if url in urls:
            urls.remove(url)
            guild_config["urls"] = urls
            await self.save_guild_config(guild_id, guild_config)
            await interaction.followup.send(f"URL `{url}` removed.")
        else:
            await interaction.followup.send(f"URL `{url}` not found.")

    @app_commands.command(name="set_filter_range", description="Sets min/max values for a filter (e.g., year, price, km, engine_size).")
    @app_commands.describe(
        filter_name="The name of the filter (e.g., year, price, km, engine_size)",
        min_value="The minimum value",
        max_value="The maximum value"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def set_filter_range(self, interaction: discord.Interaction, filter_name: str, min_value: float, max_value: float):
        await interaction.response.defer(ephemeral=True)
        guild_id = str(interaction.guild_id)
        guild_config = await self.get_guild_config(guild_id)
        filters = guild_config.get("filters", {})

        if filter_name not in ["year", "price", "km", "engine_size"]:
            await interaction.followup.send("Invalid filter name. Choose from: `year`, `price`, `km`, `engine_size`.")
            return

        filters[f"{filter_name}_min"] = min_value
        filters[f"{filter_name}_max"] = max_value
        guild_config["filters"] = filters
        await self.save_guild_config(guild_id, guild_config)
        await interaction.followup.send(f"Filter `{filter_name}` set to min: `{min_value}`, max: `{max_value}`.")

    @app_commands.command(name="add_filter_item", description="Adds an item to a list filter (e.g., engine_type, location).")
    @app_commands.describe(
        filter_name="The name of the filter (e.g., engine_type, location)",
        item="The item to add"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def add_filter_item(self, interaction: discord.Interaction, filter_name: str, item: str):
        await interaction.response.defer(ephemeral=True)
        guild_id = str(interaction.guild_id)
        guild_config = await self.get_guild_config(guild_id)
        filters = guild_config.get("filters", {})

        if filter_name not in ["engine_type", "location"]:
            await interaction.followup.send("Invalid filter name. Choose from: `engine_type`, `location`.")
            return

        if filter_name not in filters:
            filters[filter_name] = []
        
        if item not in filters[filter_name]:
            filters[filter_name].append(item)
            guild_config["filters"] = filters
            await self.save_guild_config(guild_id, guild_config)
            await interaction.followup.send(f"Item `{item}` added to `{filter_name}` filter.")
        else:
            await interaction.followup.send(f"Item `{item}` already exists in `{filter_name}` filter.")

    @app_commands.command(name="remove_filter_item", description="Removes an item from a list filter (e.g., engine_type, location).")
    @app_commands.describe(
        filter_name="The name of the filter (e.g., engine_type, location)",
        item="The item to remove"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def remove_filter_item(self, interaction: discord.Interaction, filter_name: str, item: str):
        await interaction.response.defer(ephemeral=True)
        guild_id = str(interaction.guild_id)
        guild_config = await self.get_guild_config(guild_id)
        filters = guild_config.get("filters", {})

        if filter_name not in ["engine_type", "location"]:
            await interaction.followup.send("Invalid filter name. Choose from: `engine_type`, `location`.")
            return

        if filter_name in filters and item in filters[filter_name]:
            filters[filter_name].remove(item)
            guild_config["filters"] = filters
            await self.save_guild_config(guild_id, guild_config)
            await interaction.followup.send(f"Item `{item}` removed from `{filter_name}` filter.")
        else:
            await interaction.followup.send(f"Item `{item}` not found in `{filter_name}` filter.")

    @app_commands.command(name="set_interval", description="Sets the scraping check interval in seconds.")
    @app_commands.describe(interval="The interval in seconds (e.g., 3600 for 1 hour).")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def set_interval(self, interaction: discord.Interaction, interval: int):
        await interaction.response.defer(ephemeral=True)
        guild_id = str(interaction.guild_id)
        guild_config = await self.get_guild_config(guild_id)
        guild_config["check_interval"] = interval
        await self.save_guild_config(guild_id, guild_config)
        await interaction.followup.send(f"Check interval set to `{interval}` seconds.")

    @show_config.error
    @set_channel.error
    @add_url.error
    @remove_url.error
    @set_filter_range.error
    @add_filter_item.error
    @remove_filter_item.error
    @set_interval.error
    async def on_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("You don't have the necessary permissions to use this command. You need `Manage Guild` permission.", ephemeral=True)
        else:
            await interaction.response.send_message(f"An error occurred: {error}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(ConfigCommands(bot=bot))