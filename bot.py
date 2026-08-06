import discord
from discord.ext import commands
import random
import asyncio
from keep_alive import keep_alive
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='-', intents=intents)

user_points = {}

def add_points(user_id, points):
    user_points[user_id] = user_points.get(user_id, 0) + points

@bot.event
async def on_ready():
    print(f'البوت شغال وجاهز باسم: {bot.user}')

# ==================== قائمة الألعاب ====================
@bot.command(name='العاب')
async def games_menu(ctx):
    embed = discord.Embed(title="Game Commands", color=discord.Color.blue())
    embed.add_field(
        name="🎮 الألعاب الجماعية",
        value="• روليت\n• روليتز\n• عكسي\n• سكات\n• وصل\n• لغم\n• بومب\n• كراسي\n• نرد\n• هايد\n• خمن\n• مافيا\n• حجره\n• اكس\n• ازار",
        inline=False
    )
    embed.add_field(
        name="🎯 الألعاب الفردية",
        value="• حساب\n• عواصم\n• اشبك\n• كت\n• اسرع\n• كمل\n• فكك\n• اعلام\n• التالي\n• جمع\n• عكس\n• مفرد",
        inline=False
    )
    embed.add_field(
        name="⚙️ أوامر أخرى",
        value="• تصويت\n• توب\n• نقاطي\n• تحويل\n• ايقاف",
        inline=False
    )
    await ctx.send(embed=embed)

# ==================== الألعاب الجماعية ====================

@bot.command(name='روليت')
async def game_roulette(ctx):
    survived = random.choice([True, True, True, False]) # نسبة الخسارة 25%
    if survived:
        add_points(ctx.author.id, 15)
        await ctx.send(f"🔫 {ctx.author.mention} سحب الزناد... نجا ولله الحمد! (خذ 15 نقطة سرفايفل).")
    else:
        await ctx.send(f"💥 بـووووم! {ctx.author.mention} طاحت عليه الرصاصة وطلع برأس منفوخ! 💀")

@bot.command(name='روليتز')
async def game_rouletz(ctx):
    await ctx.send(f"🎡 {ctx.author.mention} شغل روليت الحظ السريع! تدور العجلة... وربح **20 نقطة** عشوائية!")
    add_points(ctx.author.id, 20)

@bot.command(name='عكسي')
async def game_aksi(ctx):
    words = {"مرحبا": "احبرم", "توت": "توت", "جميل": "ليمج"}
    await ctx.send(f"🔄 **لعبة عكسي الجماعية:** أسرع واحد يكتب كلمة `العكس` معكوسة يربح!")

@bot.command(name='سكات')
async def game_skat(ctx):
    await ctx.send(f"🤫 **لعبة سكات!** أطول واحد يلتزم الصمت ولا يكتب شي لمدة 15 ثانية يفوز بالنقاط! ابدأوا الصمت... 🤐")
    await asyncio.sleep(15)
    await ctx.send(f"⏱️ انتهى وقت الصمت! الفائزون هم من التزموا الهدوء.")

@bot.command(name='وصل')
async def game_wasal(ctx):
    await ctx.send(f"🔗 **لعبة وصل:** اربط الكلمة التالية بكلمة مناسبة: **(بحر)** - معاك 10 ثواني لأول إجابة!")

@bot.command(name='لغم')
async def game_mine(ctx):
    safe_box = random.randint(1, 3)
    await ctx.send(f"💣 زرعنا لغم في أحد الأبواب (1 أو 2 أو 3). اختر رقماً لا يكون فيه اللغم! (اكتب الرقم)")
    def check(m):
        return m.channel == ctx.channel and m.content.isdigit() and not m.author.bot
    try:
        msg = await bot.wait_for('message', timeout=10.0, check=check)
        choice = int(msg.content)
        if choice == safe_box:
            add_points(msg.author.id, 25)
            await ctx.send(f"🎉 كفو {msg.author.mention} اخترت الباب السليم وتجنبت اللغم! (+25 نقطة)")
        else:
            await ctx.send(f"💥 بووووم! دست على اللغم يا {msg.author.mention}! اللغم كان في باب رقم {safe_box}.")
    except asyncio.TimeoutError:
        await ctx.send("⏰ انتهى الوقت ولم تختار أي باب!")

@bot.command(name='بومب')
async def game_bomb(ctx):
    await ctx.send(f"💣 تم زرع القنبلة بواسطة {ctx.author.mention}! اكتب `قطع` بسرعة خلال 8 ثوانٍ!")
    def check(m):
        return m.content == "قطع" and not m.author.bot
    try:
        msg = await bot.wait_for('message', timeout=8.0, check=check)
        add_points(msg.author.id, 20)
        await ctx.send(f"💥 كفو {msg.author.mention} قطعت السلك الصح وفككت القنبلة! (+20 نقطة)")
    except asyncio.TimeoutError:
        await ctx.send("💥 انقضى الوقت وانفجرت القنبلة بالجميع! 💀")

@bot.command(name='كراسي')
async def game_chairs(ctx):
    await ctx.send(f"🪑 أضيئت الكراسي الموسيقية! أسرع شخص يكتب كلمة `جلس` يربح الكرسي! (معاك 5 ثواني)")
    def check(m):
        return m.content == "جلس" and not m.author.bot
    try:
        msg = await bot.wait_for('message', timeout=5.0, check=check)
        add_points(msg.author.id, 15)
        await ctx.send(f"🏆 الف مبروك يا {msg.author.mention} لحقت على الكرسي وفزت بـ 15 نقطة!")
    except asyncio.TimeoutError:
        , await ctx.send("⏰ انتهى الوقت، ما لحقوا على الكراسي!")

@bot.command(name='نرد')
async def game_dice(ctx):
    r1, r2 = random.randint(1, 6), random.randint(1, 6)
    await ctx.send(f"🎲 رمي النرد لـ {ctx.author.mention}: **{r1}** و **{r2}** (المجموع: {r1+r2})")

@bot.command(name='هايد')
async def game_hide(ctx):
    await ctx.send(f"👤 بدأ التخفي (هايد)! البوت يتخفي في مكان ما، ابحث عنه أو خمن المكان.")

@bot.command(name='خمن')
async def game_guess(ctx):
    target = random.randint(1, 10)
    await ctx.send(f"🔮 خمن الرقم السرّي من 1 إلى 10! معك 15 ثانية واكتب الرقم بالشات.")
    def check(m):
        return m.channel == ctx.channel and m.content.isdigit() and not m.author.bot
    try:
        msg = await bot.wait_for('message', timeout=15.0, check=check)
        if int(msg.content) == target:
            add_points(msg.author.id, 20)
            await ctx.send(f"🎯 الله عليك يا {msg.author.mention} خمنت الرقم الصحيح ({target})! (+20 نقطة)")
        else:
            await ctx.send(f"❌ خطأ! الرقم الصحيح كان: {target}")
    except asyncio.TimeoutError:
        await ctx.send(f"⏰ خلص الوقت! الرقم كان: {target}")

@bot.command(name='مافيا')
async def game_mafia(ctx):
    await ctx.send(f"🕵️ لعبة مافيا بدأت! من هو المافيا الخفي بينكم؟ (لعبة جماعية تفاعلية)")

@bot.command(name='حجره')
async def game_rps(ctx, choice: str = None):
    choices = ["حجر", "ورقة", "مقص"]
    if choice not in choices:
        await ctx.send("⚠️ استخدم الطريقة: `-حجره حجر` أو `-حجره ورقة` أو `-حجره مقص`")
        return
    bot_choice = random.choice(choices)
    if choice == bot_choice:
        res = "تعادل 🤝"
    elif (choice == "حجر" and bot_choice == "مقص") or (choice == "ورقة" and bot_choice == "حجر") or (choice == "مقص" and bot_choice == "ورقة"):
        res = "فزت علي! 🎉 (+10 نقاط)"
        add_points(ctx.author.id, 10)
    else:
        res = "أنا فزت عليك! 🤖"
    await ctx.send(f"اختيارك: {choice} | اختياري: {bot_choice}\nالنتيجة: **{res}**")

@bot.command(name='اكس')
async def game_xo(ctx):
    await ctx.send(f"❌⭕ لعبة اكس أو (Tic Tac Toe) جاهزة للبدء بين لاعبين!")

@bot.command(name='ازار')
async def game_azar(ctx):
    await ctx.send(f"⚡ بدأت لعبة أزار السريعة والتحديات الفورية!")


# ==================== الألعاب الفردية ====================

@bot.command(name='حساب')
async def game_math(ctx):
    n1, n2 = random.randint(1, 50), random.randint(1, 50)
    op = random.choice(['+', '-', '*'])
    ans = eval(f"{n1} {op} {n2}")
    await ctx.send(f"🧮 كم الناتج: **{n1} {op} {n2}**؟ (معاك 15 ثانية)")
    def check(m):
        return m.channel == ctx.channel and m.content.isdigit()
    try:
        msg = await bot.wait_for('message', timeout=15.0, check=check)
        if int(msg.content) == ans:
            add_points(msg.author.id, 10)
            await ctx.send(f"🎉 كفو {msg.author.mention}! صح (+10 نقاط)")
        else:
            await ctx.send(f"❌ خطأ! الناتج كان: {ans}")
    except asyncio.TimeoutError:
        await ctx.send(f"⏰ انتهى الوقت! الناتج كان: {ans}")

@bot.command(name='عواصم')
async def game_capitals(ctx):
    caps = {"السعودية": "الرياض", "مصر": "القاهرة", "الكويت": "الكويت", "الإمارات": "أبوظبي"}
    country, capital = random.choice(list(caps.items()))
    await ctx.send(f"🌍 ما هي عاصمة **{country}**؟")
    def check(m):
        return m.channel == ctx.channel and not m.author.bot
    try:
        msg = await bot.wait_for('message', timeout=15.0, check=check)
        if msg.content.strip() == capital:
            add_points(msg.author.id, 10)
            await ctx.send(f"🎉 صح يا {msg.author.mention}! العاصمة **{capital}**")
        else:
            await ctx.send(f"❌ خطأ العاصمة: {capital}")
    except asyncio.TimeoutError:
        await ctx.send(f"⏰ انتهى الوقت! العاصمة: {capital}")

@bot.command(name='اشبك')
async def game_ashbak(ctx):
    await ctx.send(f"🔗 اشبك الحروف أو الكلمات لتكوين جملة مفيدة صحيحة!")

@bot.command(name='كت')
async def game_cut(ctx):
    qs = ["لو خيروك: بدون إنترنت أو بدون أصدقاء؟", "لو خيروك: تسافر للماضي أو للمستقبل؟"]
    embed = discord.Embed(title="❓ سؤال كت", description=random.choice(qs), color=discord.Color.purple())
    await ctx.send(embed=embed)

@bot.command(name='اسرع')
async def game_asra3(ctx):
    word = random.choice(["تفاحة", "سرعة", "صاروخ", "برمجة"])
    await ctx.send(f"⚡ أسرع واحد يكتب هذه الكلمة: **{word}**")
    def check(m):
        return m.content.strip() == word and not m.author.bot
    try:
        msg = await bot.wait_for('message', timeout=10.0, check=check)
        add_points(msg.author.id, 15)
        await ctx.send(f"🏆 كفو {msg.author.mention} أسرع واحد! (+15 نقطة)")
    except asyncio.TimeoutError:
        await ctx.send(f"⏰ خلص الوقت! محد كتب الكلمة بسرعة.")

@bot.command(name='كمل')
async def game_kamel(ctx):
    await ctx.send(f"📝 كمل المثل أو الآية أو الأغنية التالية: (من طلب العلا ...)")

@bot.command(name='فكك')
async def game_unpack(ctx):
    words = {"برمجة": "ب ر م ج ة", "حاسوب": "ح ا س و ب"}
    word, unpacked = random.choice(list(words.items()))
    await ctx.send(f"✂️ فكك الكلمة: **{word}**")
    def check(m):
        return m.channel == ctx.channel and not m.author.bot
    try:
        msg = await bot.wait_for('message', timeout=15.0, check=check)
        if msg.content.replace(" ", "") == word:
            add_points(msg.author.id, 15)
            await ctx.send(f"🎉 ممتاز يا {msg.author.mention} فككتها صح!")
        else:
            await ctx.send(f"❌ خطأ!")
    except asyncio.TimeoutError:
        await ctx.send(f"⏰ انتهى الوقت!")

@bot.command(name='اعلام')
async def game_flags(ctx):
    await ctx.send(f"🚩 ما هو علم الدولة التالية؟ 🇸🇦 (أو اكتب اسم الدولة)")

@bot.command(name='التالي')
async def game_next(ctx):
    await ctx.send(f"⏭️ تم تخطي السؤال والانتقال للسؤال التالي بنجاح!")

@bot.command(name='جمع')
async def game_gam3(ctx):
    await ctx.send(f"➕ ا جمع الحروف التالية لتكون كلمة: (ك ت ا ب)")

@bot.command(name='عكس')
async def game_reverse_word(ctx):
    normal_words = ["تفاحة", "قلم", "كمبيوتر"]
    w = random.choice(normal_words)
    rev = w[::-1]
    await ctx.send(f"🔄 اعكس هذه الكلمة الأصلية: **{rev}**")
    def check(m):
        return m.channel == ctx.channel and not m.author.bot
    try:
        msg = await bot.wait_for('message', timeout=15.0, check=check)
        if msg.content.strip() == w:
            add_points(msg.author.id, 10)
            await ctx.send(f"🎉 صح يا {msg.author.mention}! الأصل هو {w}")
        else:
            await ctx.send(f"❌ خطأ! الأصل كان: {w}")
    except asyncio.TimeoutError:
        await ctx.send(f"⏰ انتهى الوقت!")

@bot.command(name='مفرد')
async def game_mufrad(ctx):
    await ctx.send(f"👤 أوجد مفرد الكلمة التالية: (أقلام)")


# ==================== الأوامر العامة والأخرى ====================

@bot.command(name='تصويت')
async def game_vote(ctx, *, topic: str = "تصويت جديد"):
    embed = discord.Embed(title="📊 صندوق التصويت", description=topic, color=discord.Color.green())
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")

@bot.command(name='توب')
async def top_board(ctx, game_name: str = None):
    if not user_points:
        await ctx.send("🏆 مافي نقاط مسجلة لحد الآن!")
        return
    sorted_users = sorted(user_points.items(), key=lambda x: x[1], reverse=True)[:5]
    desc = ""
    for i, (uid, pts) in enumerate(sorted_users, 1):
        user = ctx.guild.get_member(uid)
        name = user.name if user else "لاعب"
        desc += f"{i}. **{name}** - `{pts}` نقطة\n"
    
    title = f"🏆 لوحة الشرف ({game_name})" if game_name else "🏆 لوحة الشرف العامة"
    embed = discord.Embed(title=title, description=desc, color=discord.Color.gold())
    await ctx.send(embed=embed)

@bot.command(name='نقاطي')
async def my_points(ctx):
    pts = user_points.get(ctx.author.id, 0)
    await ctx.send(f"📊 {ctx.author.mention}, رصيدك: **{pts}** نقطة.")

@bot.command(name='تحويل')
async def transfer_points(ctx, member: discord.Member, amount: int):
    sender_pts = user_points.get(ctx.author.id, 0)
    if amount <= 0 or sender_pts < amount:
        await ctx.send("❌ عذراً، لا توجد نقاط كافية أو القيمة غير صالحة.")
        return
    user_points[ctx.author.id] -= amount
    add_points(member.id, amount)
    await ctx.send(f"✅ تم تحويل **{amount}** نقطة إلى {member.mention}!")

@bot.command(name='ايقاف')
async def stop_bot_game(ctx):
    await ctx.send(f"🛑 تم إيقاف الألعاب بواسطة {ctx.author.mention}.")

# تشغيل البوت
keep_alive()
bot.run(os.environ['TOKEN'])
