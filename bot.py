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

# ==================== قائمة الألعاب الكاملة ====================
@bot.command(name='العاب')
async def games_menu(ctx):
    embed = discord.Embed(title="🎮 Game Commands - قائمة الألعاب", color=discord.Color.blue())
    embed.add_field(
        name="🎮 الألعاب الجماعية",
        value="• مافيا\n• روليت\n• روليتز\n• عكسي\n• سكات\n• وصل\n• لغم\n• بومب\n• كراسي\n• نرد\n• هايد\n• خمن\n• حجره\n• اكس\n• ازار",
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

# ==================== نظام أزرار ولعبة المافيا بالشكل المطلوب تماماً ====================

class JoinGameView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30)
        self.participants = []

    @discord.ui.button(label="دخول 👤+", style=discord.ButtonStyle.secondary, custom_id="join_btn")
    async def join_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user not in self.participants:
            if len(self.participants) >= 24:
                await interaction.response.send_message("⚠️ عذراً، اكتمل العدد الأقصى (24 لاعب)!", ephemeral=True)
                return
            self.participants.append(interaction.user)
            await interaction.response.send_message("✅ تم انضمامك بنجاح للعبة المافيا!", ephemeral=True)
            await self.update_embed(interaction, 30)
        else:
            await interaction.response.send_message("⚠️ أنت منضم مسبقاً!", ephemeral=True)

    @discord.ui.button(label="خروج 👤-", style=discord.ButtonStyle.secondary, custom_id="leave_btn")
    async def leave_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.participants:
            self.participants.remove(interaction.user)
            await interaction.response.send_message("❌ تم انسحابك من اللعبة.", ephemeral=True)
            await self.update_embed(interaction, 30)
        else:
            await interaction.response.send_message("⚠️ أنت لست منضماً أصلاً!", ephemeral=True)

    async def update_embed(self, interaction: discord.Interaction, remaining_time):
        count = len(self.participants)
        
        embed = discord.Embed(
            title=f"اللاعبين: {count}/24",
            description=f"in {remaining_time} seconds",
            color=discord.Color.dark_theme()
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/1534223835031801956/1534961993503604736/B5320697-566B-45A7-9972-6BCF90A9E25B.png?ex=6a760841&is=6a74b6c1&hm=6fa313de223f874fe63edadc5c7855934bf9da5f32a08fd02baba9ec35a6fcf2&")
        
        try:
            await interaction.message.edit(embed=embed, view=self)
        except:
            pass

class TargetSelectView(discord.ui.View):
    def __init__(self, players):
        super().__init__(timeout=25)
        self.selected_target = None
        for p in players:
            self.add_item(TargetButton(p))

class TargetButton(discord.ui.Button):
    def __init__(self, player):
        super().__init__(label=player.display_name, style=discord.ButtonStyle.primary)
        self.target_player = player

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_target = self.target_player
        await interaction.response.send_message(f"✅ تم اختيار: **{self.target_player.display_name}**", ephemeral=True)
        self.view.stop()

@bot.command(name='مافيا')
async def cmd_mafia(ctx):
    view = JoinGameView()
    embed = discord.Embed(
        title="اللاعبين: 0/24",
        description="in 30 seconds",
        color=discord.Color.dark_theme()
    )
    embed.set_image(url="https://cdn.discordapp.com/attachments/1534223835031801956/1534961993503604736/B5320697-566B-45A7-9972-6BCF90A9E25B.png?ex=6a760841&is=6a74b6c1&hm=6fa313de223f874fe63edadc5c7855934bf9da5f32a08fd02baba9ec35a6fcf2&")
    
    msg = await ctx.send(embed=embed, view=view)
    
    # عد تنازلي لمدة 30 ثانية وتحديث الوقت في الرسالة كل ثانية
    for remaining in range(29, -1, -1):
        await asyncio.sleep(1)
        count = len(view.participants)
        
        embed.title = f"اللاعبين: {count}/24"
        embed.description = f"in {remaining} seconds"
        try:
            await msg.edit(embed=embed, view=view)
        except:
            break

    participants = view.participants

    # تعطيل الأزرار بعد انتهاء الوقت
    for child in view.children:
        child.disabled = True
    try:
        await msg.edit(view=view)
    except:
        pass

    # التحقق من أن العدد 5 لاعبين على الأقل
    if len(participants) < 5:
        await ctx.send("**تم إيقاف اللعبة لعدم وجود `5` لاعبين على الأقل - ⛔.**")
        return

    # توزيع الأدوار
    random.shuffle(participants)
    mafia_player = participants[0]
    doctor_player = participants[1]
    citizens = participants[2:]

    roles = {mafia_player: 'مافيا', doctor_player: 'طبيب'}
    for c in citizens:
        roles[c] = 'مواطن'

    await ctx.send(f"🔒 **تم توزيع الأدوار سراً بالخاص!** عدد اللاعبين المشاركين: {len(participants)}.")

    # إرسال الأدوار بالخاص
    try:
        await mafia_player.send("🔪 **أنت القاتل (المافيا)!** اختبئ جيداً واقضِ على الجميع.")
        await doctor_player.send("💉 **أنت الطبيب!** مهمتك حماية شخص كل ليلة من القتل.")
        for c in citizens:
            await c.send("👥 **أنت مواطن بريء!** حاول معرفة القاتل والتصويت عليه.")
    except:
        pass

    # 1. بداية الليل ودور الطبيب أولاً
    await ctx.send("🌙 **حل الليل... تنام المدينة.**")
    await ctx.send("💉 **دور الطبيب الآن!** (تصل رسالة خاصة للطبيب لاختيار من يحميه...)")

    doctor_target = None
    try:
        view_doctor = TargetSelectView(participants)
        await doctor_player.send("💉 **اختر الشخص الذي تريد حمايته هذه الليلة:**", view=view_doctor)
        await view_doctor.wait()
        doctor_target = view_doctor.selected_target
    except:
        pass

    # 2. دور المافيا ثانياً
    await ctx.send("🔪 **دور المافيا الآن!** (تصل رسالة خاصة للمافيا لاختيار الضحية...)")

    mafia_target = None
    try:
        view_mafia = TargetSelectView(participants)
        await mafia_player.send("🔪 **اختر الشخص الذي تريد قتله هذه الليلة:**", view=view_mafia)
        await view_mafia.wait()
        mafia_target = view_mafia.selected_target
    except:
        pass

    await asyncio.sleep(2)
    await ctx.send("☀️ **أشرقت شمس اليوم الجديد!** حان وقت الكشف عن الأحداث...")

    # 3. النتيجة بحسب شروطك الدقيقة
    if mafia_target and mafia_target == doctor_target:
        await ctx.send(f"🛡️ **تمت حماية {mafia_target.display_name} من قبل الطبيب من القاتل!** ولم يمت أحد هذه الليلة. 🎉")
    elif mafia_target:
        await ctx.send(f"💀 للأسف، نجحت المافيا وتم اغتيال اللاعب **{mafia_target.display_name}**!")
        if mafia_target in participants:
            participants.remove(mafia_target)
    else:
        await ctx.send("🌅 لم تحدث أي حالة قتل هذه الليلة!")

    # 4. مرحلة التصويت الجماعي
    await ctx.send("🗳️ **بدأ التصويت!** من تعتقدون أنه المافيا؟ (اكتب اسم الشخص أو سوِّ له منشن خلال 15 ثانية)")

    votes = {}
    def vote_check(m):
        return m.channel == ctx.channel and not m.author.bot

    vote_end = asyncio.get_event_loop().time() + 15
    while asyncio.get_event_loop().time() < vote_end:
        try:
            v_msg = await bot.wait_for('message', timeout=2.0, check=vote_check)
            voter = v_msg.author
            target = v_msg.mentions[0] if v_msg.mentions else None
            if target and target in participants:
                votes[voter] = target
        except asyncio.TimeoutError:
            pass

    if votes:
        from collections import Counter
        tally = Counter(votes.values())
        most_voted, count = tally.most_common(1)[0]
        await ctx.send(f"⚖️ تم طرد **{most_voted.display_name}** بأغلبية الأصوات!")
        
        if roles.get(most_voted) == 'مافيا':
            await ctx.send(f"🎉 **مبروك للمواطنين والطبيب!** لقد كشفتم المافيا (**{most_voted.display_name}**) وفزتم باللعبة!")
        else:
            await ctx.send(f"❌ **{most_voted.display_name}** كان مواطناً بريئاً! المافيا فازت باللعبة 😈")
    else:
        await ctx.send("⏰ انتهى الوقت دون إبعاد أحد ونجت المافيا!")

# ==================== الألعاب الجماعية ====================

@bot.command(name='روليت')
async def cmd_roulette(ctx):
    survived = random.choice([True, True, True, False])
    if survived:
        add_points(ctx.author.id, 15)
        await ctx.send(f"🔫 {ctx.author.mention} سحب الزناد... نجا ولله الحمد! (+15 نقطة).")
    else:
        await ctx.send(f"💥 بـووووم! {ctx.author.mention} طاحت عليه الرصاصة! 💀")

@bot.command(name='روليتز')
async def cmd_rouletz(ctx):
    add_points(ctx.author.id, 20)
    await ctx.send(f"🎡 {ctx.author.mention} شغل روليت الحظ وربح **20 نقطة**!")

@bot.command(name='عكسي')
async def cmd_aksi(ctx):
    await ctx.send(f"🔄 **لعبة عكسي:** أسرع واحد يعكس الكلمة التالية (مدرسة) يكتبها بالشات!")

@bot.command(name='سكات')
async def cmd_skat(ctx):
    await ctx.send(f"🤫 **لعبة سكات!** أطول شخص يلتزم الصمت لمدة 10 ثواني يفوز! 🤐")
    await asyncio.sleep(10)
    await ctx.send(f"⏱️ انتهى وقت السكات!")

@bot.command(name='وصل')
async def cmd_wasal(ctx):
    await ctx.send(f"🔗 **لعبة وصل:** اربط الكلمة التالية (سماء) بكلمة مناسبة!")

@bot.command(name='لغم')
async def cmd_mine(ctx):
    safe = random.randint(1, 3)
    await ctx.send(f"💣 زرعنا لغم في أحد الأبواب (1 أو 2 أو 3). اختر رقماً لا يكون فيه اللغم!")
    def check(m):
        return m.channel == ctx.channel and m.content.isdigit() and not m.author.bot
    try:
        msg = await bot.wait_for('message', timeout=10.0, check=check)
        if int(msg.content) == safe:
            add_points(msg.author.id, 25)
            await ctx.send(f"🎉 كفو {msg.author.mention} تجنبت اللغم وفزت بـ 25 نقطة!")
        else:
            await ctx.send(f"💥 بووووم! دست على اللغم يا {msg.author.mention}.")
    except asyncio.TimeoutError:
        await ctx.send("⏰ انتهى الوقت!")

@bot.command(name='بومب')
async def cmd_bomb(ctx):
    await ctx.send(f"💣 تم زرع القنبلة بواسطة {ctx.author.mention}! اكتب `قطع` بسرعة خلال 8 ثواني!")
    def check(m):
        return m.content == "قطع" and not m.author.bot
    try:
        msg = await bot.wait_for('message', timeout=8.0, check=check)
        add_points(msg.author.id, 20)
        await ctx.send(f"💥 كفو {msg.author.mention} فككت القنبلة بسلام! (+20 نقطة)")
    except asyncio.TimeoutError:
        await ctx.send("💥 بوووم! انفجرت القنبلة بالجميع! 💀")

@bot.command(name='كراسي')
async def cmd_chairs(ctx):
    await ctx.send(f"🪑 أسرع شخص يكتب كلمة `جلس` يربح الكرسي! (معاك 5 ثواني)")
    def check(m):
        return m.content == "جلس" and not m.author.bot
    try:
        msg = await bot.wait_for('message', timeout=5.0, check=check)
        add_points(msg.author.id, 15)
        await ctx.send(f"🏆 الف مبروك يا {msg.author.mention} لحقت على الكرسي!")
    except asyncio.TimeoutError:
        await ctx.send("⏰ انتهى الوقت!")

@bot.command(name='نرد')
async def cmd_dice(ctx):
    r1, r2 = random.randint(1, 6), random.randint(1, 6)
    await ctx.send(f"🎲 رمي النرد لـ {ctx.author.mention}: **{r1}** و **{r2}** (المجموع: {r1+r2})")

@bot.command(name='هايد')
async def cmd_hide(ctx):
    await ctx.send(f"👤 بدأ التخفي (هايد)! ابحث عن المكان السري.")

@bot.command(name='خمن')
async def cmd_guess(ctx):
    target = random.randint(1, 10)
    await ctx.send(f"🔮 خمن الرقم السري من 1 إلى 10! (معاك 15 ثانية)")
    def check(m):
        return m.channel == ctx.channel and m.content.isdigit() and not m.author.bot
    try:
        msg = await bot.wait_for('message', timeout=15.0, check=check)
        if int(msg.content) == target:
            add_points(msg.author.id, 20)
            await ctx.send(f"🎯 كفو {msg.author.mention} خمنت الرقم الصحيح ({target})!")
        else:
            await ctx.send(f"❌ خطأ! الرقم كان: {target}")
    except asyncio.TimeoutError:
        await ctx.send(f"⏰ انتهى الوقت! الرقم كان: {target}")

@bot.command(name='حجره')
async def cmd_rps(ctx, choice: str = None):
    choices = ["حجر", "ورقة", "مقص"]
    if choice not in choices:
        await ctx.send("⚠️ اكتب هكذا: `-حجره حجر` أو `-حجره ورقة` أو `-حجره مقص`")
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
async def cmd_xo(ctx):
    await ctx.send(f"❌⭕ لعبة اكس أو جاهزة للبدء!")

@bot.command(name='ازار')
async def cmd_azar(ctx):
    await ctx.send(f"⚡ بدأت لعبة أزار والتحديات السريعة!")

# ==================== الألعاب الفردية ====================

@bot.command(name='حساب')
async def cmd_math(ctx):
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
            await ctx.send(f"🎉 كفو {msg.author.mention}! إجابة صحيحة (+10 نقاط)")
        else:
            await ctx.send(f"❌ خطأ! الناتج كان: {ans}")
    except asyncio.TimeoutError:
        await ctx.send(f"⏰ انتهى الوقت! الناتج كان: {ans}")

@bot.command(name='عواصم')
async def cmd_capitals(ctx):
    caps = {"السعودية": "الرياض", "مصر": "القاهرة", "الكويت": "الكويت", "الإمارات": "أبوظبي"}
    country, capital = random.choice(list(caps.items()))
    await ctx.send(f"🌍 ما هي عاصمة **{country}**؟")
    def check(m):
        return m.channel == ctx.channel and not m.author.bot
    try:
        msg = await bot.wait_for('message', timeout=15.0, check=check)
        if msg.content.strip() == capital:
            add_points(msg.author.id, 10)
            await ctx.send(f"🎉 صح يا {msg.author.mention}! العاصمة هي **{capital}**")
        else:
            await ctx.send(f"❌ خطأ! العاصمة الصحيحة: {capital}")
    except asyncio.TimeoutError:
        await ctx.send(f"⏰ انتهى الوقت! العاصمة: {capital}")

@bot.command(name='اشبك')
async def cmd_ashbak(ctx):
    await ctx.send(f"🔗 اشبك الحروف التالية لتكوين كلمة مفيدة!")

@bot.command(name='كت')
async def cmd_cut(ctx):
    qs = ["لو خيروك بين: بدون إنترنت أو بدون أصدقاء؟", "لو خيروك بين: السفر للماضي أو للمستقبل؟"]
    embed = discord.Embed(title="❓ سؤال كت", description=random.choice(qs), color=discord.Color.purple())
    await ctx.send(embed=embed)

@bot.command(name='اسرع')
async def cmd_asra3(ctx):
    word = random.choice(["تفاحة", "سرعة", "صاروخ", "برمجة"])
    await ctx.send(f"⚡ أسرع واحد يكتب هذه الكلمة: **{word}**")
    def check(m):
        return m.content.strip() == word and not m.author.bot
    try:
        msg = await bot.wait_for('message', timeout=10.0, check=check)
        add_points(msg.author.id, 15)
        await ctx.send(f"🏆 كفو {msg.author.mention} أسرع واحد! (+15 نقطة)")
    except asyncio.TimeoutError:
        await ctx.send(f"⏰ خلص الوقت!")

@bot.command(name='كمل')
async def cmd_kamel(ctx):
    await ctx.send(f"📝 كمل المثل التالي: (من طلب العلا ...)")

@bot.command(name='فكك')
async def cmd_unpack(ctx):
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
async def cmd_flags(ctx):
    await ctx.send(f"🚩 ما هو اسم الدولة صاحبة هذا العلم؟ 🇸🇦")

@bot.command(name='التالي')
async def cmd_next(ctx):
    await ctx.send(f"⏭️ تم تخطي السؤال والانتقال للسؤال التالي بنجاح!")

@bot.command(name='جمع')
async def cmd_gam3(ctx):
    await ctx.send(f"➕ اجمع الحروف التالية لتكون كلمة: (ك - ت - ا - ب)")

@bot.command(name='عكس')
async def cmd_reverse(ctx):
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
async def cmd_mufrad(ctx):
    await ctx.send(f"👤 أوجد مفرد الكلمة التالية: (أقلام)")

# ==================== الأوامر العامة والأخرى ====================

@bot.command(name='تصويت')
async def cmd_vote(ctx, *, topic: str = "تصويت جديد"):
    embed = discord.Embed(title="📊 صندوق التصويت", description=topic, color=discord.Color.green())
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")

@bot.command(name='توب')
async def cmd_top(ctx, game_name: str = None):
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
async def cmd_my_points(ctx):
    pts = user_points.get(ctx.author.id, 0)
    await ctx.send(f"📊 {ctx.author.mention}, رصيدك: **{pts}** نقطة.")

@bot.command(name='تحويل')
async def cmd_transfer(ctx, member: discord.Member, amount: int):
    sender_pts = user_points.get(ctx.author.id, 0)
    if amount <= 0 or sender_pts < amount:
        await ctx.send("❌ عذراً، لا توجد نقاط كافية أو القيمة غير صالحة.")
        return
    user_points[ctx.author.id] -= amount
    add_points(member.id, amount)
    await ctx.send(f"✅ تم تحويل **{amount}** نقطة إلى {member.mention}!")

@bot.command(name='ايقاف')
async def cmd_stop(ctx):
    await ctx.send(f"🛑 تم إيقاف الألعاب بواسطة {ctx.author.mention}.")

# تشغيل البوت
keep_alive()
bot.run(os.environ['TOKEN'])
