import os
import discord
from discord import app_commands
from flask import Flask
from threading import Thread

# =========================================================
# Render Keep Alive
# =========================================================
app = Flask("")

@app.route("/")
def home():
    return "DeadZone Development Bot is running."

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    Thread(target=run_web).start()

# =========================================================
# Discord Bot Setup
# =========================================================
class DeadZoneBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

        print("================================================")
        print(" DeadZone Development System")
        print(" Slash commands synchronized globally")
        print(" System status: ONLINE")
        print("================================================")

bot = DeadZoneBot()

# =========================================================
# Ready Event
# =========================================================
@bot.event
async def on_ready():
    print("================================================")
    print(f" Logged in as: {bot.user}")
    print(" Connected to Discord API")
    print(" Development services initialized")
    print("================================================")

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="DeadZone Development"
        )
    )

# =========================================================
# Colors
# =========================================================
COLORS = {
    "update": discord.Color.from_rgb(255, 170, 0),
    "showcase": discord.Color.from_rgb(180, 120, 255),
    "active": discord.Color.from_rgb(67, 181, 129),
    "working": discord.Color.from_rgb(255, 201, 107),
    "rework": discord.Color.from_rgb(255, 140, 70),
    "break": discord.Color.from_rgb(114, 137, 218),
    "burnout": discord.Color.from_rgb(90, 90, 90),
    "preparing": discord.Color.from_rgb(200, 130, 255),
    "experimental": discord.Color.from_rgb(88, 210, 200),
    "paused": discord.Color.from_rgb(240, 71, 71)
}

# =========================================================
# UPDATE COMMAND
# =========================================================
@bot.tree.command(
    name="update",
    description="Publish a development update or patch notes"
)
@app_commands.describe(
    version="Update version",
    title="Headline for this update",
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
        description=(
            f"## {title}\n\n"
            f"{formatted_details}"
        ),
        color=COLORS["update"]
    )

    embed.add_field(
        name="Build Version",
        value=version,
        inline=True
    )

    embed.add_field(
        name="Category",
        value="Patch Notes",
        inline=True
    )

    embed.add_field(
        name="Status",
        value="Released",
        inline=True
    )

    embed.set_thumbnail(
        url=bot.user.display_avatar.url
    )

    if image_url and image_url.startswith("http"):
        embed.set_image(url=image_url)

    embed.set_footer(
        text=f"Published by {interaction.user.name}"
    )

    embed.timestamp = discord.utils.utcnow()

    # Role Pings
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

# =========================================================
# SHOWCASE COMMAND
# =========================================================
@bot.tree.command(
    name="showcase",
    description="Showcase a new weapon, map, feature, or system"
)
@app_commands.describe(
    asset_name="Name of the showcased content",
    description="Showcase details",
    media_url="Optional image or media URL"
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
        color=COLORS["showcase"]
    )

    embed.add_field(
        name="Content Type",
        value="Development Showcase",
        inline=True
    )

    embed.add_field(
        name="Project",
        value="DeadZone",
        inline=True
    )

    embed.add_field(
        name="Visibility",
        value="Public Preview",
        inline=True
    )

    embed.set_thumbnail(
        url=bot.user.display_avatar.url
    )

    if media_url and media_url.startswith("http"):
        if any(ext in media_url.lower() for ext in [
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".webp"
        ]):
            embed.set_image(url=media_url)
        else:
            embed.add_field(
                name="Media Link",
                value=media_url,
                inline=False
            )

    embed.set_footer(
        text=f"Showcased by {interaction.user.name}"
    )

    embed.timestamp = discord.utils.utcnow()

    await interaction.response.send_message(
        "Showcase published successfully.",
        ephemeral=True
    )

    await interaction.channel.send(embed=embed)

# =========================================================
# DEVELOPMENT STATUS COMMAND
# =========================================================
@bot.tree.command(
    name="status",
    description="Update the current development status"
)
@app_commands.describe(
    state="Current development state",
    message="Additional developer notes"
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

    embed = discord.Embed(
        title="DeadZone Development Status",
        description=(
            f"## {state.name}\n\n"
            f"{message}"
        ),
        color=COLORS.get(state.value)
    )

    embed.add_field(
        name="Project",
        value="DeadZone",
        inline=True
    )

    embed.add_field(
        name="Current Activity",
        value=state.name,
        inline=True
    )

    embed.add_field(
        name="Team Status",
        value="Monitoring",
        inline=True
    )

    embed.set_thumbnail(
        url=bot.user.display_avatar.url
    )

    embed.set_footer(
        text=f"Updated by {interaction.user.name}"
    )

    embed.timestamp = discord.utils.utcnow()

    await interaction.response.send_message(
        "Development status updated successfully.",
        ephemeral=True
    )

    await interaction.channel.send(embed=embed)

# =========================================================
# SERVER RULES COMMAND
# =========================================================
@bot.tree.command(
    name="rules",
    description="Publish or update the server rules"
)
@app_commands.describe(
    title="Rules headline",
    rules="Server rules (Use \\n for new lines)",
    role_1="First role to ping",
    role_2="Second role to ping",
    role_3="Third role to ping"
)
@app_commands.checks.has_permissions(manage_guild=True)
async def rules(
    interaction: discord.Interaction,
    title: str,
    rules: str,
    role_1: discord.Role = None,
    role_2: discord.Role = None,
    role_3: discord.Role = None
):

    formatted_rules = rules.replace("\\n", "\n")

    embed = discord.Embed(
        title=f"{title}",
        description=formatted_rules,
        color=discord.Color.from_rgb(88, 101, 242)
    )

    embed.add_field(
        name="Server",
        value=interaction.guild.name,
        inline=True
    )

    embed.add_field(
        name="Category",
        value="Community Rules",
        inline=True
    )

    embed.add_field(
        name="Status",
        value="Active",
        inline=True
    )

    if interaction.guild.icon:
        embed.set_thumbnail(url=interaction.guild.icon.url)

    embed.set_footer(
        text=f"Published by {interaction.user.name}"
    )

    embed.timestamp = discord.utils.utcnow()

    # Role Pings
    roles_to_ping = []

    for role in [role_1, role_2, role_3]:
        if role and role not in roles_to_ping:
            roles_to_ping.append(role)

    ping_message = " ".join(role.mention for role in roles_to_ping)

    await interaction.response.send_message(
        "Server rules published successfully.",
        ephemeral=True
    )

    if ping_message:
        await interaction.channel.send(
            content=ping_message,
            embed=embed
        )
    else:
        await interaction.channel.send(embed=embed)

# =========================================================
# Add To Error Handler
# =========================================================
@rules.error
async def rules_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError
):

    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "You do not have permission to use this command.",
            ephemeral=True
        )

# =========================================================
# Permission Error Handler
# =========================================================
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

# =========================================================
# Start Services
# =========================================================
keep_alive()

TOKEN = os.environ.get("DISCORD_TOKEN")

if TOKEN:
    bot.run(TOKEN)
else:
    print("DISCORD_TOKEN was not found in environment variables.")