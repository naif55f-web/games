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

bot = commands.Bot(command_prefix='-', intents=intents)

# قواعد البيانات المؤقتة
active_tickets = {} 
closed_tickets = set()
ticket_stats = defaultdict(lambda: {"opened": 0, "closed": 0})
warns = defaultdict(int)

# إعدادات البوت الافتراضية
ticket_settings = {
    "panel_channel": None,
    "log_channel": None,
    "category_id": None,
    "global_support_role": None,
    "panel_image": "https://cdn.discordapp.com/attachments/1534396073072656558/1535009128978714695/panel.png",
    "type_roles": {
        "support": None,
        "staff_apply_boys": None,
        "staff_apply_girls": None,
        "scrim": None,
        "store": None,
        "partnerships": None
    },
    "type_messages": {
        "support": "يرجى شرح مشكلتك أو طلبك التقني بالتفصيل وسيتم الرد عليك قريباً.",
        "staff_apply_boys": "أهلاً بك في تقديم فرع العيال، يرجى تعبئة النموذج وإرسال المعلومات المطلوبة.",
        "staff_apply_girls": "أهلاً بكِ في تقديم فرع البنات، يرجى إرسال تفاصيل التقديم هنا.",
        "scrim": "يرجى كتابة اسم كلانك وعدد اللاعبين لترتيب السكرم.",
        "store": "مرحباً بك، اذكر الرتبة أو الطلب الذي تريده مع طريقة الدفع.",
        "partnerships": "أهلاً بك في قسم التعاونات، ارسل تفاصيل سيرفرك أو عرضك."
    }
}

@bot.event
async def on_ready():
    print(f'بوت Naxo الشخصي الشامل يعمل بنجاح: {bot.user}')

# ==================== نظام قائمة الأوامر المنسدلة الاحترافية (-all) ====================

class AllCommandsDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="1. الأوامر العامة والإدارة", description="عرض أوامر بينج، كلير، سيرفر، أفتار، اقتراحات، السجلات", value="all_gen"),
            discord.SelectOption(label="2. نظام الاقتصاد والألعاب", description="عرض أوامر الرصيد، دايلي، وورك، شوب، وألعاب الحظ", value="all_eco"),
            discord.SelectOption(label="3. متجر السيرفر والحقيبة", description="عرض أوامر المتجر وشراء الرتب والمخزون", value="all_store"),
            discord.SelectOption(label="4. الإدارة المالية للمسؤولين", description="عرض أوامر إضافة وتصفير أرصدة الأعضاء", value="all_fin"),
            discord.SelectOption(label="5. نظام المصارحات Tellonym", description="عرض أوامر المصارحات السرية وإعداد الروم", value="all_tell"),
            discord.SelectOption(label="6. نظام البرودكاست المتطور", description="عرض أوامر البرودكاست العام والرتب والرومات", value="all_bc"),
            discord.SelectOption(label="7. الردود والذكاء والحماية", description="عرض الردود التلقائية وحماية السبام والرايد", value="all_auto")
        ]
        super().__init__(placeholder="يرجى الاختيار لعرض قسم الأوامر المطلوبة ..", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        val = self.values[0]
        if val == "all_gen":
            text = (
                "**1. الأوامر العامة والإدارة السريعة**\n"
                "• `-k` : عرض قائمة الأوامر العامة الأساسية.\n"
                "• `-ping` : قياس سرعة استجابة البوت بالمللي ثانية.\n"
                "• `-clear [العدد]` : حذف الرسائل دفعة واحدة (للإدارة).\n"
                "• `-server` : عرض معلومات السيرفر الكاملة.\n"
                "• `-avatar [@user]` : عرض صورة الأفاتار الخاصة بك أو بأي عضو.\n"
                "• `-rules` : نشر قوانين السيرفر الرسمية.\n"
                "• `-suggest [الاقتراح]` : إرسال اقتراح مع أزرار للتصويت (ايجاب وسلب).\n"
                "• `-announce [النص] [العنوان]` : إرسال إعلان رسمي مرتب للإدارة.\n"
                "• `-log` : عرض لوحة تحكم وحالة السجلات والحماية."
            )
        elif val == "all_eco":
            text = (
                "**2. نظام الاقتصاد والألعاب المتكامل**\n"
                "• `-c` : عرض قائمة أوامر الاقتصاد.\n"
                "• `-bal` أو `-balance [@user]` : عرض رصيدك أو رصيد عضو آخر.\n"
                "• `-daily` : استلام المكافأة اليومية (500 عملة كل 24 ساعة).\n"
                "• `-work` : العمل لكسب دخل عشوائي (100-300 عملة كل ساعة).\n"
                "• `-beg` : الشاذة للحصول على مبلغ بسيط (كل 15 دقيقة).\n"
                "• `-pay [@user] [المبلغ]` : تحويل أموال لعضو آخر.\n"
                "• `-leaderboard` أو `-lb` : قائمة أغنى 10 أشخاص في السيرفر.\n"
                "• `-slots [المبلغ]` : ماكينة الحظ لمضاعفة الأرباح.\n"
                "• `-dice [المبلغ]` : رمي النرد والمنافسة ضد البوت.\n"
                "• `-coinflip [صورة/كتابة] [المبلغ]` : لعبة العملة المعدنية."
            )
        elif val == "all_store":
            text = (
                "**3. متجر السيرفر والحقيبة**\n"
                "• `-shop` : تغيير لون، رتب) عرض المنتجات المتاحة للشراء (VIP، إلخ).\n"
                "• `-buy [الاسم]` : شراء منتج من المتجر برصيدك.\n"
                "• `-inventory` : عرض محتويات حقيبتك وما تملكه.\n"
                "• `-use [الاسم]` : استخدام عنصر قمت بشرائه من الحقيبة."
            )
        elif val == "all_fin":
            text = (
                "**4. أوامر الإدارة المالية (للمسؤولين فقط)**\n"
                "• `-addcoins [@user] [المبلغ]` : إضافة أموال لرصيد عضو.\n"
                "• `-removecoins [@user] [المبلغ]` : خصم أموال من رصيد عضو.\n"
                "• `-setcoins [@user] [المبلغ]` : تعيين رصيد محدد لعضو.\n"
                "• `-resetcoins [@user]` : تصفير رصيد العضو تماماً."
            )
        elif val == "all_tell":
            text = (
                "**5. نظام المصارحات (Tellonym)**\n"
                "• `-tell` : عرض شرح وأوامر نظام المصارحات.\n"
                "• `-sendtell [@user] [الرسالة]` : إرسال مصارحة سرية لعضو (مع حذف رسالتك تلقائياً للسرية).\n"
                "• `-setchannel` : تحديد روم استقبال المصارحات تلقائياً.\n"
                "• مصطلحات النظام: Tellonym (صارحة)، Anonymous (مجهول)، Inbox (صندوق الوارد)."
            )
        elif val == "all_bc":
            text = (
                "**6. نظام البرودكاست المتطور**\n"
                "• `-broadcast` : عرض شرح وأوامر نظام البرودكاست الشامل.\n"
                "• `-bc [الرسالة]` : إرسال برودكاست عام لجميع الأعضاء عبر الخاص مع إحصائيات.\n"
                "• `-bc-role [@الرتبة] [الرسالة]` : إرسال برودكاست لأصحاب رتبة معينة عبر الخاص.\n"
                "• `-bc-room [#روم] [الرسالة]` : إرسال برودكاست رسمي داخل روم معين.\n"
                "• والمتغيرات المتاحة: `{user}` لمنشن العضو، `{username}` لاسم العضو، `{server}` لاسم السيرفر، `{members}` لعدد الأعضاء."
            )
        elif val == "all_auto":
            text = (
                "**7. الردود الذكية والحماية (تعمل تلقائياً بدون بريفكس)**\n"
                "• منو قطوتي -> يرجع البوت بـ (مياو)\n"
                "• منو بطتي -> يرجع البوت بـ (بط بط)\n"
                "• شاطر أو شاطرة -> يرجع البوت بـ (كلزق)\n"
                "• حماية السبام التلقائي : حذف الرسائل المتكررة السريعة وإرسال تحذير للسجلات.\n"
                "• مكافحة الرايد : رصد دخول أعداد هائلة من الأعضاء في ثوان معدودة.\n"
                "• سجلات الرومات والرتب والرسائل : تتبع التعديل والحذف والإنشاء تلقائياً.\n\n"
                "طلب بواسطة: x | جميع الحقوق محفوظة"
            )
        else:
            text = "يرجى اختيار قسم صحيح."

        embed = discord.Embed(
            description=text,
            color=discord.Color.from_rgb(35, 39, 42)
        )
        await interaction.response.edit_message(embed=embed, view=AllCommandsView())

class AllCommandsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=900)  # وقت طويل يصل لـ 15 دقيقة لعدم انتهاء التفاعل بسرعة
        self.add_item(AllCommandsDropdown())

@bot.command(name="all")
async def all_commands_cmd(ctx):
    await ctx.message.delete()
    intro_text = (
        "**دليل جميع أوامر وأنظمة البوت الشاملة حرفياً**\n"
        "إليك كافة الأوامر، الأنظمة، الألعاب، والشروحات الموجودة داخل البوت بالتفصيل.\n"
        "اختر من القائمة أدناه لعرض تفاصيل وشرح أي قسم تريد:"
    )
    embed = discord.Embed(
        description=intro_text,
        color=discord.Color.from_rgb(35, 39, 42)
    )
    view = AllCommandsView()
    await ctx.send(embed=embed, view=view)

# ==================== القائمة الهرمية للتحكم ($settings) ====================

class MainSettingsDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="1. إدارة الأقسام والتكتات", description="التحكم الكامل بأقسام الدعم والتقديم والطلبات", value="tickets_mgmt"),
            discord.SelectOption(label="2. إدارة الرتب والمشرفين", description="تحديد رتب الدعم لكل قسم على حدة", value="roles_mgmt"),
            discord.SelectOption(label="3. إعدادات الرومات والسجلات", description="تحديد روم السجلات والتصنيفات", value="channels_mgmt"),
            discord.SelectOption(label="4. دليل الأوامر والاختصارات", description="عرض شرح سريع لكافة أوامر البوت وطرق استخدامها", value="help_guide"),
            discord.SelectOption(label="5. إحصائيات ونشاط البوت", description="عرض تقارير التكتات المفتوحة والمغلقة", value="stats_view"),
            discord.SelectOption(label="6. نشر لوحة التكتات الأساسية", description="إرسال البنرات والقائمة في الروم الحالي", value="send_panel_main")
        ]
        super().__init__(placeholder="اختر القسم أو النظام للتحكم به ..", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        val = self.values[0]
        if val == "tickets_mgmt":
            await interaction.response.edit_message(content="**قسم إدارة التكتات والأقسام الفرعية:**\nاختر القسم الذي تريد تعديله:", view=SubDepartmentsView())
        elif val == "roles_mgmt":
            role = interaction.guild.get_role(ticket_settings["global_support_role"]) if ticket_settings["global_support_role"] else "غير محدد"
            await interaction.response.edit_message(content=f"**قسم إدارة الرتب:**\nرتبة الدعم العامة الحالية: {role.mention if hasattr(role, 'mention') else role}\n\n**الأوامر الخاصة بالرتب:**\n• `-setsupportrole @الرتبة`", view=MainSettingsView())
        elif val == "channels_mgmt":
            log = interaction.guild.get_channel(ticket_settings["log_channel"]) if ticket_settings["log_channel"] else "غير محدد"
            cat = interaction.guild.get_channel(ticket_settings["category_id"]) if ticket_settings["category_id"] else "غير محدد"
            await interaction.response.edit_message(content=f"**قسم الرومات:**\nروم السجلات: {log.mention if hasattr(log, 'mention') else log}\nالتصنيف الأساسي: {cat.name if hasattr(cat, 'name') else cat}\n\n**الأوامر الخاصة:**\n• `-setlog #روم`\n• `-setcategory #تصنيف`", view=MainSettingsView())
        elif val == "help_guide":
            await interaction.response.edit_message(content="**دليل الأوامر السريعة:**\n1. `-setup-ticket` : نشر اللوحة.\n2. `-close` : إغلاق تكت.\n3. `-warn / -ban / -kick` : الإدارة.\n4. `-clear [عدد]` : مسح الرسائل.", view=MainSettingsView())
        elif val == "stats_view":
            total_active = len(active_tickets)
            await interaction.response.edit_message(content=f"**إحصائيات البوت:**\nالتكتات النشطة حالياً: {total_active}", view=MainSettingsView())
        elif val == "send_panel_main":
            view = TicketSelectView()
            await interaction.channel.send(content=ticket_settings["panel_image"], view=view)
            await interaction.response.edit_message(content="تم إرسال لوحة التكتات بنجاح في الشات.", view=MainSettingsView())

class SubDepartmentsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=900)

    @discord.ui.select(placeholder="اختر القسم الفرعي للتفاصيل ..", options=[
        discord.SelectOption(label="الدعم الفني (Support)", value="sub_support"),
        discord.SelectOption(label="تقديم العيال (Boys Apply)", value="sub_boys"),
        discord.SelectOption(label="تقديم البنات (Girls Apply)", value="sub_girls"),
        discord.SelectOption(label="السكرم والبطولات (Scrim)", value="sub_scrim"),
        discord.SelectOption(label="طلب الرتب (Store)", value="sub_store"),
        discord.SelectOption(label="التعاونات والشراكات (Partnerships)", value="sub_partners")
    ])
    async def sub_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        dept = select.values[0]
        key = dept.replace("sub_", "")
        msg = ticket_settings["type_messages"].get(key, "لا توجد رسالة.")
        await interaction.response.edit_message(content=f"**إعدادات القسم ({key}):**\nالرسالة الحالية:\n> {msg}", view=MainSettingsView())

    @discord.ui.button(label="العودة للقائمة الرئيسية", style=discord.ButtonStyle.grey, custom_id="back_home_naxo_ultimate")
    async def back_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="لوحة التحكم الرئيسية:", view=MainSettingsView())

class MainSettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=900)
        self.add_item(MainSettingsDropdown())

    @discord.ui.button(label="إغلاق اللوحة", style=discord.ButtonStyle.red, custom_id="close_main_settings_naxo_ultimate")
    async def close_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()

@bot.command(name="settings")
@commands.has_permissions(administrator=True)
async def settings_dashboard(ctx):
    await ctx.message.delete()
    log_ch = ctx.guild.get_channel(ticket_settings["log_channel"]) if ticket_settings["log_channel"] else None
    sup_role = ctx.guild.get_role(ticket_settings["global_support_role"]) if ticket_settings["global_support_role"] else None
    cat_ch = ctx.guild.get_channel(ticket_settings["category_id"]) if ticket_settings["category_id"] else None

    embed = discord.Embed(
        title="Naxo Hub • لوحة التحكم الشخصية",
        description=(
            f"**روم السجلات:** {log_ch.mention if log_ch else 'غير محدد'}\n"
            f"**رتبة الدعم:** {sup_role.mention if sup_role else 'غير محددة'}\n"
            f"**تصنيف التكتات:** {cat_ch.name if cat_ch else 'غير محدد'}\n\n"
            f"استخدم القائمة أدناه للتحكم:"
        ),
        color=discord.Color.from_rgb(35, 39, 42)
    )
    await ctx.send(embed=embed, view=MainSettingsView())

# ==================== أوامر الإدارة والحماية ====================
@bot.command(name="warn")
@commands.has_permissions(manage_messages=True)
async def warn_cmd(ctx, member: discord.Member, *, reason="لا يوجد سبب"):
    await ctx.message.delete()
    warns[member.id] += 1
    await ctx.send(f"تم تحذير {member.mention}. إجمالي التحذيرات: {warns[member.id]}. السبب: {reason}")

@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban_cmd(ctx, member: discord.Member, *, reason="لا يوجد سبب"):
    await ctx.message.delete()
    await member.ban(reason=reason)
    await ctx.send(f"تم حظر {member.name} نهائياً. السبب: {reason}")

@bot.command(name="kick")
@commands.has_permissions(kick_members=True)
async def kick_cmd(ctx, member: discord.Member, *, reason="لا يوجد سبب"):
    await ctx.message.delete()
    await member.kick(reason=reason)
    await ctx.send(f"تم طرد {member.name}. السبب: {reason}")

@bot.command(name="clear")
@commands.has_permissions(manage_messages=True)
async def clear_messages(ctx, amount: int = 10):
    await ctx.message.delete()
    deleted = await ctx.channel.purge(limit=amount)
    await ctx.send(f"تم مسح {len(deleted)} رسالة بنجاح.", delete_after=4)

@bot.command(name="setsupportrole")
@commands.has_permissions(administrator=True)
async def set_support_role(ctx, role: discord.Role):
    await ctx.message.delete()
    ticket_settings["global_support_role"] = role.id
    await ctx.send(f"تم تحديد رتبة الدعم العامة: {role.mention}", delete_after=5)

@bot.command(name="setlog")
@commands.has_permissions(administrator=True)
async def set_log(ctx, channel: discord.TextChannel):
    await ctx.message.delete()
    ticket_settings["log_channel"] = channel.id
    await ctx.send(f"تم تعيين روم السجلات: {channel.mention}", delete_after=5)

@bot.command(name="setcategory")
@commands.has_permissions(administrator=True)
async def set_category(ctx, category: discord.CategoryChannel):
    await ctx.message.delete()
    ticket_settings["category_id"] = category.id
    await ctx.send(f"تم تعيين تصنيف التكتات: {category.name}", delete_after=5)

@bot.command(name="setup-ticket")
@commands.has_permissions(administrator=True)
async def setup_ticket(ctx):
    await ctx.message.delete()
    view = TicketSelectView()
    await ctx.channel.send(content=ticket_settings["panel_image"], view=view)

@bot.command(name="ping")
async def check_ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"سرعة استجابة البوت: {latency}ms")

@bot.command(name="userinfo")
async def userinfo_cmd(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"معلومات المستخدم: {member.name}", color=discord.Color.blue())
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="تاريخ الانضمام للديسكورد", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="تاريخ الانضمام للسيرفر", value=member.joined_at.strftime("%Y-%m-%d") if member.joined_at else "غير معروف", inline=True)
    await ctx.send(embed=embed)

@bot.command(name="avatar")
async def avatar_cmd(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"صورة {member.name}", color=discord.Color.dark_purple())
    embed.set_image(url=member.avatar.url if member.avatar else member.default_avatar.url)
    await ctx.send(embed=embed)

# ==================== لوحة التكتات والأزرار ====================
class TicketSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="اختر القسم المطلوب لفتح تذكرة ..",
        options=[
            discord.SelectOption(label="الدعم الفني", value="support", description="للشكاوى والمشاكل التقنية"),
            discord.SelectOption(label="تقديم فرع العيال", value="staff_apply_boys", description="للتقديم على الإدارة"),
            discord.SelectOption(label="تقديم فرع البنات", value="staff_apply_girls", description="للتقديم على الإدارة النسائية"),
            discord.SelectOption(label="طلب سكرم", value="scrim", description="تنظيم ومباريات السكرم"),
            discord.SelectOption(label="طلب رتبة", value="store", description="شراء واستفسارات الرتب"),
            discord.SelectOption(label="التعاونات", value="partnerships", description="الشراكات والاعلانات")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        guild = interaction.guild
        user = interaction.user

        if user.id in active_tickets:
            chan = guild.get_channel(active_tickets[user.id])
            if chan:
                await interaction.response.send_message(f"لديك تكت مفتوح مسبقاً هنا: {chan.mention}", ephemeral=True)
                return
            else:
                active_tickets.pop(user.id, None)

        ticket_type = select.values[0]
        type_names = {
            "support": "الدعم-الفني",
            "staff_apply_boys": "تقديم-عيال",
            "staff_apply_girls": "تقديم-بنات",
            "scrim": "طلب-سكرم",
            "store": "طلب-رتبه",
            "partnerships": "تعاونات"
        }
        
        channel_name = f"ticket-{type_names.get(ticket_type, 'support')}-{user.name}"
        category = guild.get_channel(ticket_settings["category_id"]) if ticket_settings["category_id"] else None
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
        }
        
        target_role_id = ticket_settings["type_roles"].get(ticket_type) or ticket_settings.get("global_support_role")
        if target_role_id:
            support_role = guild.get_role(target_role_id)
            if support_role:
                overwrites[support_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        try:
            ticket_channel = await guild.create_text_channel(name=channel_name, category=category, overwrites=overwrites)
        except Exception as e:
            await interaction.response.send_message(f"حدث خطأ أثناء الإنشاء: {e}", ephemeral=True)
            return

        active_tickets[user.id] = ticket_channel.id
        custom_msg = ticket_settings["type_messages"].get(ticket_type, "يرجى توضيح طلبك.")

        embed = discord.Embed(
            title=f"تكت: {select.values[0]}",
            description=f"مرحباً بك {user.mention}\n{custom_msg}",
            color=discord.Color.dark_theme()
        )
        embed.set_footer(text=f"صاحب التكت ID: {user.id}")

        control_view = TicketControlView()
        ping_content = f"{user.mention}"
        if target_role_id:
            ping_content += f" <@&{target_role_id}>"

        await ticket_channel.send(content=ping_content, embed=embed, view=control_view)
        await interaction.response.send_message(f"تم إنشاء تكت الخاص بك بنجاح: {ticket_channel.mention}", ephemeral=True)

class TicketControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="إغلاق التكت", style=discord.ButtonStyle.red, custom_id="close_ticket_btn_naxo_ultimate")
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.channel
        await interaction.response.send_message("جاري إغلاق التكت وحفظ السجل...")
        for uid, cid in list(active_tickets.items()):
            if cid == channel.id:
                active_tickets.pop(uid, None)
                break
        await asyncio.sleep(2)
        await channel.delete()

@bot.command(name="close")
@commands.has_permissions(manage_channels=True)
async def ticket_close_cmd(ctx):
    await ctx.message.delete()
    channel = ctx.channel
    for uid, cid in list(active_tickets.items()):
        if cid == channel.id:
            active_tickets.pop(uid, None)
            break
    await ctx.send("جاري إغلاق التكت...")
    await asyncio.sleep(2)
    await channel.delete()

@bot.command(name="add")
@commands.has_permissions(manage_channels=True)
async def ticket_add(ctx, member: discord.Member):
    await ctx.message.delete()
    await ctx.channel.set_permissions(member, read_messages=True, send_messages=True)
    await ctx.send(f"تمت إضافة {member.mention} للتكت.", delete_after=5)

@bot.command(name="remove")
@commands.has_permissions(manage_channels=True)
async def ticket_remove(ctx, member: discord.Member):
    await ctx.message.delete()
    await ctx.channel.set_permissions(member, overwrite=None)
    await ctx.send(f"تمت إزالة {member.mention} من التكت.", delete_after=5)

@bot.command(name="lock")
@commands.has_permissions(manage_channels=True)
async def ticket_lock(ctx):
    await ctx.message.delete()
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("تم قفل التكت.", delete_after=5)

@bot.command(name="unlock")
@commands.has_permissions(manage_channels=True)
async def ticket_unlock(ctx):
    await ctx.message.delete()
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("تم فتح التكت.", delete_after=5)

keep_alive()
bot.run(os.environ['TOKEN'])
