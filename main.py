import os
import random
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
    return "Your bot is running 24/7 online!"

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
        # Set required intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(intents=intents)
        # Create Command Tree for Slash Commands
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Sync slash commands globally across all servers
        await self.tree.sync()
        print("Slash commands synced globally!")

bot = MyBot()

@bot.event
async def on_ready():
    print(f'=================================')
    print(f'Logged in as {bot.user}')
    print(f'Bot is ready on Render 24/7!')
    print(f'=================================')

# ========================================================
# Slash Commands with Descriptions
# ========================================================

# 1. /ping Command
@bot.tree.command(name="ping", description="Check the bot's response speed latency")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"Pong! 📱 (Latency: {latency}ms)")

# 2. /say Command
@bot.tree.command(name="say", description="Make the bot repeat a message sent by you")
@app_commands.describe(text="The message you want the bot to say")
async def say(interaction: discord.Interaction, text: str):
    # Reply silently to the sender, then send the message to the channel
    await interaction.response.send_message("Message sent!", ephemeral=True)
    await interaction.channel.send(text)

# 3. /roll Command
@bot.tree.command(name="roll", description="Roll a random number between 1 and 100")
async def roll(interaction: discord.Interaction):
    number = random.randint(1, 100)
    await interaction.response.send_message(f"🎲 Random Number Result (1-100): **{number}**")

# 4. /userinfo Command
@bot.tree.command(name="userinfo", description="Display your server profile information card")
async def userinfo(interaction: discord.Interaction):
    user = interaction.user
    embed = discord.Embed(title=f"User Info: {user.name}", color=discord.Color.blue())
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name="Username", value=user.mention, inline=True)
    embed.add_field(name="Account Created At", value=user.created_at.strftime("%d/%m/%Y"), inline=True)
    await interaction.response.send_message(embed=embed)

# 5. /clean Command (Requires Manage Messages Permission)
@bot.tree.command(name="clean", description="Bulk delete messages in this channel quickly")
@app_commands.describe(amount="Number of messages to delete")
@app_commands.checks.has_permissions(manage_messages=True)
async def clean(interaction: discord.Interaction, amount: int):
    await interaction.response.send_message(f"🧹 Clearing {amount} messages...", ephemeral=True)
    await interaction.channel.purge(limit=amount)

# 6. /kick Command (Requires Kick Members Permission)
@bot.tree.command(name="kick", description="Kick a member from this server")
@app_commands.describe(member="The member to kick", reason="The reason for kicking")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"🚪 Successfully kicked {member.name}! Reason: {reason}")

# Error handler for missing permissions on Admin commands
@clean.error
@kick.error
async def permission_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ You do not have permission to use this command!", ephemeral=True)

# Run Web Server first
keep_alive()

# Run the bot using the Token from Render Environment
TOKEN = os.environ.get('DISCORD_TOKEN')
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ DISCORD_TOKEN not found in Render Environment variables!")
