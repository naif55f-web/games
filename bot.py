import discord
from discord.ext import commands
import random
import asyncio
from keep_alive import keep_alive

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
        value="• روليت\n• عكسي\n• سكات\n• وصل\n• بومب\n• نرد\n• خمن\n• حجره\n• اكس",
        inline=False
    )
    embed.add_field(
        name="🎯 الألعاب الفردية",
        value="• حساب\n• عواصم\n• كت\n• فكك\n• اعلام\n• جمع\n• عكس",
        inline=False
    )
    embed.add_field(
        name="⚙️ أوامر أخرى",
        value="• توب\n• نقاطي\n• تحويل\n• ايقاف",
        inline=False
    )
    await ctx.send(embed=embed)

# ==================== الألعاب الفردية ====================

@bot.command(name='حساب')
async def game_math(ctx):
    num1, num2 = random.randint(1, 50), random.randint(1, 50)
    op = random.choice(['+', '-', '*'])
    answer = eval(f"{num1} {op} {num2}")
    
    await ctx.send(f"🧮 أسرع! كم الناتج: **{num1} {op} {num2}**؟ (معاك 15 ثانية)")
    
    def check(m):
        return m.channel == ctx.channel and m.content.isdigit()

    try:
        msg = await bot.wait_for('message', timeout=15.0, check=check)
        if int(msg.content) == answer:
            add_points(msg.author.id, 10)
            await ctx.send(f"🎉 كفو {msg.author.mention}! إجابتك صحيحة وفزت بـ **10 نقاط**.")
        else:
            await ctx.send(f"❌ إجابة خاطئة! الناتج الصحيح كان: {answer}")
    except asyncio.TimeoutError:
        await ctx.send(f"⏰ انتهى الوقت! الناتج كان: {answer}")

@bot.command(name='عواصم')
async def game_capitals(ctx):
    capitals = {"السعودية": "الرياض", "مصر": "القاهرة", "الكويت": "الكويت", "الإمارات": "أبوظبي", "قطر": "الدوحة", "الأردن": "عمان"}
    country, capital = random.choice(list(capitals.items()))
    
    await ctx.send(f"🌍 ما هي عاصمة **{country}**؟ (معاك 15 ثانية)")
    
    def check(m):
        return m.channel == ctx.channel and not m.author.bot

    try:
        msg = await bot.wait_for('message', timeout=15.0, check=check)
        if msg.content.strip() == capital:
            add_points(msg.author.id, 10)
            await ctx.send(f"🎉 صح عليك يا {msg.author.mention}! العاصمة هي **{capital}** (خذ 10 نقاط).")
        else:
            await ctx.send(f"❌ خطأ! العاصمة الصحيحة هي: **{capital}**")
    except asyncio.TimeoutError:
        await ctx.send(f"⏰ خلص الوقت! العاصمة هي: **{capital}**")

@bot.command(name='فكك')
async def game_unpack(ctx):
    words = {"برمجة": "ب ر م ج ة", "حاسوب": "ح ا س و ب", "ديسكورد": "د ي س ك و ر د"}
    word, unpacked = random.choice(list(words.items()))
    
    await ctx.send(f"✂️ فكك الكلمة التالية: **{word}**\n(اكتبها مفصولة بمسافات، معاك 20 ثانية)")
    
    def check(m):
        return m.channel == ctx.channel and not m.author.bot

    try:
        msg = await bot.wait_for('message', timeout=20.0, check=check)
        if msg.content.replace(" ", "") == word:
            add_points(msg.author.id, 15)
            await ctx.send(f"🎉 ممتاز يا {msg.author.mention}! فككتها صح وفزت بـ **15 نقطة**.")
        else:
            await ctx.send(f"❌ خطأ!")
    except asyncio.TimeoutError:
        await ctx.send(f"⏰ انتهى الوقت!")

@bot.command(name='كت')
async def game_cut(ctx):
    questions = [
        "لو خيروك بين: العيش بدون إنترنت أو بدون أصدقاء؟",
        "لو خيروك بين: السفر للماضي أو للمستقبل؟",
        "لو خيروك بين: القدرة على الطيران أو الاختفاء؟"
    ]
    embed = discord.Embed(title="❓ سؤال كت", description=random.choice(questions), color=discord.Color.purple())
    await ctx.send(embed=embed)

@bot.command(name='عكس')
async def game_reverse_word(ctx):
    normal_words = ["تفاحة", "قلم", "كمبيوتر", "شارع", "جامعة"]
    w = random.choice(normal_words)
    reversed_w = w[::-1]
    
    await ctx.send(f"🔄 اعكس هذه الكلمة: **{reversed_w}** (وش أصلها؟ معاك 15 ثانية)")
    
    def check(m):
        return m.channel == ctx.channel and not m.author.bot

    try:
        msg = await bot.wait_for('message', timeout=15.0, check=check)
        if msg.content.strip() == w:
            add_points(msg.author.id, 10)
            await ctx.send(f"🎉 كفو {msg.author.mention}! الأصل هو **{w}**.")
        else:
            await ctx.send(f"❌ خطأ! الأصل كان: **{w}**")
    except asyncio.TimeoutError:
        await ctx.send(f"⏰ انتهى الوقت!")

@bot.command(name='نرد')
async def game_dice(ctx):
    r1, r2 = random.randint(1, 6), random.randint(1, 6)
    await ctx.send(f"🎲 {ctx.author.mention} رمى النرد وطلع له: **{r1}** و **{r2}** (المجموع: {r1+r2})")

@bot.command(name='حجره')
async def game_rps(ctx, choice: str = None):
    choices = ["حجر", "ورقة", "مقص"]
    if choice not in choices:
        await ctx.send("⚠️ اختر هكذا: `-حجره حجر` أو `-حجره ورقة` أو `-حجره مقص`")
        return
    bot_choice = random.choice(choices)
    
    if choice == bot_choice:
        result = "تعادل! 🤝"
    elif (choice == "حجر" and bot_choice == "مقص") or (choice == "ورقة" and bot_choice == "حجر") or (choice == "مقص" and bot_choice == "ورقة"):
        result = "فزت علي! 🎉 (+10 نقاط)"
        add_points(ctx.author.id, 10)
    else:
        result = "أنا فزت عليك! 🤖 هاردلك."
        
    await ctx.send(f"اختيارك: **{choice}** | اختياري: **{bot_choice}**\nالنتيجة: **{result}**")

@bot.command(name='بومب')
async def game_bomb(ctx):
    await ctx.send(f"💣 تم زرع القنبلة بواسطة {ctx.author.mention}! اكتب `قطع` بسرعة خلال 8 ثانية عشان تنقذ السيرفر!")
    def check(m):
        return m.content == "قطع" and not m.author.bot
    try:
        msg = await bot.wait_for('message', timeout=8.0, check=check)
        await ctx.send(f"💥 كفو {msg.author.mention}! قدرت تقطع السلك الصحيح وتفكك القنبلة بسلام (+20 نقطة)!")
        add_points(msg.author.id, 20)
    except asyncio.TimeoutError:
        await ctx.send("💥 **بوووووووم!** انقضى الوقت وانفجرت القنبلة بالجميع! 💀")

@bot.command(name='نقاطي')
async def my_points(ctx):
    pts = user_points.get(ctx.author.id, 0)
    await ctx.send(f"📊 {ctx.author.mention}, رصيدك الحالي هو: **{pts}** نقطة.")

@bot.command(name='توب')
async def top_board(ctx):
    if not user_points:
        await ctx.send("🏆 مافي أي نقاط مسجلة لحد الحين، ابدأوا اللعب!")
        return
    sorted_users = sorted(user_points.items(), key=lambda x: x[1], reverse=True)[:5]
    desc = ""
    for i, (uid, pts) in enumerate(sorted_users, 1):
        user = ctx.guild.get_member(uid)
        name = user.name if user else "لاعب مغادر"
        desc += f"{i}. **{name}** - `{pts}` نقطة\n"
    embed = discord.Embed(title="🏆 لوحة الشرف (التوب)", description=desc, color=discord.Color.gold())
    await ctx.send(embed=embed)

@bot.command(name='تحويل')
async def transfer_points(ctx, member: discord.Member, amount: int):
    sender_pts = user_points.get(ctx.author.id, 0)
    if amount <= 0 or sender_pts < amount:
        await ctx.send("❌ عذراً، تأكد من رصيدك أو القيمة المدخلة.")
        return
    user_points[ctx.author.id] -= amount
    add_points(member.id, amount)
    await ctx.send(f"✅ تم تحويل **{amount}** نقطة بنجاح إلى {member.mention}!")

@bot.command(name='ايقاف')
async def stop_bot_game(ctx):
    await ctx.send(f"🛑 تم إيقاف الألعاب النشطة بواسطة {ctx.author.mention}.")

# تشغيل السيرفر الوهمي ثم البوت
keep_alive()
import os
bot.run(os.environ['TOKEN'])
