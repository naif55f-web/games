import discord
from discord.ext import commands
import os
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'البوت شغال وجاهز باسم: {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"تم مزامنة {len(synced)} أمر بنجاح.")
    except Exception as e:
        print(e)

# ==================== 1. بوت بينج (Ping) ====================
@bot.tree.command(name="ping", description="يقيس سرعة استجابة البوت")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! السرعة: `{latency}ms`")

# ==================== 2. بوت حذف الشات (Clear) ====================
@bot.tree.command(name="clear", description="حذف عدد معين من الرسائل")
@discord.app_commands.default_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    if amount <= 0:
        await interaction.response.send_message("❌ الرجاء إدخال رقم أكبر من الصفر.", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"✅ تم حذف `{len(deleted)}` رسالة بنجاح.", ephemeral=True)

# ==================== 3. بوت ترحيب (Welcome) ====================
@bot.event
async def on_member_join(member: discord.Member):
    # يُفضّل تخصيص روم ترحيب معين، هنا سيرسل في الروم الافتتاحي أو العامة إن وجدت
    for channel in member.guild.text_channels:
        if "welcome" in channel.name or "ترحيب" in channel.name or "الرئيسية" in channel.name:
            await channel.send(f"حياك الله {member.mention}، نورت السيرفر! 🎉")
            break

# ==================== 4. بوت معلومات (Server Info) ====================
@bot.tree.command(name="server", description="يعرض معلومات السيرفر")
async def server_info(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"📊 معلومات سيرفر: {guild.name}", color=discord.Color.blue())
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="👑 صاحب السيرفر", value=guild.owner.mention, inline=True)
    embed.add_field(name="👥 عدد الأعضاء", value=str(guild.member_count), inline=True)
    embed.add_field(name="📅 تاريخ الإنشاء", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
    await interaction.response.send_message(embed=embed)

# ==================== 5. بوت أفاتار (Avatar) ====================
@bot.tree.command(name="avatar", description="يعرض صورة البروفایل لشخص معين")
async def avatar(interaction: discord.Interaction, user: discord.Member = None):
    target = user or interaction.user
    embed = discord.Embed(title=f"🖼️ صورة الأفاتار لـ {target.name}", color=discord.Color.gold())
    embed.set_image(url=target.display_avatar.url)
    await interaction.response.send_message(embed=embed)

# ==================== 6. بوت قوانين (Rules) ====================
@bot.tree.command(name="rules", description="يرسل قوانين السيرفر الرسمية")
@discord.app_commands.default_permissions(administrator=True)
async def rules(interaction: discord.Interaction):
    embed = discord.Embed(title="📜 قوانين السيرفر", description="الرجاء الالتزام بالقوانين لضمان تجربة ممتعة للجميع:", color=discord.Color.red())
    embed.add_field(name="1️⃣ الاحترام المتبادل", value="يمنع الشتم أو الاستهزاء بأي عضو.", inline=False)
    embed.add_field(name="2️⃣ عدم السبام", value="يمنع إرسال الرسائل المتكررة أو الإزعاج.", inline=False)
    embed.add_field(name="3️⃣ الإعلانات", value="يمنع نشر روابط سيرفرات أخرى أو روابط خارجية.", inline=False)
    await interaction.channel.send(embed=embed)
    await interaction.response.send_message("✅ تم نشر القوانين بنجاح.", ephemeral=True)

# ==================== 7. بوت اقتراحات (Suggest) ====================
@bot.tree.command(name="suggest", description="إرسال اقتراح جديد للتصويت")
async def suggest(interaction: discord.Interaction, *, suggestion: str):
    embed = discord.Embed(title="💡 اقتراح جديد", description=suggestion, color=discord.Color.green())
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
    
    await interaction.response.send_message("✅ تم إرسال اقتراحك بنجاح!", ephemeral=True)
    
    msg = await interaction.channel.send(embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")

# ==================== 8. بوت إعلان (Announce) ====================
@bot.tree.command(name="announce", description="إرسال إعلان رسمي ومرتب")
@discord.app_commands.default_permissions(administrator=True)
async def announce(interaction: discord.Interaction, title: str, *, message: str):
    embed = discord.Embed(title=f"📢 {title}", description=message, color=discord.Color.orange())
    embed.set_footer(text=f"بواسطة: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
    
    await interaction.channel.send(embed=embed)
    await interaction.response.send_message("✅ تم نشر الإعلان بنجاح.", ephemeral=True)

keep_alive()
bot.run(os.environ['TOKEN'])
