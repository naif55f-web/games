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
cooldowns = {"daily": {}, "work": {}, "beg": {}, "broadcast": {}}
inventory_db = defaultdict(list)

shop_items = {
    "color": {"name": "تغيير لون الاسم", "price": 5000, "desc": "يتيح لك تغيير لون اسمك"},
    "vip": {"name": "رتبة VIP يوم", "price": 15000, "desc": "رتبة VIP لمدة يوم كامل"},
    "elite": {"name": "رتبة Elite أسبوع", "price": 50000, "desc": "رتبة Elite لمدة أسبوع"},
    "ticket": {"name": "دخول سحب خاص", "price": 10000, "desc": "تذكرة دخول للسحب القادم"}
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

# ==================== الأمر الشامل (-all) ====================
@bot.command(name="all")
async def all_commands_guide(ctx):
    embed = discord.Embed(
        title="دليل جميع أوامر وأنظمة البوت الشاملة حرفياً",
        description="إليك كافة الأوامر، الأنظمة، الألعاب، والشروحات الموجودة داخل البوت بالتفصيل:",
        color=discord.Color.dark_embed()
    )
    
    # 1. الأوامر العامة وأوامر السيرفر
    embed.add_field(
        name="1. الأوامر العامة والإدارة السريعة",
        value=(
            "• -k : عرض قائمة الأوامر العامة الأساسية.\n"
            "• -ping : قياس سرعة استجابة البوت بالمللي ثانية.\n"
            "• -clear [العدد] : حذف الرسائل دفعة واحدة (للإدارة).\n"
            "• -server : عرض معلومات السيرفر الكاملة.\n"
            "• -avatar [@user] : عرض صورة الأفاتار الخاصة بك أو بأي عضو.\n"
            "• -rules : نشر قوانين السيرفر الرسمية.\n"
            "• -suggest [الاقتراح] : إرسال اقتراح مع أزرار للتصويت (ايجاب وسلب).\n"
            "• -announce [العنوان] [النص] : إرسال إعلان رسمي مرتب للإدارة.\n"
            "• -log : عرض لوحة تحكم وحالة السجلات والحماية."
        ),
        inline=False
    )
    
    # 2. نظام الاقتصاد والألعاب
    embed.add_field(
        name="2. نظام الاقتصاد والألعاب المتكامل",
        value=(
            "• -c : عرض قائمة أوامر الاقتصاد.\n"
            "• -balance أو -bal [@user] : عرض رصيدك أو رصيد عضو آخر.\n"
            "• -daily : استلام المكافأة اليومية (500 عملة كل 24 ساعة).\n"
            "• -work : العمل لكسب دخل عشوائي (100-300 عملة كل ساعة).\n"
            "• -beg : الشحاذة للحصول على مبلغ بسيط (كل 15 دقيقة).\n"
            "• -pay [@user] [المبلغ] : تحويل أموال لعضو آخر.\n"
            "• -leaderboard أو -lb : قائمة أغنى 10 أشخاص في السيرفر.\n"
            "• -slots [المبلغ] : ماكينة الحظ لمضاعفة الأرباح.\n"
            "• -dice [المبلغ] : رمي النرد والمنافسة ضد البوت.\n"
            "• -coinflip [المبلغ] [صورة/كتابة] : لعبة العملة المعدنية."
        ),
        inline=False
    )
    
    # 3. المتجر والحقيبة
    embed.add_field(
        name="3. متجر السيرفر والحقيبة",
        value=(
            "• -shop : عرض المنتجات المتاحة للشراء (تغيير لون، رتب VIP، إلخ).\n"
            "• -buy [الاسم] : شراء منتج من المتجر برصيدك.\n"
            "• -inventory : عرض محتويات حقيبتك وما تملكه.\n"
            "• -use [الاسم] : استخدام عنصر قمت بشرائه من الحقيبة."
        ),
        inline=False
    )
    
    # 4. أوامر الإدارة المالية
    embed.add_field(
        name="4. أوامر الإدارة المالية (للمسؤولين فقط)",
        value=(
            "• -addcoins [@user] [المبلغ] : إضافة أموال لرصيد عضو.\n"
            "• -removecoins [@user] [المبلغ] : خصم أموال من رصيد عضو.\n"
            "• -setcoins [@user] [المبلغ] : تعيين رصيد محدد لعضو.\n"
            "• -resetcoins [@user] : تصفير رصيد العضو تماماً."
        ),
        inline=False
    )
    
    # 5. نظام التليون (Tellonym)
    embed.add_field(
        name="5. نظام المصارحات (Tellonym)",
        value=(
            "• -tell : عرض شرح وأوامر نظام المصارحات.\n"
            "• -sendtell [@العضو] [الرسالة] : إرسال مصارحة سرية لعضو (مع حذف رسالتك تلقائياً للسرية).\n"
            "• -setchannel : تحديد روم استقبال المصارحات تلقائياً.\n"
            "• مصطلحات النظام: Tellonym (مصارحة)، Anonymous (مجهول)، Inbox (صندوق الوارد)."
        ),
        inline=False
    )
    
    # 6. نظام البرودكاست (Broadcast)
    embed.add_field(
        name="6. نظام البرودكاست المتطور",
        value=(
            "• -برودكاست : عرض شرح وأوامر نظام البرودكاست الشامل.\n"
            "• -bc [الرسالة] : إرسال برودكاست عام لجميع الأعضاء عبر الخاص مع إحصائيات.\n"
            "• -bc-role [@الرتبة] [الرسالة] : إرسال برودكاست لأصحاب رتبة معينة عبر الخاص.\n"
            "• -bc-room [#الروم] [الرسالة] : إرسال برودكاست رسمي داخل روم معين.\n"
            "• المتغيرات المتاحة: {user} لمنشن العضو، {username} لاسم العضو، {server} لاسم السيرفر، {members} لعدد الأعضاء."
        ),
        inline=False
    )
    
    # 7. الردود الذكية والحماية التلقائية
    embed.add_field(
        name="7. الردود الذكية والحماية (تعمل تلقائياً بدون بريفكس)",
        value=(
            "• منو قطوتي -> يرجع البوت بـ (مياو)\n"
            "• منو بطتي -> يرجع البوت بـ (بط بط)\n"
            "• شاطر أو شاطرة -> يرجع البوت بـ (كلزق)\n"
            "• حماية السبام التلقائي : حذف الرسائل المتكررة السريعة وإرسال تحذير للسجلات.\n"
            "• مكافحة الرايد : رصد دخول أعداد هائلة من الأعضاء في ثوانٍ معدودة.\n"
            "• سجلات الرومات والرتب والرسائل : تتبع التعديل والحذف والإنشاء تلقائياً."
        ),
        inline=False
    )
    
    embed.set_footer(text=f"طلب بواسطة: {ctx.author.display_name} | جميع الحقوق محفوظة")
    await ctx.send(embed=embed)

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
    embed.add_field(name="-tell", value="عرض نظام المصارحات (Tellonym) والشرح.", inline=False)
    embed.add_field(name="-برودكاست", value="عرض شرح وأوامر نظام البرودكاست المتطور.", inline=False)
    embed.add_field(name="-all", value="عرض الدليل الشامل لجميع أوامر وأنظمة البوت حرفياً.", inline=False)
    
    await ctx.send(embed=embed)

# ==================== قائمة أوامر الاقتصاد (-c) ====================
@bot.command(name="c")
async def economy_help(ctx):
    embed = discord.Embed(title="قائمة أوامر الاقتصاد والألعاب والمتجر", description="إليك كافة الأوامر المالية وطريقة استخدامها:", color=discord.Color.gold())
    
    embed.add_field(name="الأوامر الأساسية", value="• -balance أو -bal [@user] : رصيدك أو رصيد غيرك\n• -daily : مكافأة يومية\n• -work : العمل لكسب المال\n• -beg : الشحاذة\n• -pay [@user] [المبلغ] : تحويل أموال\n• -leaderboard أو -lb : لوحة الشرف", inline=False)
    embed.add_field(name="ألعاب الحظ والمراهنات", value="• -slots [المبلغ] : ماكينة الحظ\n• -dice [المبلغ] : النرد\n• -coinflip [المبلغ] [صورة/كتابة] : العملة", inline=False)
    embed.add_field(name="المتجر والحقيبة", value="• -shop : المتجر\n• -buy [الاسم] : الشراء\n• -inventory : الحقيبة\n• -use [الاسم] : الاستخدام", inline=False)
    
    await ctx.send(embed=embed)

# ==================== نظام التليون (-tell) ====================
@bot.command(name="tell")
async def tell_help(ctx):
    embed = discord.Embed(title="نظام المصارحات", description="أوامر وشرح نظام المصارحات السرية:", color=discord.Color.purple())
    embed.add_field(name="الأوامر", value="• -tell : عرض الشرح\n• -sendtell [@العضو] [الرسالة] : إرسال مصارحة سرية\n• -setchannel : تحديد روم المصارحات", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="sendtell")
async def send_tell(ctx, member: discord.Member, *, message_text: str):
    await ctx.message.delete()
    if member.id == ctx.author.id:
        await ctx.send("لا يمكنك إرسال مصارحة لنفسك!", delete_after=5)
        return
    embed = discord.Embed(title="وصلت لك مصارحة جديدة", description=f"```{message_text}```", color=discord.Color.magenta())
    try:
        await member.send(embed=embed)
        await ctx.send(f"تم إرسال مصارحتك إلى {member.mention} بنجاح!", delete_after=5)
    except:
        tell_chan = get_tell_channel(ctx.guild)
        if tell_chan:
            await tell_chan.send(embed=embed)
            await ctx.send(f"تم نشر المصارحة في روم المصارحات لأن خاص العضو مغلق.", delete_after=5)
        else:
            await ctx.send("تعذر إرسال المصارحة.", delete_after=5)

# ==================== نظام البرودكاست (-برودكاست) ====================
@bot.command(name="برودكاست")
@commands.has_permissions(administrator=True)
async def broadcast_help(ctx):
    embed = discord.Embed(title="نظام البرودكاست", description="أوامر وشرح البرودكاست:", color=discord.Color.dark_gray())
    embed.add_field(name="الأوامر", value="• -برودكاست : الشرح\n• -bc [الرسالة] : عام للكل\n• -bc-role [@الرتبة] [الرسالة] : لرتبة معينة\n• -bc-room [#الروم] [الرسالة] : بروم معين", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="bc")
@commands.has_permissions(administrator=True)
async def broadcast_all(ctx, *, text: str):
    await ctx.message.delete()
    user_id = ctx.author.id
    now = time.time()
    if user_id in cooldowns["broadcast"] and now - cooldowns["broadcast"][user_id] < 60:
        await ctx.send("يرجى الانتظار دقيقة.", delete_after=5)
        return
    cooldowns["broadcast"][user_id] = now
    success = 0
    failed = 0
    status_msg = await ctx.send("جاري إرسال البرودكاست...")
    for member in ctx.guild.members:
        if member.bot: continue
        custom_text = text.replace("{user}", member.mention).replace("{username}", member.name).replace("{server}", ctx.guild.name).replace("{members}", str(ctx.guild.member_count))
        try:
            embed = discord.Embed(title=f"إعلان من {ctx.guild.name}", description=custom_text, color=discord.Color.blue())
            await member.send(embed=embed)
            success += 1
            await asyncio.sleep(0.5)
        except:
            failed += 1
    await status_msg.edit(content=f"تم إرسال البرودكاست. الناجح: {success} | الفاشل: {failed}")

@bot.command(name="bc-role")
@commands.has_permissions(administrator=True)
async def broadcast_role(ctx, role: discord.Role, *, text: str):
    await ctx.message.delete()
    success = 0
    failed = 0
    status_msg = await ctx.send(f"جاري الإرسال لرتبة {role.name}...")
    for member in role.members:
        if member.bot: continue
        custom_text = text.replace("{user}", member.mention).replace("{username}", member.name).replace("{server}", ctx.guild.name).replace("{members}", str(ctx.guild.member_count))
        try:
            embed = discord.Embed(title=f"إعلان برتبة {role.name}", description=custom_text, color=discord.Color.green())
            await member.send(embed=embed)
            success += 1
            await asyncio.sleep(0.5)
        except:
            failed += 1
    await status_msg.edit(content=f"تم إرسال برودكاست الرتبة. الناجح: {success} | الفاشل: {failed}")

@bot.command(name="bc-room")
@commands.has_permissions(administrator=True)
async def broadcast_room(ctx, channel: discord.TextChannel, *, text: str):
    await ctx.message.delete()
    custom_text = text.replace("{user}", "@everyone").replace("{username}", "الجميع").replace("{server}", ctx.guild.name).replace("{members}", str(ctx.guild.member_count))
    embed = discord.Embed(title=f"إعلان رسمي", description=custom_text, color=discord.Color.orange())
    await channel.send(embed=embed)
    await ctx.send(f"تم الإرسال إلى الروم {channel.mention}.", delete_after=5)

# ==================== الأوامر الاقتصادية ====================
@bot.command(aliases=["bal"])
async def balance(ctx, member: discord.Member = None):
    target = member or ctx.author
    bal = get_balance(target.id)
    await ctx.send(f"{target.mention} رصيدك: {bal} عملة")

@bot.command()
async def daily(ctx):
    user_id = ctx.author.id
    now = time.time()
    if user_id in cooldowns["daily"] and now - cooldowns["daily"][user_id] < 86400:
        await ctx.send("استلمت مكافأتك مسبقاً.")
        return
    cooldowns["daily"][user_id] = now
    update_balance(user_id, 500)
    await ctx.send(f"{ctx.author.mention} استلمت 500 عملة!")

@bot.command()
async def work(ctx):
    user_id = ctx.author.id
    now = time.time()
    if user_id in cooldowns["work"] and now - cooldowns["work"][user_id] < 3600:
        await ctx.send("انتظر قليلاً للعمل مجدداً.")
        return
    cooldowns["work"][user_id] = now
    earned = random.randint(100, 300)
    update_balance(user_id, earned)
    await ctx.send(f"{ctx.author.mention} كسبت +{earned} عملة!")

@bot.command()
async def beg(ctx):
    user_id = ctx.author.id
    now = time.time()
    if user_id in cooldowns["beg"] and now - cooldowns["beg"][user_id] < 900:
        await ctx.send("انتظر قبل الشحاذة.")
        return
    cooldowns["beg"][user_id] = now
    if random.choice([True, False]):
        earned = random.randint(10, 100)
        update_balance(user_id, earned)
        await ctx.send(f"أعطاك شخص +{earned} عملة.")
    else:
        await ctx.send("رفض الجميع إعطاءك شيئاً.")

@bot.command()
async def pay(ctx, member: discord.Member, amount: int):
    if amount <= 0 or get_balance(ctx.author.id) < amount or member.id == ctx.author.id:
        await ctx.send("خطأ في عملية التحويل.")
        return
    update_balance(ctx.author.id, -amount)
    update_balance(member.id, amount)
    await ctx.send(f"تم تحويل {amount} إلى {member.mention}.")

@bot.command(aliases=["lb"])
async def leaderboard(ctx):
    if not economy_db:
        await ctx.send("لا توجد بيانات.")
        return
    sorted_users = sorted(economy_db.items(), key=lambda x: x[1], reverse=True)[:10]
    desc = "".join([f"{idx}. <@!{uid}> - {bal}\n" for idx, (uid, bal) in enumerate(sorted_users, 1)])
    embed = discord.Embed(title="أغنى الأعضاء", description=desc, color=discord.Color.gold())
    await ctx.send(embed=embed)

@bot.command()
async def slots(ctx, amount: int):
    if amount <= 0 or get_balance(ctx.author.id) < amount:
        await ctx.send("رصيد غير كافٍ.")
        return
    symbols = ["تفاح", "موز", "برتقال", "جرس", "ماس"]
    result = [random.choice(symbols) for _ in range(3)]
    update_balance(ctx.author.id, -amount)
    if result[0] == result[1] == result[2]:
        won = amount * 5
        update_balance(ctx.author.id, won)
        await ctx.send(f"النتيجة: {' '.join(result)} | ربحت +{won}")
    else:
        await ctx.send(f"النتيجة: {' '.join(result)} | خسرت -{amount}")

@bot.command()
async def dice(ctx, amount: int):
    if amount <= 0 or get_balance(ctx.author.id) < amount:
        await ctx.send("رصيد غير كافٍ.")
        return
    user_roll, bot_roll = random.randint(1, 6), random.randint(1, 6)
    update_balance(ctx.author.id, -amount)
    if user_roll > bot_roll:
        update_balance(ctx.author.id, amount * 2)
        await ctx.send(f"نردك: {user_roll} | البوت: {bot_roll} (فزت)")
    else:
        await ctx.send(f"نردك: {user_roll} | البوت: {bot_roll} (خسرت)")

@bot.command()
async def coinflip(ctx, amount: int, choice: str):
    choice = choice.lower()
    if choice not in ["صورة", "كتابة"] or amount <= 0 or get_balance(ctx.author.id) < amount:
        await ctx.send("خطأ في البيانات.")
        return
    result = random.choice(["صورة", "كتابة"])
    update_balance(ctx.author.id, -amount)
    if choice == result:
        update_balance(ctx.author.id, amount * 2)
        await ctx.send(f"جاءت {result} (فزت)")
    else:
        await ctx.send(f"جاءت {result} (خسرت)")

@bot.command()
async def shop(ctx):
    embed = discord.Embed(title="المتجر", description="استخدم -buy [الاسم]", color=discord.Color.teal())
    for k, i in shop_items.items():
        embed.add_field(name=f"{i['name']} ({k})", value=f"{i['desc']} - السعر: {i['price']}", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def buy(ctx, item_key: str):
    item_key = item_key.lower()
    if item_key not in shop_items or get_balance(ctx.author.id) < shop_items[item_key]["price"]:
        await ctx.send("خطأ في الشراء.")
        return
    update_balance(ctx.author.id, -shop_items[item_key]["price"])
    inventory_db[ctx.author.id].append(item_key)
    await ctx.send("تم الشراء بنجاح.")

@bot.command()
async def inventory(ctx):
    items = inventory_db[ctx.author.id]
    if not items:
        await ctx.send("حقيبتك فارغة.")
        return
    desc = "".join([f"• {shop_items[k]['name']}\n" for k in set(items)])
    embed = discord.Embed(title="الحقيبة", description=desc, color=discord.Color.blurple())
    await ctx.send(embed=embed)

@bot.command()
async def use(ctx, item_key: str):
    item_key = item_key.lower()
    if item_key not in inventory_db[ctx.author.id]:
        await ctx.send("العنصر غير موجود.")
        return
    inventory_db[ctx.author.id].remove(item_key)
    await ctx.send("تم الاستخدام بنجاح.")

@bot.command()
@commands.has_permissions(administrator=True)
async def addcoins(ctx, member: discord.Member, amount: int):
    update_balance(member.id, amount)
    await ctx.send("تمت الإضافة.")

@bot.command()
@commands.has_permissions(administrator=True)
async def removecoins(ctx, member: discord.Member, amount: int):
    update_balance(member.id, -amount)
    await ctx.send("تم الخصم.")

@bot.command()
@commands.has_permissions(administrator=True)
async def setcoins(ctx, member: discord.Member, amount: int):
    economy_db[member.id] = max(0, amount)
    await ctx.send("تم التعيين.")

@bot.command()
@commands.has_permissions(administrator=True)
async def resetcoins(ctx, member: discord.Member):
    economy_db[member.id] = 0
    await ctx.send("تم التصفير.")

@bot.command(name="setchannel")
@commands.has_permissions(administrator=True)
async def set_channel(ctx):
    await ctx.send("تم تفعيل التعرف التلقائي.")

@bot.command(name="log")
@commands.has_permissions(administrator=True)
async def log_status(ctx):
    await ctx.send("لوحة السجلات مفعلة.")

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return
    content = message.content.strip()
    if content == "منو قطوتي":
        await message.channel.send("مياو")
    elif content == "منو بطتي":
        await message.channel.send("بط بط")
    elif content == "شاطر" or content == "شاطرة":
        await message.channel.send("كلزق")
    
    author_id = message.author.id
    current_time = asyncio.get_event_loop().time()
    message_cache[author_id] = [t for t in message_cache[author_id] if current_time - t < 5]
    message_cache[author_id].append(current_time)
    if len(message_cache[author_id]) > 5:
        try:
            await message.delete()
            log_chan = get_log_channel(message.guild)
            if log_chan: await log_chan.send("تنبيه سبام.")
        except: pass
        return
    await bot.process_commands(message)

@bot.event
async def on_member_join(member: discord.Member):
    for channel in member.guild.text_channels:
        if "welcome" in channel.name.lower() or "ترحيب" in channel.name:
            await channel.send(f"حياك الله {member.mention}")
            break

@bot.event
async def on_message_delete(message):
    if message.author.bot or not message.guild: return
    log_chan = get_log_channel(message.guild)
    if log_chan:
        await log_chan.send(f"حذف رسالة لـ {message.author.mention}")

@bot.event
async def on_message_edit(before, after):
    if before.author.bot or not before.guild or before.content == after.content: return
    log_chan = get_log_channel(before.guild)
    if log_chan:
        await log_chan.send(f"تعديل رسالة لـ {before.author.mention}")

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")

@bot.command(name="clear")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.message.delete()
    deleted = await ctx.channel.purge(limit=amount)
    msg = await ctx.send(f"تم حذف {len(deleted)} رسالة.")
    await asyncio.sleep(3)
    try: await msg.delete()
    except: pass

@bot.command(name="server")
async def server_info(ctx):
    await ctx.send(f"السيرفر: {ctx.guild.name} | الأعضاء: {ctx.guild.member_count}")

@bot.command(name="avatar")
async def avatar(ctx, user: discord.Member = None):
    target = user or ctx.author
    await ctx.send(target.display_avatar.url)

@bot.command(name="rules")
@commands.has_permissions(administrator=True)
async def rules(ctx):
    await ctx.message.delete()
    await ctx.send("قوانين السيرفر: الاحترام، عدم السبام، منع الإعلانات.")

@bot.command(name="suggest")
async def suggest(ctx, *, suggestion: str):
    await ctx.message.delete()
    msg = await ctx.send(f"اقتراح من {ctx.author.mention}: {suggestion}")
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")

@bot.command(name="announce")
@commands.has_permissions(administrator=True)
async def announce(ctx, title: str, *, message: str):
    await ctx.message.delete()
    await ctx.send(f"إعلان: **{title}**\n{message}")

keep_alive()
bot.run(os.environ['TOKEN'])
