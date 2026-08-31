import discord
from discord import app_commands
from discord.ext import commands
import data
import config


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invite_cache = {}

    async def cog_load(self):
        for guild in self.bot.guilds:
            try:
                self.invite_cache[guild.id] = await guild.invites()
            except discord.Forbidden:
                pass

    # ---------- WELCOME / GOODBYE ----------
    @commands.hybrid_command(name="setwelcome", description="Imposta il canale di benvenuto")
    @commands.has_permissions(administrator=True)
    async def setwelcome(self, ctx, channel: discord.TextChannel):
        settings = data.load("settings")
        g = settings.setdefault(str(ctx.guild.id), {})
        g["welcome_channel"] = channel.id
        data.save("settings", settings)
        await ctx.send(f"✅ Canale di benvenuto impostato su {channel.mention}")

    @commands.hybrid_command(name="setgoodbye", description="Imposta il canale di addio")
    @commands.has_permissions(administrator=True)
    async def setgoodbye(self, ctx, channel: discord.TextChannel):
        settings = data.load("settings")
        g = settings.setdefault(str(ctx.guild.id), {})
        g["goodbye_channel"] = channel.id
        data.save("settings", settings)
        await ctx.send(f"✅ Canale di addio impostato su {channel.mention}")

    @commands.hybrid_command(name="setwelcomegoodbyelogs", description="Imposta il canale log welcome/goodbye")
    @commands.has_permissions(administrator=True)
    async def setwelcomegoodbyelogs(self, ctx, channel: discord.TextChannel):
        settings = data.load("settings")
        g = settings.setdefault(str(ctx.guild.id), {})
        g["welcome_goodbye_log"] = channel.id
        data.save("settings", settings)
        await ctx.send(f"✅ Canale log welcome/goodbye impostato su {channel.mention}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        settings = data.load("settings").get(str(member.guild.id), {})
        role = member.guild.get_role(config.UNVERIFIED_ROLE)
        if role:
            try:
                await member.add_roles(role)
            except discord.Forbidden:
                pass

        channel_id = settings.get("welcome_channel")
        if channel_id:
            channel = member.guild.get_channel(channel_id)
            if channel:
                await channel.send(f"👋 Benvenuto {member.mention} su **{member.guild.name}**!")

        log_id = settings.get("welcome_goodbye_log")
        if log_id:
            log = member.guild.get_channel(log_id)
            if log:
                await log.send(f"📥 {member} è entrato nel server.")

        await self.update_invite_tracking(member)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        settings = data.load("settings").get(str(member.guild.id), {})
        channel_id = settings.get("goodbye_channel")
        if channel_id:
            channel = member.guild.get_channel(channel_id)
            if channel:
                await channel.send(f"👋 {member.mention} ha lasciato il server.")
        log_id = settings.get("welcome_goodbye_log")
        if log_id:
            log = member.guild.get_channel(log_id)
            if log:
                await log.send(f"📤 {member} ha lasciato il server.")

    # ---------- INVITES ----------
    async def update_invite_tracking(self, member):
        guild = member.guild
        try:
            new_invites = await guild.invites()
        except discord.Forbidden:
            return
        old_invites = self.invite_cache.get(guild.id, [])
        inviter = None
        for old in old_invites:
            match = next((i for i in new_invites if i.code == old.code), None)
            if match and match.uses > old.uses:
                inviter = match.inviter
                break
        self.invite_cache[guild.id] = new_invites

        if inviter:
            invites_data = data.load("invites")
            g = invites_data.setdefault(str(guild.id), {})
            u = g.setdefault(str(inviter.id), 0)
            g[str(inviter.id)] = u + 1
            data.save("invites", invites_data)

            settings = data.load("settings").get(str(guild.id), {})
            log_id = settings.get("invites_channel")
            if log_id:
                log = guild.get_channel(log_id)
                if log:
                    await log.send(f"📨 {member.mention} invitato da {inviter.mention}")

    @commands.hybrid_command(name="setinviteschannel", description="Imposta il canale log inviti")
    @commands.has_permissions(administrator=True)
    async def setinviteschannel(self, ctx, channel: discord.TextChannel):
        settings = data.load("settings")
        g = settings.setdefault(str(ctx.guild.id), {})
        g["invites_channel"] = channel.id
        data.save("settings", settings)
        await ctx.send(f"✅ Canale inviti impostato su {channel.mention}")

    @commands.hybrid_command(name="invites", description="Mostra i tuoi inviti")
    async def invites_cmd(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        invites_data = data.load("invites")
        count = invites_data.get(str(ctx.guild.id), {}).get(str(member.id), 0)
        await ctx.send(f"📨 {member.mention} ha **{count}** inviti")

    @commands.hybrid_command(name="showinvites", description="Mostra la classifica degli inviti")
    async def showinvites(self, ctx):
        invites_data = data.load("invites").get(str(ctx.guild.id), {})
        sorted_invites = sorted(invites_data.items(), key=lambda x: x[1], reverse=True)[:10]
        embed = discord.Embed(title="📨 Classifica Inviti", color=discord.Color.teal())
        desc = ""
        for i, (uid, count) in enumerate(sorted_invites, 1):
            desc += f"**{i}.** <@{uid}> — {count} inviti\n"
        embed.description = desc or "Nessun dato."
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="resetinvites", description="Resetta gli inviti di un utente")
    @commands.has_permissions(administrator=True)
    async def resetinvites(self, ctx, member: discord.Member):
        invites_data = data.load("invites")
        g = invites_data.setdefault(str(ctx.guild.id), {})
        g[str(member.id)] = 0
        data.save("invites", invites_data)
        await ctx.send(f"✅ Inviti di {member.mention} resettati")

    @commands.hybrid_command(name="resetinvitesall", description="Resetta tutti gli inviti del server")
    @commands.has_permissions(administrator=True)
    async def resetinvitesall(self, ctx):
        invites_data = data.load("invites")
        invites_data[str(ctx.guild.id)] = {}
        data.save("invites", invites_data)
        await ctx.send("✅ Tutti gli inviti sono stati resettati")

    # ---------- INVITE BOT ----------
    @commands.hybrid_command(name="invitebot", description="Ottieni il link di invito del bot")
    async def invitebot(self, ctx):
        app_info = await self.bot.application_info()
        link = discord.utils.oauth_url(app_info.id, permissions=discord.Permissions(administrator=True))
        await ctx.send(f"🔗 Invita il bot: {link}")

    # ---------- USERINFO / SERVERINFO ----------
    @commands.hybrid_command(name="userinfo", description="Mostra le info di un utente")
    async def userinfo(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(title=f"Info su {member}", color=member.color)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="ID", value=member.id)
        embed.add_field(name="Account creato", value=discord.utils.format_dt(member.created_at, "R"))
        embed.add_field(name="Entrato il", value=discord.utils.format_dt(member.joined_at, "R"))
        embed.add_field(name="Ruoli", value=", ".join(r.mention for r in member.roles[1:]) or "Nessuno", inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="serverinfo", description="Mostra le info del server")
    async def serverinfo(self, ctx):
        guild = ctx.guild
        embed = discord.Embed(title=guild.name, color=discord.Color.blue())
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.add_field(name="Membri", value=guild.member_count)
        embed.add_field(name="Creato il", value=discord.utils.format_dt(guild.created_at, "R"))
        embed.add_field(name="Proprietario", value=guild.owner.mention if guild.owner else "N/A")
        embed.add_field(name="Canali", value=len(guild.channels))
        embed.add_field(name="Ruoli", value=len(guild.roles))
        await ctx.send(embed=embed)

    # ---------- STAFF QUEST ----------
    @commands.hybrid_command(name="staffquestcreate", description="Crea le domande del provino staff")
    @commands.has_permissions(administrator=True)
    async def staffquestcreate(self, ctx, *, questions: str):
        # domande separate da "|"
        q_list = [q.strip() for q in questions.split("|") if q.strip()]
        sq = data.load("staffquest")
        sq[str(ctx.guild.id)] = q_list
        data.save("staffquest", sq)
        await ctx.send(f"✅ Salvate {len(q_list)} domande per il provino staff")

    @commands.hybrid_command(name="staffquest", description="Mostra le domande del provino staff")
    async def staffquest(self, ctx):
        sq = data.load("staffquest").get(str(ctx.guild.id), [])
        if not sq:
            return await ctx.send("❌ Nessuna domanda impostata.")
        embed = discord.Embed(title="📋 Domande Provino Staff", color=discord.Color.purple())
        embed.description = "\n".join(f"**{i+1}.** {q}" for i, q in enumerate(sq))
        await ctx.send(embed=embed)

    # ---------- VERIFICA ----------
    @commands.hybrid_command(name="verifica", description="Invia il messaggio di verifica")
    @commands.has_permissions(administrator=True)
    async def verifica(self, ctx):
        msg = await ctx.send(
            f"Per vedere il resto dei canali e goderti un'esperienza migliore del server, "
            f"reagisci qui sotto con ✅ e otterrai il ruolo <@&{config.VERIFIED_ROLE}>"
        )
        await msg.add_reaction("✅")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.emoji.name != "✅" or payload.member is None or payload.member.bot:
            return
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if message.author.id != self.bot.user.id:
            return
        if "verifica" not in message.content.lower() and "reagisci" not in message.content.lower():
            return
        role = payload.member.guild.get_role(config.VERIFIED_ROLE)
        unverified = payload.member.guild.get_role(config.UNVERIFIED_ROLE)
        if role:
            await payload.member.add_roles(role)
        if unverified and unverified in payload.member.roles:
            await payload.member.remove_roles(unverified)


async def setup(bot):
    await bot.add_cog(Utility(bot))
