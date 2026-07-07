import os
import asyncio
import discord
from discord import app_commands
from flask import Flask
from threading import Thread
from mcrcon import MCRcon

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
# Minecraft RCON Config
# =========================================================
# host/port มาจากเซิร์ฟเวอร์ของคุณ (th1.xd.in.th : 24790)
# ส่วนรหัสผ่าน RCON ต้องตั้งเป็น Environment Variable ชื่อ MCRCON_PASSWORD
# (ห้ามใส่รหัสผ่านตรงๆ ในโค้ด)
MCRCON_HOST = os.environ.get("MCRCON_HOST", "th1.xd.in.th")
MCRCON_PORT = int(os.environ.get("MCRCON_PORT", "25575"))
MCRCON_PASSWORD = os.environ.get("MCRCON_PASSWORD")

def _rcon_command_sync(command: str) -> str:
    """ฟังก์ชัน sync ที่ยิงคำสั่งไปที่เซิร์ฟเวอร์ Minecraft ผ่าน RCON"""
    with MCRcon(MCRCON_HOST, MCRCON_PASSWORD, port=MCRCON_PORT, timeout=10) as mcr:
        response = mcr.command(command)
        return response

async def send_mc_command(command: str) -> tuple[bool, str]:
    """
    เวอร์ชัน async สำหรับเรียกใช้ใน discord.py โดยไม่บล็อค event loop
    คืนค่าเป็น (สำเร็จหรือไม่, ข้อความผลลัพธ์หรือสาเหตุที่ผิดพลาด)
    """
    if not MCRCON_PASSWORD:
        error_msg = "ยังไม่ได้ตั้งค่า MCRCON_PASSWORD ใน Environment Variables"
        print(error_msg)
        return False, error_msg
    try:
        result = await asyncio.to_thread(_rcon_command_sync, command)
        return True, result
    except ConnectionRefusedError:
        error_msg = f"เชื่อมต่อ {MCRCON_HOST}:{MCRCON_PORT} ไม่ได้ (Connection refused) — RCON อาจยังไม่เปิด หรือพอร์ตปิดอยู่"
        print(f"RCON command failed: {error_msg}")
        return False, error_msg
    except TimeoutError:
        error_msg = f"เชื่อมต่อ {MCRCON_HOST}:{MCRCON_PORT} หมดเวลา (Timeout) — เช็ค Firewall/Allocation ของพอร์ตนี้"
        print(f"RCON command failed: {error_msg}")
        return False, error_msg
    except Exception as e:
        error_text = str(e)
        if "auth" in error_text.lower() or "login" in error_text.lower():
            error_msg = "รหัสผ่าน RCON ไม่ถูกต้อง (Authentication failed) — เช็ค MCRCON_PASSWORD ให้ตรงกับ rcon.password ใน server.properties"
        else:
            error_msg = f"เกิดข้อผิดพลาด: {error_text}"
        print(f"RCON command failed: {error_msg}")
        return False, error_msg

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
            name="Playing DeadZone"
        )
    )

# =========================================================
# POLL COMMAND
# =========================================================
@bot.tree.command(name="poll", description="Create a community poll")
@app_commands.describe(
    question="Poll question",
    options="Choices separated with |",
    duration="Poll duration in minutes",
    role_1="First role to ping",
    role_2="Second role to ping",
    role_3="Third role to ping"
)
@app_commands.checks.has_permissions(manage_messages=True)
async def poll(
    interaction: discord.Interaction,
    question: str,
    options: str,
    duration: int,
    role_1: discord.Role = None,
    role_2: discord.Role = None,
    role_3: discord.Role = None
):
    choices = [choice.strip() for choice in options.split("|")]

    if len(choices) < 2:
        return await interaction.response.send_message(
            "A poll must have at least 2 options.",
            ephemeral=True
        )

    if len(choices) > 10:
        return await interaction.response.send_message(
            "Polls can only have up to 10 options.",
            ephemeral=True
        )

    reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

    description = ""

    for i, choice in enumerate(choices):
        description += f"{reactions[i]} {choice}\n"

    embed = discord.Embed(
        title="Community Poll",
        description=f"## {question}\n\n{description}",
        color=discord.Color.from_rgb(88, 101, 242)
    )

    embed.set_footer(text=f"Poll created by {interaction.user.name}")
    embed.timestamp = discord.utils.utcnow()

    ping_message = get_ping_message(role_1, role_2, role_3)

    await interaction.response.send_message(
        "Poll created successfully.",
        ephemeral=True
    )

    if ping_message:
        message = await interaction.channel.send(content=ping_message, embed=embed)
    else:
        message = await interaction.channel.send(embed=embed)

    for i in range(len(choices)):
        await message.add_reaction(reactions[i])

    await asyncio.sleep(duration * 60)

    updated_embed = message.embeds[0]
    updated_embed.color = discord.Color.dark_grey()

    await message.edit(embed=updated_embed)

# =========================================================
# BAN COMMAND (Discord + Minecraft ผ่าน RCON)
# =========================================================
ALLOWED_ROLES = [
    "DeadZone HR",
    "Head Moderator"
]

@bot.tree.command(name="ban", description="Ban a member from the server (and optionally the Minecraft server)")
@app_commands.describe(
    member="Member to ban",
    reason="Reason for the ban",
    mc_username="ชื่อผู้เล่นในเกม Minecraft (ถ้าต้องการแบนในเซิร์ฟเวอร์ด้วย)"
)
async def ban(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str = "No reason provided",
    mc_username: str = None
):
    user_roles = [role.name for role in interaction.user.roles]

    if not any(role in ALLOWED_ROLES for role in user_roles):
        return await interaction.response.send_message(
            "You do not have permission to use this command.",
            ephemeral=True
        )

    if member.top_role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
        return await interaction.response.send_message(
            "You cannot ban this member.",
            ephemeral=True
        )

    await interaction.response.defer(ephemeral=True)

    # --- แบนออกจาก Discord ---
    await member.ban(reason=reason)

    # --- แบนในเซิร์ฟเวอร์ Minecraft ผ่าน RCON (ถ้ามีการกรอกชื่อในเกม) ---
    mc_status_text = "ไม่ได้ระบุชื่อในเกม (ข้ามการแบนในเซิร์ฟเวอร์)"
    if mc_username:
        success, info = await send_mc_command(f"ban {mc_username} {reason}")
        if success:
            mc_status_text = f"แบนในเซิร์ฟเวอร์ Minecraft สำเร็จ ({mc_username})"
        else:
            mc_status_text = f"แบนในเซิร์ฟเวอร์ Minecraft ไม่สำเร็จ ({mc_username})\n{info}"

    embed = discord.Embed(
        title="Member Banned",
        description=f"{member.mention} has been banned from the server.",
        color=discord.Color.red()
    )

    embed.add_field(name="Member", value=f"{member} ({member.id})", inline=False)
    embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
    embed.add_field(name="Reason", value=reason, inline=True)
    embed.add_field(name="Minecraft Server", value=mc_status_text, inline=False)

    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f"Banned by {interaction.user.name}")
    embed.timestamp = discord.utils.utcnow()

    await interaction.followup.send("Member banned successfully.", ephemeral=True)
    await interaction.channel.send(embed=embed)

# =========================================================
# KICK COMMAND (Discord + Minecraft ผ่าน RCON)
# =========================================================
@bot.tree.command(name="kick", description="Kick a member from the server (and optionally the Minecraft server)")
@app_commands.describe(
    member="Member to kick",
    reason="Reason for the kick",
    mc_username="ชื่อผู้เล่นในเกม Minecraft (ถ้าต้องการเตะออกจากเซิร์ฟเวอร์ด้วย)"
)
async def kick(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str = "No reason provided",
    mc_username: str = None
):
    user_roles = [role.name for role in interaction.user.roles]

    if not any(role in ALLOWED_ROLES for role in user_roles):
        return await interaction.response.send_message(
            "You do not have permission to use this command.",
            ephemeral=True
        )

    if member.top_role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
        return await interaction.response.send_message(
            "You cannot kick this member.",
            ephemeral=True
        )

    await interaction.response.defer(ephemeral=True)

    # --- เตะออกจาก Discord ---
    await member.kick(reason=reason)

    # --- เตะออกจากเซิร์ฟเวอร์ Minecraft ผ่าน RCON (ถ้ามีการกรอกชื่อในเกม) ---
    mc_status_text = "ไม่ได้ระบุชื่อในเกม (ข้ามการเตะในเซิร์ฟเวอร์)"
    if mc_username:
        success, info = await send_mc_command(f"kick {mc_username} {reason}")
        if success:
            mc_status_text = f"เตะออกจากเซิร์ฟเวอร์ Minecraft สำเร็จ ({mc_username})"
        else:
            mc_status_text = f"เตะออกจากเซิร์ฟเวอร์ Minecraft ไม่สำเร็จ ({mc_username})\n{info}"

    embed = discord.Embed(
        title="Member Kicked",
        description=f"{member.mention} has been kicked from the server.",
        color=discord.Color.orange()
    )

    embed.add_field(name="Member", value=f"{member} ({member.id})", inline=False)
    embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
    embed.add_field(name="Reason", value=reason, inline=True)
    embed.add_field(name="Minecraft Server", value=mc_status_text, inline=False)

    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f"Kicked by {interaction.user.name}")
    embed.timestamp = discord.utils.utcnow()

    await interaction.followup.send("Member kicked successfully.", ephemeral=True)
    await interaction.channel.send(embed=embed)

# =========================================================
# UNBAN COMMAND (Discord + Minecraft ผ่าน RCON)
# =========================================================
@bot.tree.command(name="unban", description="Unban a user from the server")
@app_commands.describe(
    user_id="User ID to unban",
    mc_username="ชื่อผู้เล่นในเกม Minecraft (ถ้าต้องการปลดแบนในเซิร์ฟเวอร์ด้วย)"
)
async def unban(interaction: discord.Interaction, user_id: str, mc_username: str = None):
    user_roles = [role.name for role in interaction.user.roles]

    if not any(role in ALLOWED_ROLES for role in user_roles):
        return await interaction.response.send_message(
            "You do not have permission to use this command.",
            ephemeral=True
        )

    try:
        user = await bot.fetch_user(int(user_id))
        await interaction.guild.unban(user)

        mc_status_text = "ไม่ได้ระบุชื่อในเกม (ข้ามการปลดแบนในเซิร์ฟเวอร์)"
        if mc_username:
            success, info = await send_mc_command(f"pardon {mc_username}")
            if success:
                mc_status_text = f"ปลดแบนในเซิร์ฟเวอร์ Minecraft สำเร็จ ({mc_username})"
            else:
                mc_status_text = f"ปลดแบนในเซิร์ฟเวอร์ Minecraft ไม่สำเร็จ ({mc_username})\n{info}"

        embed = discord.Embed(
            title="Member Unbanned",
            description=f"{user.mention} has been unbanned.",
            color=discord.Color.green()
        )

        embed.add_field(name="User", value=f"{user} ({user.id})", inline=False)
        embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
        embed.add_field(name="Minecraft Server", value=mc_status_text, inline=False)

        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"Unbanned by {interaction.user.name}")
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message("Member unbanned successfully.", ephemeral=True)
        await interaction.channel.send(embed=embed)

    except Exception:
        await interaction.response.send_message(
            "Failed to unban user. Invalid ID or user is not banned.",
            ephemeral=True
        )

# =========================================================
# MCBAN COMMAND (แบนเฉพาะในเซิร์ฟเวอร์ Minecraft ผ่าน RCON)
# =========================================================
@bot.tree.command(name="mcban", description="Ban a player from the Minecraft server only (RCON)")
@app_commands.describe(
    mc_username="ชื่อผู้เล่นในเกม Minecraft ที่ต้องการแบน",
    reason="เหตุผลในการแบน"
)
async def mcban(interaction: discord.Interaction, mc_username: str, reason: str = "No reason provided"):
    user_roles = [role.name for role in interaction.user.roles]

    if not any(role in ALLOWED_ROLES for role in user_roles):
        return await interaction.response.send_message(
            "You do not have permission to use this command.",
            ephemeral=True
        )

    await interaction.response.defer(ephemeral=True)

    success, info = await send_mc_command(f"ban {mc_username} {reason}")

    if not success:
        return await interaction.followup.send(
            f"แบน `{mc_username}` ในเซิร์ฟเวอร์ Minecraft ไม่สำเร็จ\n{info}",
            ephemeral=True
        )

    embed = discord.Embed(
        title="Minecraft Player Banned",
        description=f"`{mc_username}` has been banned from the Minecraft server.",
        color=discord.Color.red()
    )

    embed.add_field(name="Player", value=mc_username, inline=True)
    embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)

    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.set_footer(text=f"Banned by {interaction.user.name}")
    embed.timestamp = discord.utils.utcnow()

    await interaction.followup.send("Minecraft ban executed successfully.", ephemeral=True)
    await interaction.channel.send(embed=embed)

# =========================================================
# MCUNBAN COMMAND (ปลดแบนเฉพาะในเซิร์ฟเวอร์ Minecraft ผ่าน RCON)
# =========================================================
@bot.tree.command(name="mcunban", description="Unban a player from the Minecraft server only (RCON)")
@app_commands.describe(
    mc_username="ชื่อผู้เล่นในเกม Minecraft ที่ต้องการปลดแบน"
)
async def mcunban(interaction: discord.Interaction, mc_username: str):
    user_roles = [role.name for role in interaction.user.roles]

    if not any(role in ALLOWED_ROLES for role in user_roles):
        return await interaction.response.send_message(
            "You do not have permission to use this command.",
            ephemeral=True
        )

    await interaction.response.defer(ephemeral=True)

    success, info = await send_mc_command(f"pardon {mc_username}")

    if not success:
        return await interaction.followup.send(
            f"ปลดแบน `{mc_username}` ในเซิร์ฟเวอร์ Minecraft ไม่สำเร็จ\n{info}",
            ephemeral=True
        )

    embed = discord.Embed(
        title="Minecraft Player Unbanned",
        description=f"`{mc_username}` has been unbanned from the Minecraft server.",
        color=discord.Color.green()
    )

    embed.add_field(name="Player", value=mc_username, inline=True)
    embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)

    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.set_footer(text=f"Unbanned by {interaction.user.name}")
    embed.timestamp = discord.utils.utcnow()

    await interaction.followup.send("Minecraft unban executed successfully.", ephemeral=True)
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
        description=f"## {title}\n\n{details.replace(chr(92)+'n', chr(10))}",
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
# MEMBER JOIN EVENT
# =========================================================
WELCOME_CHANNEL_ID = 948801995907678261
RULES_CHANNEL_URL = "https://discord.com/channels/948801995907678259/948810517852610611"

@bot.event
async def on_member_join(member: discord.Member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)

    if not channel:
        return

    embed = discord.Embed(
        title="Welcome to DeadZone Server Community",
        description=(
            f"Welcome {member.mention} to the server.\n\n"
            f"Please read the server rules before chatting:\n"
            f"{RULES_CHANNEL_URL}"
        ),
        color=discord.Color.from_rgb(88, 101, 242)
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    if member.guild.icon:
        embed.set_image(url=member.guild.icon.url)

    embed.set_footer(text="DeadZone Community")
    embed.timestamp = discord.utils.utcnow()

    await channel.send(content=member.mention, embed=embed)

# =========================================================
# MEMBER LEAVE EVENT
# =========================================================
@bot.event
async def on_member_remove(member: discord.Member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)

    if not channel:
        return

    embed = discord.Embed(
        title="Member Left",
        description=f"{member} has left the server.",
        color=discord.Color.from_rgb(240, 71, 71)
    )

    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text="DeadZone Community")
    embed.timestamp = discord.utils.utcnow()

    await channel.send(embed=embed)

# =========================================================
# Start Bot
# =========================================================
keep_alive()

TOKEN = os.environ.get("DISCORD_TOKEN")

if TOKEN:
    bot.run(TOKEN)
else:
    print("DISCORD_TOKEN was not found in environment variables.")
