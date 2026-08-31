import discord
import asyncio
from discord.ext import commands
from discord.ui import View, Select, Button, Modal, TextInput

STAFF_ROLE_1 = 1543922260623102029
STAFF_ROLE_2 = 1543974160127098975

TICKET_CATEGORY_NAME = "🎫 Ticket"

# ---------------------- BOTTONI COMUNI DI GESTIONE TICKET ----------------------
class TicketManageView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.green, custom_id="ticket_claim")
    async def claim(self, interaction: discord.Interaction, button: Button):
        if not any(r.id in (STAFF_ROLE_1, STAFF_ROLE_2) for r in interaction.user.roles):
            return await interaction.response.send_message("❌ Non hai i permessi per fare claim.", ephemeral=True)
        await interaction.channel.send(f"✅ Ticket preso in carico da {interaction.user.mention}")
        await interaction.response.defer()

    @discord.ui.button(label="Unclaim", style=discord.ButtonStyle.gray, custom_id="ticket_unclaim")
    async def unclaim(self, interaction: discord.Interaction, button: Button):
        if not any(r.id in (STAFF_ROLE_1, STAFF_ROLE_2) for r in interaction.user.roles):
            return await interaction.response.send_message("❌ Non hai i permessi.", ephemeral=True)
        await interaction.channel.send(f"↩️ Ticket rilasciato da {interaction.user.mention}")
        await interaction.response.defer()

    @discord.ui.button(label="Close", style=discord.ButtonStyle.red, custom_id="ticket_close")
    async def close(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("🔒 Il ticket verrà eliminato tra 5 secondi...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

    @discord.ui.button(label="Close with reason", style=discord.ButtonStyle.red, custom_id="ticket_close_reason")
    async def close_with_reason(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(CloseReasonModal())

    @discord.ui.button(label="Add user", style=discord.ButtonStyle.blurple, custom_id="ticket_add_user")
    async def add_user(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(AddUserModal())


class CloseReasonModal(Modal, title="Chiudi ticket con motivazione"):
    reason = TextInput(label="Motivazione", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"🔒 Ticket in chiusura tra 5 secondi.\n**Motivo:** {self.reason.value}"
        )
        channel = interaction.channel
        await asyncio.sleep(5)
        await channel.delete()


class AddUserModal(Modal, title="Aggiungi utente al ticket"):
    user_id = TextInput(label="ID o menzione utente", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            uid = int(self.user_id.value.strip("<@!>"))
            member = interaction.guild.get_member(uid)
            if member is None:
                return await interaction.response.send_message("❌ Utente non trovato.", ephemeral=True)
            await interaction.channel.set_permissions(member, view_channel=True, send_messages=True, read_message_history=True)
            await interaction.response.send_message(f"✅ {member.mention} è stato aggiunto al ticket.")
        except ValueError:
            await interaction.response.send_message("❌ ID non valido.", ephemeral=True)


# ---------------------- FUNZIONE CREAZIONE CANALE TICKET ----------------------
async def create_ticket_channel(interaction: discord.Interaction, prefix: str, topic: str):
    guild = interaction.guild
    category = discord.utils.get(guild.categories, name=TICKET_CATEGORY_NAME)
    if category is None:
        category = await guild.create_category(TICKET_CATEGORY_NAME)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        guild.get_role(STAFF_ROLE_1): discord.PermissionOverwrite(view_channel=True, send_messages=True),
        guild.get_role(STAFF_ROLE_2): discord.PermissionOverwrite(view_channel=True, send_messages=True),
    }

    channel = await guild.create_text_channel(
        name=f"{prefix}-{interaction.user.name}",
        category=category,
        overwrites=overwrites,
        topic=topic
    )

    embed = discord.Embed(
        title=f"🎫 {topic}",
        description=f"Ticket aperto da {interaction.user.mention}\nUno staff member ti risponderà a breve.",
        color=discord.Color.blurple()
    )

    role1 = guild.get_role(STAFF_ROLE_1)
    role2 = guild.get_role(STAFF_ROLE_2)

    await channel.send(
        content=f"{interaction.user.mention} {role1.mention if role1 else ''} {role2.mention if role2 else ''}",
        embed=embed,
        view=TicketManageView()
    )

    await interaction.response.send_message(f"✅ Ticket creato: {channel.mention}", ephemeral=True)


# ---------------------- PANNELLO TICKET PRINCIPALE (SELECT MENU) ----------------------
class MainTicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Aiuto generale", value="aiuto", emoji="❓"),
            discord.SelectOption(label="Segnala utente", value="segnala", emoji="🚨"),
            discord.SelectOption(label="Reclama giveaway", value="giveaway", emoji="🎁"),
            discord.SelectOption(label="Provino staff", value="provino", emoji="📋"),
            discord.SelectOption(label="Partnership", value="partnership", emoji="🤝"),
            discord.SelectOption(label="Idee server", value="idee", emoji="💡"),
        ]
        super().__init__(placeholder="Seleziona il motivo del ticket...", options=options, custom_id="main_ticket_select")

    async def callback(self, interaction: discord.Interaction):
        topics = {
            "aiuto": "Aiuto generale",
            "segnala": "Segnalazione utente",
            "giveaway": "Reclamo giveaway",
            "provino": "Provino staff",
            "partnership": "Partnership",
            "idee": "Idee server"
        }
        await create_ticket_channel(interaction, self.values[0], topics[self.values[0]])


class MainTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(MainTicketSelect())


# ---------------------- PANNELLO MINECRAFT ----------------------
class MinecraftPanelView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="⛏️ Supporto Minecraft", style=discord.ButtonStyle.green, custom_id="minecraft_ticket")
    async def minecraft_button(self, interaction: discord.Interaction, button: Button):
        await create_ticket_channel(interaction, "minecraft", "Supporto Minecraft")


# ---------------------- PANNELLO SPONSOR ----------------------
class SponsorPanelView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="💸 Richiedi sponsor", style=discord.ButtonStyle.green, custom_id="sponsor_ticket")
    async def sponsor_button(self, interaction: discord.Interaction, button: Button):
        await create_ticket_channel(interaction, "sponsor", "Richiesta sponsor")


# ---------------------- PANNELLO PROVINO STAFF ----------------------
class StaffPanelView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📋 Provino staff", style=discord.ButtonStyle.green, custom_id="staff_ticket")
    async def staff_button(self, interaction: discord.Interaction, button: Button):
        await create_ticket_channel(interaction, "provino", "Provino staff")


# ---------------------- COG ----------------------
class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        # Registra le view persistenti (necessario dopo un riavvio del bot)
        self.bot.add_view(TicketManageView())
        self.bot.add_view(MainTicketView())
        self.bot.add_view(MinecraftPanelView())
        self.bot.add_view(SponsorPanelView())
        self.bot.add_view(StaffPanelView())

    @commands.command(name="pannelloticket")
    @commands.has_permissions(administrator=True)
    async def pannello_ticket(self, ctx):
        embed = discord.Embed(
            title="🎫 Apri un ticket",
            description=(
                "Aprendo ticket qua puoi richiedere:\n\n"
                "❓| Aiuto Generale\n"
                "🚨| Segnala Utente\n"
                "🎁| Reclama Giveaway\n"
                "📋| Provino Staff\n"
                "🤝| Partnership\n\n"
                "⚠️ ATTENZIONE: ⚠️ Ci teniamo il diritto di chiudere i ticket aperti inutilmente"
            ),
            color=discord.Color.blurple()
        )
        await ctx.send(embed=embed, view=MainTicketView())

    @commands.command(name="pannellominecraft")
    @commands.has_permissions(administrator=True)
    async def pannello_minecraft(self, ctx):
        embed = discord.Embed(
            title="⛏️ Supporto Minecraft",
            description="Se vuoi far vedere la tua build per flexxarla oppure per far unire più gente al tuo server Java o Bedrock di Minecraft.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed, view=MinecraftPanelView())

    @commands.command(name="ticketsponsor")
    @commands.has_permissions(administrator=True)
    async def ticket_sponsor(self, ctx):
        embed = discord.Embed(
            title="💸 Richiedi sponsor",
            description="Richiedi uno sponsor a pagamento.",
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed, view=SponsorPanelView())

    @commands.command(name="pannelloprovinostaff")
    @commands.has_permissions(administrator=True)
    async def pannello_provino_staff(self, ctx):
        embed = discord.Embed(
            title="📋 Provino staff",
            description="Vieni a far parte anche tu del nostro staff!",
            color=discord.Color.purple()
        )
        await ctx.send(embed=embed, view=StaffPanelView())


async def setup(bot):
    await bot.add_cog(Tickets(bot))
