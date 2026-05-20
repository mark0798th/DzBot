import os
import discord
from discord import app_commands
from flask import Flask
from threading import Thread

# ========================================================
# Web Server for Render Keep-Alive (24/7)
# ========================================================
app = Flask('')

@app.route('/')
def home():
    return "Game Showcase Bot is running 24/7 online!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# ========================================================
# Discord Slash Bot Setup
# ========================================================
class MyBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print("Game Showcase slash commands synced globally!")

bot = MyBot()

@bot.event
async def on_ready():
    print(f'=================================')
    print(f'Logged in as {bot.user}')
    print(f'Game Showcase Bot is ready on Render!')
    print(f'=================================')
    # Set Bot status to "Watching Game Updates"
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Game Updates & Showcases"))

# ========================================================
# Game Update & Showcase Slash Commands
# ========================================================

# 1. /update - Post a game update/patch notes announcement
@bot.tree.command(name="update", description="Post a beautiful game update / patch notes announcement")
@app_commands.describe(
    version="The version number (e.g., v1.5.0)",
    title="Headline of the update",
    details="What is new in this update? (Use \\n for new lines)",
    image_url="Optional: URL of the update poster or screenshot"
)
@app_commands.checks.has_permissions(manage_messages=True)
async def update(interaction: discord.Interaction, version: str, title: str, details: str, image_url: str = None):
    # Format details to support actual line breaks
    formatted_details = details.replace("\\n", "\n")
    
    embed = discord.Embed(
        title=f"DeadZone : {version} - {title}",
        description=formatted_details,
        color=discord.Color.gold()
    )
    embed.set_author(name="Development Team", icon_url=interaction.user.display_avatar.url)
    embed.set_footer(text=f"Posted by {interaction.user.name} • Today")
    
    if image_url and image_url.startswith("http"):
        embed.set_image(url=image_url)
        
    await interaction.response.send_message("Announcement posted!", ephemeral=True)
    await interaction.channel.send(embed=embed)


# 2. /showcase - Showcase a specific item, skin, map, or feature
@bot.tree.command(name="showcase", description="Showcase a new game asset, weapon, skin, or system")
@app_commands.describe(
    asset_name="Name of the item/feature being showcased",
    description="Describe the statistics, rarity, or details of this asset",
    media_url="URL of the showcase image, GIF, or YouTube link"
)
@app_commands.checks.has_permissions(manage_messages=True)
async def showcase(interaction: discord.Interaction, asset_name: str, description: str, media_url: str):
    formatted_desc = description.replace("\\n", "\n")
    
    embed = discord.Embed(
        title=f"{asset_name}",
        description=formatted_desc,
        color=discord.Color.purple()
    )
    embed.set_author(name="Sneak Peek & Showcase", icon_url=bot.user.display_avatar.url)
    
    # If it's a standard link, attach it cleanly
    if media_url.startswith("http"):
        if any(ext in media_url.lower() for ext in [".png", ".jpg", ".jpeg", ".gif"]):
            embed.set_image(url=media_url)
        else:
            embed.add_field(name="Image", value=media_url, inline=False)
            
    await interaction.response.send_message("Showcase posted!", ephemeral=True)
    await interaction.channel.send(embed=embed)


# 3. /status - Post current game server status
@bot.tree.command(name="status", description="Update the current community or game server status")
@app_commands.describe(
    state="Select server status",
    message="Additional notes about the current server status"
)
@app_commands.choices(state=[
    app_commands.Choice(name="🟢 Online / Stable", value="online"),
    app_commands.Choice(name="🟡 Maintenance / Updating", value="maintenance"),
    app_commands.Choice(name="🔴 Offline / Issues", value="offline")
])
@app_commands.checks.has_permissions(manage_messages=True)
async def status(interaction: discord.Interaction, state: app_commands.Choice[str], message: str = "No additional details."):
    color_map = {
        "online": discord.Color.green(),
        "maintenance": discord.Color.orange(),
        "offline": discord.Color.red()
    }
    
    embed = discord.Embed(
        title="🎮 Game Server Status Report",
        description=f"Current State: **{state.name}**\n\n**Details:**\n{message}",
        color=color_map.get(state.value, discord.Color.light_grey())
    )
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.set_footer(text="Live Server Status Dashboard")
    
    await interaction.response.send_message("Status report updated!", ephemeral=True)
    await interaction.channel.send(embed=embed)


# Error handler for regular members trying to post announcements
@update.error
@showcase.error
@status.error
async def permission_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ Error: Only game developers/moderators can use this command!", ephemeral=True)

# Run Web Server first
keep_alive()

# Run the bot using the Token from Render Environment
TOKEN = os.environ.get('DISCORD_TOKEN')
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ DISCORD_TOKEN not found in Render Environment variables!")
