import discord
from discord.ext import commands
import os
import asyncio
import random
import time
from collections import defaultdict
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.moderation = True

bot = commands.Bot(command_prefix='-', intents=intents)

# تخزين بيانات حماية السبام والرايد
message_cache = defaultdict(list)
join_cache = defaultdict(list)

# قواعد البيانات الوهمية للاقتصاد والمتجر
economy_db = {}
cooldowns = {"daily": {}, "work": {}, "beg": {}}
inventory_db = defaultdict(list)

shop_items = {
    "color": {"name": "تغيير لون الاسم", "price": 5000, "desc": "🎨 يتيح لك تغيير لون اسمك"},
    "vip": {"name": "رتبة VIP يوم", "price": 15000, "desc": "⭐ رتبة VIP لمدة يوم كامل"},
    "elite": {"name": "رتبة Elite أسبوع", "price": 50000, "desc": "👑 رتبة Elite لمدة أسبوع"},
    "ticket": {"name": "دخول سحب خاص", "price": 10000, "desc": "🎟️ تذكرة دخول للسحب القادم"}
}

@bot.event
async def on_ready():
    print(f'البوت الشامل شغال وجاهز باسم: {bot.user}')

def get_balance(user_id):
    return economy_db.get(user_id, 0)

def update_balance(user_id, amount):
    economy_db[user_id] = get_balance(user_id) + amount
    if economy_db[user_id] < 0:
        economy_db[user_id] = 0

def get_log_channel(guild):
    for channel in guild.text_channels:
        if "log" in channel.name.lower() or "سجلات" in channel.name or "سجل" in channel.name:
            return channel
    return None

def get_tell_channel(guild):
    for channel in guild.text_channels:
        if "tell" in channel.name.lower() or "صارحني" in channel.name or "مصارحات" in channel.name:
            return channel
    return None

# ==================== قائمة الأوامر العامة (-k) ====================
@bot.command(name="k")
async def help_menu(ctx):
    embed = discord.Embed(title="قائمة أوامر البوت الشاملة", description="إليك كافة الأوامر المتاحة وطريقة استخدامها:", color=discord.Color.blue())
    
    embed.add_field(name="-ping", value="يقيس سرعة استجابة البوت.", inline=False)
    embed.add_field(name="-clear [العدد]", value="حذف الرسائل دفعة واحدة.", inline=False)
    embed.add_field(name="-server", value="معلومات السيرفر.", inline=False)
    embed.add_field(name="-avatar [@user]", value="عرض الأفاتار.", inline=False)
    embed.add_field(name="-rules", value="نشر القوانين.", inline=False)
    embed.add_field(name="-suggest [الاقتراح]", value="إرسال اقتراح مع أزرار للتصويت.", inline=False)
    embed.add_field(name="-announce [العنوان] [النص]", value="إرسال إعلان رسمي مرتب.", inline=False)
    embed.add_field(name="-log", value="لوحة تحكم السجلات.", inline=False)
    embed.add_field(name="-c", value="عرض قائمة أوامر الاقتصاد والألعاب والمتجر بالتفصيل.", inline=False)
    embed.add_field(name="-tell", value="عرض نظام المصارحات (Tellonym) والشرح والترجمة.", inline=False)
    
    embed.add_field(name="الردود الذكية (بدون بريفكس)", value="• منو قطوتي -> مياو\n• منو بطتي -> بط بط\n• شاطر / شاطرة -> كلزق", inline=False)
    embed.add_field(name="الحماية والسجلات", value="منع السبام، مكافحة الرايد، وسجلات الرومات والرتب والرسائل.", inline=False)
    
    await ctx.send(embed=embed)

# ==================== قائمة أوامر الاقتصاد (-c) ====================
@bot.command(name="c")
async def economy_help(ctx):
    embed = discord.Embed(title="💰 قائمة أوامر الاقتصاد والألعاب والمتجر", description="إليك كافة الأوامر المالية وطريقة استخدامها:", color=discord.Color.gold())
    
    embed.add_field(name="الأوامر الأساسية", value="• `-balance` أو `-bal [@user]` : يعرض رصيدك أو رصيد شخص آخر.\n• `-daily` : يمنحك مكافأة يومية (500 Coins كل 24 ساعة).\n• `-work` : تذهب للعمل وتكسب مبلغاً عشوائياً (100-300 Coins) كل ساعة.\n• `-beg` : تشحذ للحصول على مبلغ بسيط (10-100 Coins) كل 15 دقيقة.\n• `-pay [@user] [المبلغ]` : تحويل عملات لشخص آخر في السيرفر.\n• `-leaderboard` أو `-lb` : يعرض قائمة أغنى 10 أشخاص في السيرفر.", inline=False)
    embed.add_field(name="ألعاب الحظ والمراهنات", value="• `-slots [المبلغ]` : ماكينة الحظ لمضاعفة أرباحك.\n• `-dice [المبلغ]` : رمي النرد والمنافسة ضد البوت.\n• `-coinflip [المبلغ] [صورة/كتابة]` : مراهنة العملة المعدنية.", inline=False)
    embed.add_field(name="المتجر والحقيبة", value="• `-shop` : يعرض قائمة المنتجات المتاحة للشراء.\n• `-buy [اسم المنتج]` : لشراء منتج من المتجر.\n• `-inventory` : يعرض حقيبتك وما تحويه من عناصر.\n• `-use [اسم المنتج]` : لاستخدام عنصر قمت بشرائه.", inline=False)
    embed.add_field(name="أوامر الإدارة المالية (تتطلب مسؤول)", value="• `-addcoins [@user] [المبلغ]`\n• `-removecoins [@user] [المبلغ]`\n• `-setcoins [@user] [المبلغ]`\n• `-resetcoins [@user]`", inline=False)
    
    await ctx.send(embed=embed)

# ==================== نظام التليون (-tell) ====================
@bot.command(name="tell")
async def tell_help(ctx):
    embed = discord.Embed(
        title="💌 نظام المصارحات (Tellonym System)",
        description="إليك كافة الأوامر والشرح والترجمة الخاصة بنظام المصارحات السرية في السيرفر:",
        color=discord.Color.purple()
    )
    
    embed.add_field(
        name="📌 ما هو نظام Tellonym؟",
        value="نظام يسمح للأعضاء بإرسال رسائل ومصارحات سرية أو علنية لبعضهم البعض بشكل ممتع ومنظم.",
        inline=False
    )
    
    embed.add_field(
        name="⚙️ الأوامر وطريقة الاستخدام",
        value=(
            "• `-tell` : يعرض لك هذه القائمة الشاملة والشرح.\n"
            "• `-sendtell [@العضو] [الرسالة]` : لإرسال مصارحة (تيل) سرية وموجهة للعضو.\n"
            "• `-setchannel` : تعيين روم مخصص لاستقبال المصارحات (خاص بالإدارة)."
        ),
        inline=False
    )
    
    embed.add_field(
        name="🌐 الترجمة والمصطلحات (Translation)",
        value=(
            "• **Tellonym / Tell** = مصارحة أو رسالة سرية.\n"
            "• **Anonymous** = مجهول (بدون ذكر اسم المرسل).\n"
            "• **Inbox** = صندوق الوارد الخاص بالمصارحات."
        ),
        inline=False
    )
    
    embed.set_footer(text=f"طلب بواسطة: {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="sendtell")
async def send_tell(ctx, member: discord.Member, *, message_text: str):
    await ctx.message.delete()
    if member.id == ctx.author.id:
        await ctx.send("❌ لا يمكنك إرسال مصارحة لنفسك!", delete_after=5)
        return

    embed = discord.Embed(
        title="💌 وصلت لك مصارحة جديدة (New Tell)",
        description=f"```{message_text}```",
        color=discord.Color.magenta()
    )
    embed.set_footer(text="تم إرسال هذه المصارحة عبر نظام Tellonym المجهول.")

    try:
        await member.send(embed=embed)
        await ctx.send(f"✅ {ctx.author.mention}، تم إرسال مصارحتك إلى {member.mention} بنجاح!", delete_after=5)
    except:
        tell_chan = get_tell_channel(ctx.guild)
        if tell_chan:
            embed.add_field(name="إلى العضو", value=member.mention, inline=False)
            await tell_chan.send(embed=embed)
            await ctx.send(f"✅ {ctx.author.mention}، تم نشر المصارحة في روم المصارحات لأن خاص العضو مغلق.", delete_after=5)
        else:
            await ctx.send("❌ تعذر إرسال المصارحة (خاص العضو مغلق ولا يوجد روم مصارحات عام).", delete_after=5)

# ==================== الأوامر الاقتصادية ====================
@bot.command(aliases=["bal"])
async def balance(ctx, member: discord.Member = None):
    target = member or ctx.author
    bal = get_balance(target.id)
    await ctx.send(f"👤 {target.mention} رصيدك الحالي: `{bal} Coins` 🪙")

@bot.command()
async def daily(ctx):
    user_id = ctx.author.id
    now = time.time()
    if user_id in cooldowns["daily"] and now - cooldowns["daily"][user_id] < 86400:
        remaining = int(86400 - (now - cooldowns["daily"][user_id]))
        hours = remaining // 3600
        await ctx.send(f"⏳ لقد استلمت مكافأتك اليومية مسبقاً. انتظر `{hours}` ساعة.")
        return
    
    cooldowns["daily"][user_id] = now
    update_balance(user_id, 500)
    await ctx.send(f"🎁 {ctx.author.mention} استلمت مكافأتك اليومية: `500 Coins` 🪙!")

@bot.command()
async def work(ctx):
    user_id = ctx.author.id
    now = time.time()
    if user_id in cooldowns["work"] and now - cooldowns["work"][user_id] < 3600:
        remaining = int(3600 - (now - cooldowns["work"][user_id]))
        minutes = remaining // 60
        await ctx.send(f"⏳ أنت متعب وتحتاج للراحة. انتظر `{minutes}` دقيقة للعمل مجدداً.")
        return
    
    cooldowns["work"][user_id] = now
    earned = random.randint(100, 300)
    update_balance(user_id, earned)
    await ctx.send(f"💼 {ctx.author.mention} ذهبت للعمل وكسبت `+{earned} Coins` 🪙!")

@bot.command()
async def beg(ctx):
    user_id = ctx.author.id
    now = time.time()
    if user_id in cooldowns["beg"] and now - cooldowns["beg"][user_id] < 900:
        await ctx.send(f"⏳ الناس ملوا منك! انتظر قليلاً قبل الشحاذة مرة أخرى.")
        return
    
    cooldowns["beg"][user_id] = now
    if random.choice([True, False]):
        earned = random.randint(10, 100)
        update_balance(user_id, earned)
        await ctx.send(f"🤲 أعطاك شخص طيب `+{earned} Coins` 🪙.")
    else:
        await ctx.send(f"🙄 رفض الجميع إعطاءك أي شيء هذه المرة.")

@bot.command()
async def pay(ctx, member: discord.Member, amount: int):
    if amount <= 0:
        await ctx.send("❌ الرجاء تحديد مبلغ صحيح.")
        return
    
    sender_id = ctx.author.id
    if get_balance(sender_id) < amount:
        await ctx.send("❌ ليس لديك رصيد كافٍ لتتمكن من التحويل.")
        return
    
    if member.id == sender_id:
        await ctx.send("❌ لا يمكنك التحويل لنفسك.")
        return
    
    update_balance(sender_id, -amount)
    update_balance(member.id, amount)
    await ctx.send(f"✅ تم تحويل `{amount} Coins` بنجاح إلى {member.mention} 💸.")

@bot.command(aliases=["lb"])
async def leaderboard(ctx):
    if not economy_db:
        await ctx.send("📊 لا يوجد أي بيانات اقتصادية حتى الآن.")
        return
    
    sorted_users = sorted(economy_db.items(), key=lambda x: x[1], reverse=True)[:10]
    embed = discord.Embed(title="🏆 قائمة أغنى 10 أشخاص في السيرفر", color=discord.Color.gold())
    
    desc = ""
    for idx, (uid, bal) in enumerate(sorted_users, 1):
        user = ctx.guild.get_member(uid)
        name = user.display_name if user else f"مستخدم {uid}"
        desc += f"**{idx}.** {name} ⟷ `{bal} Coins` 🪙\n"
    
    embed.description = desc
    await ctx.send(embed=embed)

# ==================== ألعاب الحظ ====================
@bot.command()
async def slots(ctx, amount: int):
    if amount <= 0 or get_balance(ctx.author.id) < amount:
        await ctx.send("❌ رصيدك لا يكفي أو المبلغ غير صحيح.")
        return
    
    symbols = ["🍒", "🍋", "🍊", "🔔", "💎"]
    result = [random.choice(symbols) for _ in range(3)]
    
    update_balance(ctx.author.id, -amount)
    if result[0] == result[1] == result[2]:
        won = amount * 5
        update_balance(ctx.author.id, won)
        await ctx.send(f"🎰 | {' '.join(result)} | ربحت مضاعف! مبروك كسبت `+{won} Coins` 🎉")
    else:
        await ctx.send(f"🎰 | {' '.join(result)} | خسرت محاولتك `- {amount} Coins` 😢")

@bot.command()
async def dice(ctx, amount: int):
    if amount <= 0 or get_balance(ctx.author.id) < amount:
        await ctx.send("❌ رصيدك لا يكفي أو المبلغ غير صحيح.")
        return
    
    user_roll = random.randint(1, 6)
    bot_roll = random.randint(1, 6)
    
    update_balance(ctx.author.id, -amount)
    if user_roll > bot_roll:
        update_balance(ctx.author.id, amount * 2)
        await ctx.send(f"🎲 رميت النرد وجاء (`{user_roll}` مقابل بوت `{bot_roll}`). لقد فزت بـ `+{amount} Coins`! 🎉")
    elif user_roll < bot_roll:
        await ctx.send(f"🎲 رميت النرد وجاء (`{user_roll}` مقابل بوت `{bot_roll}`). لقد خسرت `- {amount} Coins` 😢")
    else:
        update_balance(ctx.author.id, amount)
        await ctx.send(f"🎲 تعادل! (`{user_roll}` مقابل `{bot_roll}`). استرددت أموالك.")

@bot.command()
async def coinflip(ctx, amount: int, choice: str):
    choice = choice.lower()
    if choice not in ["صورة", "كتابة"]:
        await ctx.send("❌ يرجى اختيار إما (صورة) أو (كتابة).")
        return
    
    if amount <= 0 or get_balance(ctx.author.id) < amount:
        await ctx.send("❌ رصيدك لا يكفي أو المبلغ غير صحيح.")
        return
    
    result = random.choice(["صورة", "كتابة"])
    update_balance(ctx.author.id, -amount)
    
    if choice == result:
        update_balance(ctx.author.id, amount * 2)
        await ctx.send(f"🪙 جاءت العملة على ({result})! فزت بـ `+{amount} Coins` 🎉")
    else:
        await ctx.send(f"🪙 جاءت العملة على ({result})! خسرت `- {amount} Coins` 😢")

# ==================== المتجر والحقيبة ====================
@bot.command()
async def shop(ctx):
    embed = discord.Embed(title="🛍️ متجر السيرفر", description="استخدم أمر `-buy [الاسم]` للشراء:", color=discord.Color.teal())
    for key, item in shop_items.items():
        embed.add_field(name=f"{item['name']} (`{key}`)", value=f"{item['desc']}\n💰 السعر: `{item['price']} Coins`", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def buy(ctx, item_key: str):
    item_key = item_key.lower()
    if item_key not in shop_items:
        await ctx.send("❌ هذا المنتج غير موجود في المتجر. اكتب `-shop` لعرض المنتجات.")
        return
    
    item = shop_items[item_key]
    user_id = ctx.author.id
    if get_balance(user_id) < item["price"]:
        await ctx.send("❌ لا تملك رصيداً كافياً لشراء هذا المنتج.")
        return
    
    update_balance(user_id, -item["price"])
    inventory_db[user_id].append(item_key)
    await ctx.send(f"✅ تم شراء `{item['name']}` بنجاح! تم إضافته إلى حقيبتك `-inventory`.")

@bot.command()
async def inventory(ctx):
    user_id = ctx.author.id
    items = inventory_db[user_id]
    if not items:
        await ctx.send("🎒 حقيبتك فارغة حالياً.")
        return
    
    item_counts = {item: items.count(item) for item in set(items)}
    desc = ""
    for k, count in item_counts.items():
        desc += f"• {shop_items[k]['name']} (العدد: `{count}`) [استخدم `-use {k}`]\n"
    
    embed = discord.Embed(title=f"🎒 حقيبة {ctx.author.name}", description=desc, color=discord.Color.blurple())
    await ctx.send(embed=embed)

@bot.command()
async def use(ctx, item_key: str):
    item_key = item_key.lower()
    user_id = ctx.author.id
    if item_key not in inventory_db[user_id]:
        await ctx.send("❌ هذا المنتج غير موجود في حقيبتك.")
        return
    
    inventory_db[user_id].remove(item_key)
    await ctx.send(f"✨ لقد استخدمت العنصر `{shop_items[item_key]['name']}` بنجاح! تواصل مع الإدارة لتفعيل جائزتك.")

# ==================== أوامر الإدارة المالية ====================
@bot.command()
@commands.has_permissions(administrator=True)
async def addcoins(ctx, member: discord.Member, amount: int):
    update_balance(member.id, amount)
    await ctx.send(f"✅ تمت إضافة `{amount} Coins` إلى رصيد {member.mention}.")

@bot.command()
@commands.has_permissions(administrator=True)
async def removecoins(ctx, member: discord.Member, amount: int):
    update_balance(member.id, -amount)
    await ctx.send(f"✅ تم خصم `{amount} Coins` من رصيد {member.mention}.")

@bot.command()
@commands.has_permissions(administrator=True)
async def setcoins(ctx, member: discord.Member, amount: int):
    economy_db[member.id] = max(0, amount)
    await ctx.send(f"✅ تم تعيين رصيد {member.mention} ليصبح `{amount} Coins`.")

@bot.command()
@commands.has_permissions(administrator=True)
async def resetcoins(ctx, member: discord.Member):
    economy_db[member.id] = 0
    await ctx.send(f"✅ تم تصفير رصيد {member.mention}.")

@bot.command(name="setchannel")
@commands.has_permissions(administrator=True)
async def set_channel(ctx):
    await ctx.send(f"✅ {ctx.author.mention}، سيقوم البوت تلقائياً بالاعتماد على أي روم يحتوي على اسم (tell أو صارحني أو مصارحات أو سجلات) لتلقي الرسائل.")

# ==================== لوحة السجلات (-log) ====================
@bot.command(name="log")
@commands.has_permissions(administrator=True)
async def log_status(ctx):
    log_chan = get_log_channel(ctx.guild)
    channel_name = log_chan.mention if log_chan else "⚠️ لم يتم العثور على روم سجلات"
    
    embed = discord.Embed(title="📊 لوحة تحكم وحالة السجلات (Logs)", color=discord.Color.dark_blue())
    embed.add_field(name="📌 روم السجلات الحالي", value=channel_name, inline=False)
    embed.add_field(name="🛡️ الحماية المفعلة", value="• منع السبام التلقائي\n• مكافحة الرايد\n• رصد حذف وتعديل الرسائل\n• رصد إنشاء وحذف الرومات والرتب", inline=False)
    embed.set_footer(text=f"بواسطة: {ctx.author.display_name}")
    await ctx.send(embed=embed)

# ==================== الأحداث والأجهزة في الخلفية ====================
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

    # منع السبام
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

    for channel in guild.text_channels:
        if "welcome" in channel.name.lower() or "ترحيب" in channel.name or "الرئيسية" in channel.name:
            await channel.send(f"حياك الله {member.mention}، نورت السيرفر!")
            break

@bot.event
async def on_message_delete(message):
    if message.author.bot or not message.guild:
        return
    log_chan = get_log_channel(message.guild)
    if log_chan:
        embed = discord.Embed(title="🗑️ حذف رسالة", color=discord.Color.red())
        embed.add_field(name="الكاتب", value=message.author.mention, inline=True)
        embed.add_field(name="الروم", value=message.channel.mention, inline=True)
        embed.add_field(name="المحتوى", value=message.content or "محتوى غير نصي", inline=False)
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
        await log_chan.send(f"📁 **تم إنشاء روم جديد:** `{channel.name}`")

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
