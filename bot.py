import discord
from discord.ext import commands
import os
import asyncio
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='-', intents=intents)

@bot.event
async def on_ready():
    print(f'البوت شغال وجاهز باسم: {bot.user}')

# ==================== قائمة الأوامر (K) ====================
@bot.command(name="k")
async def help_menu(ctx):
    embed = discord.Embed(title="📜 قائمة أوامر البوت", description="إليك كافة الأوامر المتاحة وطريقة استخدامها:", color=discord.Color.blue())
    
    embed.add_field(name="🏓 -ping", value="يقيس سرعة استجابة البوت ويرد بـ Pong مع السرعة بالمللي ثانية.", inline=False)
    embed.add_field(name="🧹 -clear [العدد]", value="يحذف عدداً محدداً من الرسائل دفعة واحدة (يتطلب صلاحية إدارة الرسائل).", inline=False)
    embed.add_field(name="📊 -server", value="يعرض بطاقة معلومات السيرفر (اسم السيرفر، المالك، عدد الأعضاء، وتاريخ الإنشاء).", inline=False)
    embed.add_field(name="🖼️ -avatar [@user]", value="يعرض صورة البروفايل (الأفاتار) الخاصة بك أو لعضو آخر تختاره.", inline=False)
    embed.add_field(name="📜 -rules", value="ينشر رسالة إمبيد رسمية تحتوي على قوانين السيرفر (يتطلب صلاحية المسؤول).", inline=False)
    embed.add_field(name="💡 -suggest [الاقتراح]", value="يرسل اقتراحك بشكل مرتب في الشات مع تفاعل الأزرار 👍 و 👎 لتصويت الأعضاء.", inline=False)
    embed.add_field(name="📢 -announce [العنوان] [النص]", value="يرسل إمبيد إعلاني رسمي ومرتب في الشات مع اسم الإداري الذي أرسله (يتطلب صلاحية المسؤول).", inline=False)
    embed.add_field(name="🐾 الردود الطريفة (بدون بريفكس)", value="• منو قطوتي -> مياو 🐱\n• منو كلبي -> هو هو 🐶\n• منو بطتي -> بط بط 🦆", inline=False)
    embed.add_field(name="👋 الترحيب التلقائي", value="وظيفة تلقائية تعمل وحدها فور دخول أي عضو جديد للسيرفر وترسل ترحيباً في روم الترحيب.", inline=False)
    
    await ctx.send(embed=embed)

# ==================== الردود الذكية (بدون بريفكس وبدون شخطة) ====================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.strip()

    if content == "منو قطوتي":
        await message.channel.send("مياو 🐱")
    elif content == "منو كلبي":
        await message.channel.send("هو هو 🐶")
    elif content == "منو بطتي":
        await message.channel.send("بط بط 🦆")

    # مهم جداً لتشغيل باقي الأوامر (مثل -k و -ping وغيرها)
    await bot.process_commands(message)

# ==================== 1. بوت بينج (Ping) ====================
@bot.command(name="ping")
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! السرعة: `{latency}ms`")

# ==================== 2. بوت حذف الشات (Clear) ====================
@bot.command(name="clear")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    if amount <= 0:
        await ctx.send("❌ الرجاء إدخال رقم أكبر من الصفر.")
        return
    
    await ctx.message.delete()
    deleted = await ctx.channel.purge(limit=amount)
    msg = await ctx.send(f"✅ تم حذف `{len(deleted)}` رسالة بنجاح.")
    await asyncio.sleep(3)
    try:
        await msg.delete()
    except:
        pass

# ==================== 3. بوت ترحيب (Welcome) ====================
@bot.event
async def on_member_join(member: discord.Member):
    for channel in member.guild.text_channels:
        if "welcome" in channel.name or "ترحيب" in channel.name or "الرئيسية" in channel.name:
            await channel.send(f"حياك الله {member.mention}، نورت السيرفر! 🎉")
            break

# ==================== 4. بوت معلومات (Server Info) ====================
@bot.command(name="server")
async def server_info(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"📊 معلومات سيرفر: {guild.name}", color=discord.Color.blue())
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="👑 صاحب السيرفر", value=guild.owner.mention, inline=True)
    embed.add_field(name="👥 عدد الأعضاء", value=str(guild.member_count), inline=True)
    embed.add_field(name="📅 تاريخ الإنشاء", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
    await ctx.send(embed=embed)

# ==================== 5. بوت أفاتار (Avatar) ====================
@bot.command(name="avatar")
async def avatar(ctx, user: discord.Member = None):
    target = user or ctx.author
    embed = discord.Embed(title=f"🖼️ صورة الأفاتار لـ {target.name}", color=discord.Color.gold())
    embed.set_image(url=target.display_avatar.url)
    await ctx.send(embed=embed)

# ==================== 6. بوت قوانين (Rules) ====================
@bot.command(name="rules")
@commands.has_permissions(administrator=True)
async def rules(ctx):
    await ctx.message.delete()
    embed = discord.Embed(title="📜 قوانين السيرفر", description="الرجاء الالتزام بالقوانين لضمان تجربة ممتعة للجميع:", color=discord.Color.red())
    embed.add_field(name="1️⃣ الاحترام المتبادل", value="يمنع الشتم أو الاستهزاء بأي عضو.", inline=False)
    embed.add_field(name="2️⃣ عدم السبام", value="يمنع إرسال الرسائل المتكررة أو الإزعاج.", inline=False)
    embed.add_field(name="3️⃣ الإعلانات", value="يمنع نشر روابط سيرفرات أخرى أو روابط خارجية.", inline=False)
    await ctx.send(embed=embed)

# ==================== 7. بوت اقتراحات (Suggest) ====================
@bot.command(name="suggest")
async def suggest(ctx, *, suggestion: str):
    await ctx.message.delete()
    embed = discord.Embed(title="💡 اقتراح جديد", description=suggestion, color=discord.Color.green())
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
    
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")

# ==================== 8. بوت إعلان (Announce) ====================
@bot.command(name="announce")
@commands.has_permissions(administrator=True)
async def announce(ctx, title: str, *, message: str):
    await ctx.message.delete()
    embed = discord.Embed(title=f"📢 {title}", description=message, color=discord.Color.orange())
    embed.set_footer(text=f"بواسطة: {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
    
    await ctx.send(embed=embed)

keep_alive()
bot.run(os.environ['TOKEN'])
