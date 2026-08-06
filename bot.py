import discord
from discord.ext import commands
import os
import asyncio
from collections import defaultdict
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.moderation = True

bot = commands.Bot(command_prefix='-', intents=intents)

# لتخزين بيانات حماية السبام والرايد مؤقتاً
message_cache = defaultdict(list)
join_cache = defaultdict(list)

@bot.event
async def on_ready():
    print(f'البوت شغال وجاهز باسم: {bot.user}')

# دالة مساعدة لجلب روم السجلات (Logs) تلقائياً
def get_log_channel(guild):
    for channel in guild.text_channels:
        if "log" in channel.name.lower() or "سجلات" in channel.name or "سجل" in channel.name:
            return channel
    return None

# ==================== قائمة الأوامر (K) ====================
@bot.command(name="k")
async def help_menu(ctx):
    embed = discord.Embed(title="قائمة أوامر البوت", description="إليك كافة الأوامر المتاحة وطريقة استخدامها:", color=discord.Color.blue())
    
    embed.add_field(name="-ping", value="يقيس سرعة استجابة البوت ويرد بـ Pong مع السرعة بالمللي ثانية.", inline=False)
    embed.add_field(name="-clear [العدد]", value="يحذف عدداً محدداً من الرسائل دفعة واحدة (يتطلب صلاحية إدارة الرسائل).", inline=False)
    embed.add_field(name="-server", value="يعرض بطاقة معلومات السيرفر (اسم السيرفر، المالك، عدد الأعضاء، وتاريخ الإنشاء).", inline=False)
    embed.add_field(name="-avatar [@user]", value="يعرض صورة البروفايل (الأفاتار) الخاصة بك أو لعضو آخر تختاره.", inline=False)
    embed.add_field(name="-rules", value="ينشر رسالة إمبيد رسمية تحتوي على قوانين السيرفر (يتطلب صلاحية المسؤول).", inline=False)
    embed.add_field(name="-suggest [الاقتراح]", value="يرسل اقتراحك بشكل مرتب في الشات مع تفاعل الأزرار للتصويت.", inline=False)
    embed.add_field(name="-announce [العنوان] [النص]", value="يرسل إمبيد إعلاني رسمي ومرتب في الشات مع اسم الإداري الذي أرسله (يتطلب صلاحية المسؤول).", inline=False)
    embed.add_field(name="-log", value="يعرض حالة نظام السجلات والرومات الخاصة بها في السيرفر.", inline=False)
    embed.add_field(name="الردود الذكية (بدون بريفكس)", value="• منو قطوتي -> مياو\n• منو بطتي -> بط بط\n• شاطر / شاطرة -> كلزق", inline=False)
    embed.add_field(name="حماية السيرفر والسجلات", value="• منع السبام التلقائي\n• مكافحة الرايد (دخول جماعي مريب)\n• سجلات كاملة (Logs) للرومات والرتب والأعضاء والرسائل المحذوفة", inline=False)
    
    await ctx.send(embed=embed)

# ==================== أمر عرض معلومات ونظام السجلات (-log) ====================
@bot.command(name="log")
@commands.has_permissions(administrator=True)
async def log_status(ctx):
    log_chan = get_log_channel(ctx.guild)
    channel_name = log_chan.mention if log_chan else "⚠️ لم يتم العثور على روم (أنشئ روم يحتوي على كلمة log أو سجلات)"
    
    embed = discord.Embed(title="📊 لوحة تحكم وحالة السجلات (Logs)", color=discord.Color.dark_blue())
    embed.add_field(name="📌 روم السجلات الحالي", value=channel_name, inline=False)
    embed.add_field(name="🛡️ الحماية المفعلة", value="• منع السبام التلقائي\n• مكافحة الرايد\n• رصد حذف وتعديل الرسائل\n• رصد إنشاء وحذف الرومات والرتب", inline=False)
    embed.set_footer(text=f"بواسطة: {ctx.author.display_name}")
    
    await ctx.send(embed=embed)

# ==================== نظام الحماية والسبام والرايد ====================
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    content = message.content.strip()

    # الردود الذكية
    if content == "منو قطوتي":
        await message.channel.send("مياو")
    elif content == "منو بطتي":
        await message.channel.send("بط بط")
    elif content == "شاطر" or content == "شاطرة":
        await message.channel.send("كلزق")

    # 1. نظام منع السبام التلقائي (Anti-Spam)
    author_id = message.author.id
    current_time = asyncio.get_event_loop().time()
    
    message_cache[author_id] = [t for t in message_cache[author_id] if current_time - t < 5]
    message_cache[author_id].append(current_time)

    if len(message_cache[author_id]) > 5:
        try:
            await message.delete()
            log_chan = get_log_channel(message.guild)
            if log_chan:
                await log_chan.send(f"⚠️ **تنبيه سبام:** تم حذف رسالة لـ {message.author.mention} بسبب إرسال رسائل متكررة بسرعة.")
        except:
            pass
        return

    await bot.process_commands(message)

# 2. مكافحة الرايد (Anti-Raid عند دخول أعضاء كثر بسرعة)
@bot.event
async def on_member_join(member: discord.Member):
    guild = member.guild
    current_time = asyncio.get_event_loop().time()
    
    join_cache[guild.id].append(current_time)
    join_cache[guild.id] = [t for t in join_cache[guild.id] if current_time - t < 10]

    log_chan = get_log_channel(guild)

    if len(join_cache[guild.id]) > 5:
        if log_chan:
            await log_chan.send(f"🚨 **تحذير رايد خطير!** تم رصد دخول عدد كبير من الأعضاء في وقت قياسي ({len(join_cache[guild.id])} أعضاء).")

    # الترحيب العادي
    for channel in guild.text_channels:
        if "welcome" in channel.name.lower() or "ترحيب" in channel.name or "الرئيسية" in channel.name:
            await channel.send(f"حياك الله {member.mention}، نورت السيرفر!")
            break

# ==================== سجلات الحماية الكاملة (Logs) ====================

@bot.event
async def on_message_delete(message):
    if message.author.bot or not message.guild:
        return
    log_chan = get_log_channel(message.guild)
    if log_chan:
        embed = discord.Embed(title="🗑️ حذف رسالة", color=discord.Color.red())
        embed.add_field(name="الكاتب", value=message.author.mention, inline=True)
        embed.add_field(name="الروم", value=message.channel.mention, inline=True)
        embed.add_field(name="المحتوى", value=message.content or "محتوى غير نصي (صورة/ملف)", inline=False)
        await log_chan.send(embed=embed)

@bot.event
async def on_message_edit(before, after):
    if before.author.bot or not before.guild or before.content == after.content:
        return
    log_chan = get_log_channel(before.guild)
    if log_chan:
        embed = discord.Embed(title="✏️ تعديل رسالة", color=discord.Color.gold())
        embed.add_field(name="الكاتب", value=before.author.mention, inline=True)
        embed.add_field(name="الروم", value=before.channel.mention, inline=True)
        embed.add_field(name="قبل التعديل", value=before.content, inline=False)
        embed.add_field(name="بعد التعديل", value=after.content, inline=False)
        await log_chan.send(embed=embed)

@bot.event
async def on_guild_channel_create(channel):
    log_chan = get_log_channel(channel.guild)
    if log_chan:
        await log_chan.send(f"📁 **تم إنشاء روم جديد:** `{channel.name}` (نوعه: {channel.type})")

@bot.event
async def on_guild_channel_delete(channel):
    log_chan = get_log_channel(channel.guild)
    if log_chan:
        await log_chan.send(f"🗑️ **تم حذف روم:** `{channel.name}`")

@bot.event
async def on_guild_role_create(role):
    log_chan = get_log_channel(role.guild)
    if log_chan:
        await log_chan.send(f"➕ **تم إنشاء رتبة جديدة:** `{role.name}`")

@bot.event
async def on_guild_role_delete(role):
    log_chan = get_log_channel(role.guild)
    if log_chan:
        await log_chan.send(f"➖ **تم حذف رتبة:** `{role.name}`")

# ==================== الأوامر الأساسية ====================
@bot.command(name="ping")
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"Pong! السرعة: `{latency}ms`")

@bot.command(name="clear")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    if amount <= 0:
        await ctx.send("الرجاء إدخال رقم أكبر من الصفر.")
        return
    await ctx.message.delete()
    deleted = await ctx.channel.purge(limit=amount)
    msg = await ctx.send(f"تم حذف `{len(deleted)}` رسالة بنجاح.")
    await asyncio.sleep(3)
    try: await msg.delete()
    except: pass

@bot.command(name="server")
async def server_info(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"معلومات سيرفر: {guild.name}", color=discord.Color.blue())
    if guild.icon: embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="صاحب السيرفر", value=guild.owner.mention, inline=True)
    embed.add_field(name="عدد الأعضاء", value=str(guild.member_count), inline=True)
    embed.add_field(name="تاريخ الإنشاء", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
    await ctx.send(embed=embed)

@bot.command(name="avatar")
async def avatar(ctx, user: discord.Member = None):
    target = user or ctx.author
    embed = discord.Embed(title=f"صورة الأفاتار لـ {target.name}", color=discord.Color.gold())
    embed.set_image(url=target.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="rules")
@commands.has_permissions(administrator=True)
async def rules(ctx):
    await ctx.message.delete()
    embed = discord.Embed(title="قوانين السيرفر", description="الرجاء الالتزام بالقوانين لضمان تجربة ممتعة للجميع:", color=discord.Color.red())
    embed.add_field(name="1. الاحترام المتبادل", value="يمنع الشتم أو الاستهزاء بأي عضو.", inline=False)
    embed.add_field(name="2. عدم السبام", value="يمنع إرسال الرسائل المتكررة أو الإزعاج.", inline=False)
    embed.add_field(name="3. الإعلانات", value="يمنع نشر روابط سيرفرات أخرى أو روابط خارجية.", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="suggest")
async def suggest(ctx, *, suggestion: str):
    await ctx.message.delete()
    embed = discord.Embed(title="اقتراح جديد", description=suggestion, color=discord.Color.green())
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")

@bot.command(name="announce")
@commands.has_permissions(administrator=True)
async def announce(ctx, title: str, *, message: str):
    await ctx.message.delete()
    embed = discord.Embed(title=f"{title}", description=message, color=discord.Color.orange())
    embed.set_footer(text=f"بواسطة: {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

keep_alive()
bot.run(os.environ['TOKEN'])
