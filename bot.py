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
        value="• مافيا (بنظام الأزرار والأدوار الكاملة)\n• روليت\n• عكسي\n• سكات\n• وصل\n• لغم\n• بومب\n• كراسي\n• نرد\n• خمن\n• حجره\n• اكس",
        inline=False
    )
    await ctx.send(embed=embed)

# ==================== نظام أزرار الانضمام والمافيا ====================

class JoinGameView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=45) # مهلة 45 ثانية للتسجيل
        self.participants = []

    @discord.ui.button(label="انضمام 🎮", style=discord.ButtonStyle.green, custom_id="join_btn")
    async def join_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user not in self.participants:
            self.participants.append(interaction.user)
            await interaction.response.send_message(f"✅ تم انضمامك بنجاح للعبة!", ephemeral=True)
            await self.update_embed(interaction)
        else:
            await interaction.response.send_message(f"⚠️ أنت منضم مسبقاً!", ephemeral=True)

    @discord.ui.button(label="انسحاب ❌", style=discord.ButtonStyle.red, custom_id="leave_btn")
    async def leave_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.participants:
            self.participants.remove(interaction.user)
            await interaction.response.send_message(f"❌ تم انسحابك من اللعبة.", ephemeral=True)
            await self.update_embed(interaction)
        else:
            await interaction.response.send_message(f"⚠️ أنت لست منضماً أصلاً!", ephemeral=True)

    async def update_embed(self, interaction: discord.Interaction):
        names = "\n".join([f"• {p.display_name}" for p in self.participants]) if self.participants else "لا يوجد لاعبين حتى الآن..."
        embed = discord.Embed(
            title="🕵️ لعبة المافيا - تسجيل الدخول",
            description=f"اضغط على **انضمام** للمشاركة أو **انسحاب** للتراجع.\n\n**المسجلون حالياً ({len(self.participants)}):**\n{names}",
            color=discord.Color.dark_theme()
        )
        await interaction.message.edit(embed=embed, view=self)

class MafiaSelectView(discord.ui.View):
    def __init__(self, players, action_type):
        super().__init__(timeout=30)
        self.value = None
        for player in players:
            self.add_item(MafiaButton(player, action_type))

class MafiaButton(discord.ui.Button):
    def __init__(self, player, action_type):
        super().__init__(label=player.display_name, style=discord.ButtonStyle.secondary)
        self.target_player = player
        self.action_type = action_type

    async def callback(self, interaction: discord.Interaction):
        self.view.value = self.target_player
        await interaction.response.send_message(f"✅ تم تسجيل اختيارك بنجاح ({self.action_type}): **{self.target_player.display_name}**", ephemeral=True)
        self.view.stop()

@bot.command(name='مافيا')
async def cmd_mafia(ctx):
    view = JoinGameView()
    embed = discord.Embed(
        title="🕵️ لعبة المافيا - تسجيل الدخول",
        description="اضغط على زر **انضمام 🎮** أدناه للمشاركة في اللعبة (معاك 45 ثانية):",
        color=discord.Color.dark_theme()
    )
    msg = await ctx.send(embed=embed, view=view)
    
    # الانتظار حتى تنتهي المهلة
    await view.wait()
    
    participants = view.participants
    if len(participants) < 3:
        await ctx.send("❌ عذراً، لم يكتمل العدد (الحد الأدنى 3 لاعبين). تم إلغاء اللعبة.")
        return

    # تعطيل الأزرار بعد بدء اللعبة
    for child in view.children:
        child.disabled = True
    try:
        await msg.edit(view=view)
    except:
        pass

    # توزيع الأدوار
    random.shuffle(participants)
    roles = {}
    roles[participants[0]] = 'mafia'
    roles[participants[1]] = 'doctor'
    for p in participants[2:]:
        roles[p] = 'citizen'

    await ctx.send(f"🔒 **تم توزيع الأدوار سراً!** عدد اللاعبين المشاركين: {len(participants)}. تفقد رسائلك الخاصة (DM).")

    # إرسال الأدوار بالخاص
    for player, role in roles.items():
        try:
            if role == 'mafia':
                await player.send("🔪 **أنت المافيا!** هدفك القضاء على الجميع بهدوء دون أن يتم كشفك.")
            elif role == 'doctor':
                await player.send("💉 **أنت الطبيب!** دورك حماية نفسك أو أحد اللاعبين كل ليلة من غدر المافيا.")
            else:
                await player.send("👥 **أنت مواطن بريء!** حاول اكتشاف المافيا والتصويت ضدهم.")
        except:
            pass

    # مرحلة الليل
    await ctx.send("🌙 **حل الليل...** تنام المدينة وتبدأ تحركات المافيا والطبيب في الخفاء.")
    
    mafia_player = [p for p, r in roles.items() if r == 'mafia'][0]
    doctor_player = [p for p, r in roles.items() if r == 'doctor'][0]

    # اختيار المافيا عبر الخاص
    mafia_target = None
    try:
        view_m = MafiaSelectView(participants, "القتل")
        await mafia_player.send("🔪 **اختر الشخص الذي تريد قتله هذه الليلة:**", view=view_m)
        await view_m.wait()
        mafia_target = view_m.value
    except:
        pass

    # اختيار الطبيب عبر الخاص
    doctor_target = None
    try:
        view_d = MafiaSelectView(participants, "الحماية")
        await doctor_player.send("💉 **اختر الشخص الذي تريد حمايته هذه الليلة:**", view=view_d)
        await view_d.wait()
        doctor_target = view_d.value
    except:
        pass

    await asyncio.sleep(3)
    await ctx.send("☀️ **اشرقت شمس اليوم الجديد!** حان وقت الكشف عن الأحداث...")

    # نتيجة الليل
    if not mafia_target:
        await ctx.send("🌅 مر ليل هادئ ولم يحدث أي مكروه اليوم.")
    elif mafia_target == doctor_target:
        await ctx.send(f"🛡️ هجمت المافيا على **{mafia_target.display_name}**، لكن الطبيب كان في الأرجح وقام بحمايته! **تمت حماية هذا المواطن من القتل وفشلت عملية القتل بنجاح! 🎉**")
    else:
        await ctx.send(f"💀 للأسف، نجحت المافيا واغتالت اللاعب **{mafia_target.display_name}** بالليل!")
        if mafia_target in participants:
            participants.remove(mafia_target)

    # مرحلة التصويت الجماعي لطرد المشتبه بهم
    await ctx.send("🗳️ **بدأت مرحلة التصويت النقاشي!** من تظن أنه المافيا؟ (منشن الشخص أو اكتب اسمه في الشات خلال 15 ثانية)")

    votes = {}
    def vote_check(m):
        return m.channel == ctx.channel and not m.author.bot

    vote_end = asyncio.get_event_loop().time() + 15
    while asyncio.get_event_loop().time() < vote_end:
        try:
            v_msg = await bot.wait_for('message', timeout=3.0, check=vote_check)
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
        await ctx.send(f"⚖️ النتيجة: تم طرد **{most_voted.display_name}** بناءً على تصويت الجماعة برصيد {count} أصوات!")
        
        if roles.get(most_voted) == 'mafia':
            await ctx.send(f"🎉 **مبروك للمواطنين والطبيب!** لقد تم القضاء على المافيا الخفي **{most_voted.display_name}** وفاز الفريق الطيب!")
        else:
            await ctx.send(f"❌ للأسف، طلع شخص بريء (**{roles.get(most_voted)}**) وفازت المافيا باللعبة!")
    else:
        await ctx.send("⏰ انتهى الوقت بدون تصويت حاسم ونجت المافيا!")

# ==================== الألعاب الأخرى ====================

@bot.command(name='روليت')
async def cmd_roulette(ctx):
    survived = random.choice([True, True, True, False])
    if survived:
        add_points(ctx.author.id, 15)
        await ctx.send(f"🔫 {ctx.author.mention} سحب الزناد... نجا ولله الحمد! (+15 نقطة).")
    else:
        await ctx.send(f"💥 بـووووم! {ctx.author.mention} طاحت عليه الرصاصة! 💀")

@bot.command(name='توب')
async def cmd_top(ctx):
    if not user_points:
        await ctx.send("🏆 مافي نقاط مسجلة لحد الآن!")
        return
    sorted_users = sorted(user_points.items(), key=lambda x: x[1], reverse=True)[:5]
    desc = ""
    for i, (uid, pts) in enumerate(sorted_users, 1):
        user = ctx.guild.get_member(uid)
        name = user.name if user else "لاعب"
        desc += f"{i}. **{name}** - `{pts}` نقطة\n"
    embed = discord.Embed(title="🏆 لوحة الشرف العامة", description=desc, color=discord.Color.gold())
    await ctx.send(embed=embed)

@bot.command(name='نقاطي')
async def cmd_my_points(ctx):
    pts = user_points.get(ctx.author.id, 0)
    await ctx.send(f"📊 {ctx.author.mention}, رصيدك: **{pts}** نقطة.")

# تشغيل البوت
keep_alive()
bot.run(os.environ['TOKEN'])
