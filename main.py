import os
import random
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

# ========================================================
# ระบบเว็บเซิร์ฟเวอร์สำหรับหลอก Render (Keep Alive แบบเปิดคู่กัน)
# ========================================================
app = Flask('')

@app.route('/')
def home():
    return "บอทของคุณกำลังทำงานออนไลน์อยู่ 24/7!"

def run_web():
    # ดึงค่าพอร์ตที่ Render กำหนดมาให้ (ปกติคือพอร์ต 10000)
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    # แยกกระบวนการไปรันเว็บเซิร์ฟเวอร์หลอกที่เบื้องหลัง ไม่ให้กวนบอทดิสคอร์ด
    t = Thread(target=run_web)
    t.start()

# ========================================================
# ระบบ Discord Bot
# ========================================================
intents = discord.Intents.default()
intents.message_content = True  # สิทธิ์อ่านข้อความคำสั่ง
intents.members = True          # สิทธิ์ตรวจสอบสมาชิก

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'=================================')
    print(f'บอท {bot.user} ออนไลน์บน Render สำเร็จแล้ว!')
    print(f'=================================')

@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"Pong! 📱 (ความเร็ว: {latency}ms)")

@bot.command()
async def say(ctx, *, text):
    await ctx.message.delete()
    await ctx.send(text)

@bot.command()
async def roll(ctx):
    number = random.randint(1, 100)
    await ctx.send(f"🎲 ผลการสุ่มเลข (1-100): **{number}**")

@bot.command()
async def userinfo(ctx):
    user = ctx.author
    embed = discord.Embed(title=f"ข้อมูลของ {user.name}", color=discord.Color.blue())
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name="ชื่อในระบบ", value=user.mention, inline=True)
    embed.add_field(name="วันที่สร้างบัญชี", value=user.created_at.strftime("%d/%m/%Y"), inline=True)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clean(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 ลบข้อความเรียบร้อยแล้ว {amount} ข้อความ!", delete_after=5)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"🚪 เตะ {member.mention} สำเร็จ! เหตุผล: {reason}")

@clean.error
@kick.error
async def permission_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ คุณไม่มีสิทธิ์ใช้งานคำสั่งนี้ครับ!")

# เปิดใช้ระบบเว็บหลอกเบื้องหลัง
keep_alive()

# ดึงค่า TOKEN จาก Environment Variable ของ Render
TOKEN = os.environ.get('DISCORD_TOKEN')
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ ตรวจไม่พบ DISCORD_TOKEN ในหน้า Environment ของ Render กรุณาเช็กการตั้งค่า!")
