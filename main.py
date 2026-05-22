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
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

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
# Colors
# =========================================================
COLORS = {
    "update": discord.Color.from_rgb(255, 170, 0),
    "showcase": discord.Color.from_rgb(180, 120, 255),
    "rules": discord.Color.from_rgb(88, 101, 242),
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
# Utility
# =========================================================
def get_ping_message(*roles):
    valid_roles = []

    for role in roles:
        if role and role not in valid_roles:
            valid_roles.append(role)

    return " ".join(role.mention for role in valid_roles)

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
# BAN COMMAND
# =========================================================
ALLOWED_BAN_ROLES = [
    "DeadZone HR",
    "Head Moderator"
]

@bot.tree.command(name="ban", description="Ban a member from the server")
@app_commands.describe(
    member="Member to ban",
    reason="Reason for the ban"
)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    user_roles = [role.name for role in interaction.user.roles]

    if not any(role in ALLOWED_BAN_ROLES for role in user_roles):
        return await interaction.response.send_message(
            "You do not have permission to use this command.",
            ephemeral=True
        )

    if member.top_role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
        return await interaction.response.send_message(
            "You cannot ban this member.",
            ephemeral=True
        )

    embed = discord.Embed(
        title="Member Banned",
        description=f"{member.mention} has been banned from the server.",
        color=discord.Color.red()
    )

    embed.add_field(name="Member", value=f"{member} ({member.id})", inline=False)
    embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
    embed.add_field(name="Reason", value=reason, inline=True)

    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f"Banned by {interaction.user.name}")
    embed.timestamp = discord.utils.utcnow()

    await member.ban(reason=reason)

    await interaction.response.send_message("Member banned successfully.", ephemeral=True)
    await interaction.channel.send(embed=embed)

# =========================================================
# DEVLOG COMMAND
# =========================================================
@bot.tree.command(name="devlog", description="Post development progress or changes")
@app_commands.describe(
    category="Type of development update",
    title="Headline of the update",
    details="What was changed, fixed, or added",
    image_url="Optional image URL"
)
@app_commands.choices(category=[
    app_commands.Choice(name="Bug Fixes", value="fix"),
    app_commands.Choice(name="New Features", value="feature"),
    app_commands.Choice(name="Balancing", value="balance"),
    app_commands.Choice(name="Optimization", value="optimization"),
    app_commands.Choice(name="Rework", value="rework"),
    app_commands.Choice(name="AI Improvements", value="ai"),
    app_commands.Choice(name="Systems Update", value="systems"),
    app_commands.Choice(name="Experimental", value="experimental")
])
@app_commands.checks.has_permissions(manage_messages=True)
async def devlog(
    interaction: discord.Interaction,
    category: app_commands.Choice[str],
    title: str,
    details: str,
    image_url: str = None
):
    color_map = {
        "fix": discord.Color.from_rgb(87, 242, 135),
        "feature": discord.Color.from_rgb(88, 101, 242),
        "balance": discord.Color.from_rgb(255, 201, 107),
        "optimization": discord.Color.from_rgb(67, 181, 129),
        "rework": discord.Color.from_rgb(255, 140, 70),
        "ai": discord.Color.from_rgb(240, 71, 71),
        "systems": discord.Color.from_rgb(180, 120, 255),
        "experimental": discord.Color.from_rgb(88, 210, 200)
    }

    embed = discord.Embed(
        title=title,
        description=details.replace("\\n", "\n"),
        color=color_map[category.value]
    )

    embed.add_field(name="Category", value=category.name, inline=True)
    embed.add_field(name="Project", value="DeadZone", inline=True)
    embed.add_field(name="Status", value="In Development", inline=True)

    embed.set_thumbnail(url=bot.user.display_avatar.url)

    if image_url and image_url.startswith("http"):
        embed.set_image(url=image_url)

    embed.set_footer(text=f"Development log by {interaction.user.name}")
    embed.timestamp = discord.utils.utcnow()

    await interaction.response.send_message("Development log published successfully.", ephemeral=True)
    await interaction.channel.send(embed=embed)

# =========================================================
# UPDATE COMMAND
# =========================================================
@bot.tree.command(name="update", description="Publish development updates")
@app_commands.describe(
    version="Update version",
    title="Update title",
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
    embed = discord.Embed(
        title=f"DeadZone Update {version}",
        description=f"## {title}\n\n{details.replace('\\n', '\n')}",
        color=COLORS["update"]
    )

    embed.add_field(name="Version", value=version, inline=True)
    embed.add_field(name="Category", value="Patch Notes", inline=True)
    embed.add_field(name="Status", value="Released", inline=True)

    embed.set_thumbnail(url=bot.user.display_avatar.url)

    if image_url and image_url.startswith("http"):
        embed.set_image(url=image_url)

    embed.set_footer(text=f"Published by {interaction.user.name}")
    embed.timestamp = discord.utils.utcnow()

    ping_message = get_ping_message(role_1, role_2, role_3)

    await interaction.response.send_message("Update announcement published successfully.", ephemeral=True)

    if ping_message:
        await interaction.channel.send(content=ping_message, embed=embed)
    else:
        await interaction.channel.send(embed=embed)

# =========================================================
# SHOWCASE COMMAND
# =========================================================
@bot.tree.command(name="showcase", description="Showcase weapons, maps, systems, or features")
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
    embed = discord.Embed(
        title=asset_name,
        description=description.replace("\\n", "\n"),
        color=COLORS["showcase"]
    )

    embed.add_field(name="Type", value="Development Showcase", inline=True)
    embed.add_field(name="Project", value="DeadZone", inline=True)
    embed.add_field(name="Visibility", value="Public Preview", inline=True)

    embed.set_thumbnail(url=bot.user.display_avatar.url)

    if media_url and media_url.startswith("http"):
        embed.set_image(url=media_url)

    embed.set_footer(text=f"Showcased by {interaction.user.name}")
    embed.timestamp = discord.utils.utcnow()

    await interaction.response.send_message("Showcase published successfully.", ephemeral=True)
    await interaction.channel.send(embed=embed)

# =========================================================
# STATUS COMMAND
# =========================================================
@bot.tree.command(name="status", description="Update development status")
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
async def status(interaction: discord.Interaction, state: app_commands.Choice[str], message: str):
    embed = discord.Embed(
        title="DeadZone Development Status",
        description=f"## {state.name}\n\n{message}",
        color=COLORS[state.value]
    )

    embed.add_field(name="Project", value="DeadZone", inline=True)
    embed.add_field(name="Current Activity", value=state.name, inline=True)
    embed.add_field(name="Team Status", value="Monitoring", inline=True)

    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.set_footer(text=f"Updated by {interaction.user.name}")
    embed.timestamp = discord.utils.utcnow()

    await interaction.response.send_message("Development status updated successfully.", ephemeral=True)
    await interaction.channel.send(embed=embed)

# =========================================================
# RULES COMMAND
# =========================================================
@bot.tree.command(name="rules", description="Publish server rules")
@app_commands.describe(
    title="Rules title",
    rules="Server rules",
    role_1="First role to ping",
    role_2="Second role to ping",
    role_3="Third role to ping"
)
@app_commands.checks.has_permissions(manage_guild=True)
async def rules(interaction: discord.Interaction, title: str, rules: str, role_1: discord.Role = None, role_2: discord.Role = None, role_3: discord.Role = None):
    embed = discord.Embed(title=title, description=rules.replace("\\n", "\n"), color=COLORS["rules"])

    if interaction.guild.icon:
        embed.set_thumbnail(url=interaction.guild.icon.url)

    embed.set_footer(text=f"Published by {interaction.user.name}")
    embed.timestamp = discord.utils.utcnow()

    ping_message = get_ping_message(role_1, role_2, role_3)

    await interaction.response.send_message("Server rules published successfully.", ephemeral=True)

    if ping_message:
        await interaction.channel.send(content=ping_message, embed=embed)
    else:
        await interaction.channel.send(embed=embed)

# =========================================================
# Error Handler
# =========================================================
@update.error
@showcase.error
@status.error
@rules.error
async def permission_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "You do not have permission to use this command.",
            ephemeral=True
        )

# =========================================================
# Start Bot
# =========================================================
keep_alive()

TOKEN = os.environ.get("DISCORD_TOKEN")

if TOKEN:
    bot.run(TOKEN)
else:
    print("DISCORD_TOKEN was not found in environment variables.")