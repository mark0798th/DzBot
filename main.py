import os
import discord
from discord import app_commands
from flask import Flask
from threading import Thread

# ========================================================
# Web Server for Render Keep-Alive
# ========================================================
app = Flask("")

@app.route("/")
def home():
    return "DeadZone Showcase Bot is running."

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# ========================================================
# Discord Client Setup
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

        print("========================================")
        print("DeadZone Showcase System initialized")
        print("Global slash commands synchronized")
        print("Bot status: ONLINE")
        print("========================================")

bot = MyBot()

# ========================================================
# Bot Ready Event
# ========================================================
@bot.event
async def on_ready():
    print("========================================")
    print(f"Authenticated as: {bot.user}")
    print("Connected to Discord successfully")
    print("Development services are active")
    print("========================================")

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="DeadZone Development"
        )
    )

# ========================================================
# UPDATE COMMAND
# ========================================================
@bot.tree.command(
    name="update",
    description="Post a game update or patch notes"
)
@app_commands.describe(
    version="Update version",
    title="Update headline",
    details="Patch notes or update details",
    image_url="Optional image URL",
    role_1="First role to ping",
    role_2="Second role to ping",
    role_3="Third role to ping"
)
@app_commands.checks.has_permissions(manage_messages=True)
async def update(
    interaction: discord.Interaction,
    version: str,
    title: str,
    details: str,
    image_url: str = None,
    role_1: discord.Role = None,
    role_2: discord.Role = None,
    role_3: discord.Role = None
):

    formatted_details = details.replace("\\n", "\n")

    embed = discord.Embed(
        title=f"DeadZone Update {version}",
        description=formatted_details,
        color=discord.Color.gold()
    )

    embed.add_field(
        name="Update Title",
        value=title,
        inline=False
    )

    embed.set_author(
        name="DeadZone Development Team",
        icon_url=interaction.user.display_avatar.url
    )

    embed.set_footer(
        text=f"Published by {interaction.user.name}"
    )

    if image_url and image_url.startswith("http"):
        embed.set_image(url=image_url)

    roles_to_ping = []

    for role in [role_1, role_2, role_3]:
        if role and role not in roles_to_ping:
            roles_to_ping.append(role)

    ping_message = " ".join(role.mention for role in roles_to_ping)

    await interaction.response.send_message(
        "Update announcement published successfully.",
        ephemeral=True
    )

    if ping_message:
        await interaction.channel.send(
            content=ping_message,
            embed=embed
        )
    else:
        await interaction.channel.send(embed=embed)

# ========================================================
# SHOWCASE COMMAND
# ========================================================
@bot.tree.command(
    name="showcase",
    description="Showcase a new weapon, system, map, or feature"
)
@app_commands.describe(
    asset_name="Name of the showcased content",
    description="Details about the showcase",
    media_url="Image or media URL"
)
@app_commands.checks.has_permissions(manage_messages=True)
async def showcase(
    interaction: discord.Interaction,
    asset_name: str,
    description: str,
    media_url: str = None
):

    formatted_description = description.replace("\\n", "\n")

    embed = discord.Embed(
        title=asset_name,
        description=formatted_description,
        color=discord.Color.purple()
    )

    embed.set_author(
        name="DeadZone Showcase",
        icon_url=bot.user.display_avatar.url
    )

    embed.set_footer(
        text=f"Showcased by {interaction.user.name}"
    )

    if media_url and media_url.startswith("http"):
        if any(ext in media_url.lower() for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp"]):
            embed.set_image(url=media_url)
        else:
            embed.add_field(
                name="Media",
                value=media_url,
                inline=False
            )

    await interaction.response.send_message(
        "Showcase published successfully.",
        ephemeral=True
    )

    await interaction.channel.send(embed=embed)

# ========================================================
# DEVELOPMENT STATUS COMMAND
# ========================================================
@bot.tree.command(
    name="status",
    description="Update current development status"
)
@app_commands.describe(
    state="Current development state",
    message="Developer notes"
)
@app_commands.choices(state=[
    app_commands.Choice(name="Active Development", value="active"),
    app_commands.Choice(name="Working on Systems", value="working"),
    app_commands.Choice(name="Reworking Features", value="rework"),
    app_commands.Choice(name="Taking a Break", value="break"),
    app_commands.Choice(name="Developer Burnout", value="burnout"),
    app_commands.Choice(name="Preparing Next Update", value="preparing"),
    app_commands.Choice(name="Experimental Features", value="experimental"),
    app_commands.Choice(name="Development Paused", value="paused")
])
@app_commands.checks.has_permissions(manage_messages=True)
async def status(
    interaction: discord.Interaction,
    state: app_commands.Choice[str],
    message: str = "No additional details."
):

    color_map = {
        "active": discord.Color.green(),
        "working": discord.Color.gold(),
        "rework": discord.Color.orange(),
        "break": discord.Color.blue(),
        "burnout": discord.Color.dark_grey(),
        "preparing": discord.Color.purple(),
        "experimental": discord.Color.teal(),
        "paused": discord.Color.red()
    }

    embed = discord.Embed(
        title="DeadZone Development Status",
        description=(
            f"Current State\n"
            f"{state.name}\n\n"
            f"Developer Notes\n"
            f"{message}"
        ),
        color=color_map.get(state.value, discord.Color.light_grey())
    )

    embed.set_author(
        name="DeadZone Studio",
        icon_url=bot.user.display_avatar.url
    )

    embed.set_footer(
        text=f"Updated by {interaction.user.name}"
    )

    await interaction.response.send_message(
        "Development status updated successfully.",
        ephemeral=True
    )

    await interaction.channel.send(embed=embed)

# ========================================================
# Permission Error Handler
# ========================================================
@update.error
@showcase.error
@status.error
async def permission_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError
):

    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "You do not have permission to use this command.",
            ephemeral=True
        )

# ========================================================
# Start Services
# ========================================================
keep_alive()

TOKEN = os.environ.get("DISCORD_TOKEN")

if TOKEN:
    bot.run(TOKEN)
else:
    print("DISCORD_TOKEN was not found in environment variables.")