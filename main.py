import os
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
from datetime import datetime, timedelta

# ======================================================
# PROFESSIONAL DISCORD BOT - SECURITY + WELCOME + MORE
# discord.py 2.x
# Install locally/Replit/Railway:
#   pip install -U discord.py
#
# IMPORTANT:
# 1) Put your bot token in environment variable: BOT_TOKEN
# 2) Replace all IDs below with your real IDs
# 3) In Discord Developer Portal > Bot enable:
#    - SERVER MEMBERS INTENT
#    - MESSAGE CONTENT INTENT
# ======================================================

TOKEN = os.getenv("MTQ4MDM5MjkxNTQ0MzI1NzQxNg.GJ_0pi.NmUlqLFQQQi02NBxqbRDXgw8mcgLwNyTU256tY")

# ===================== CONFIG =====================
GUILD_ID = 123456789012345678

WELCOME_CHANNEL_ID = 123456789012345678
GOODBYE_CHANNEL_ID = 123456789012345678
LOG_CHANNEL_ID = 123456789012345678
SUGGESTION_CHANNEL_ID = 123456789012345678
TICKET_CATEGORY_ID = 123456789012345678
VERIFY_CHANNEL_ID = 123456789012345678

AUTO_ROLE_ID = 123456789012345678
VERIFIED_ROLE_ID = 123456789012345678
STAFF_ROLE_ID = 123456789012345678
MUTED_ROLE_ID = 123456789012345678  # optional

BOT_STATUS = "Protecting your server"
WELCOME_IMAGE = None  # optional: put image url here

# ===================== INTENTS =====================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ===================== HELPERS =====================
def make_embed(title: str, description: str = "", color=discord.Color.blurple()):
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text="Professional Security Bot")
    return embed


async def send_log(guild: discord.Guild, title: str, description: str, color=discord.Color.orange()):
    channel = guild.get_channel(LOG_CHANNEL_ID)
    if channel:
        await channel.send(embed=make_embed(title, description, color))


def is_staff(member: discord.Member):
    return member.guild_permissions.administrator or any(role.id == STAFF_ROLE_ID for role in member.roles)


# ===================== VIEWS =====================
class VerifyView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.success, emoji="✅", custom_id="verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: Button):
        if not interaction.guild or not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message("This only works inside a server.", ephemeral=True)
            return

        role = interaction.guild.get_role(VERIFIED_ROLE_ID)
        if role is None:
            await interaction.response.send_message("Verified role not found. Put correct VERIFIED_ROLE_ID.", ephemeral=True)
            return

        if role in interaction.user.roles:
            await interaction.response.send_message("You are already verified.", ephemeral=True)
            return

        try:
            await interaction.user.add_roles(role, reason="User verified with button")
            await interaction.response.send_message("You are now verified. Welcome!", ephemeral=True)
            await send_log(interaction.guild, "User Verified", f"{interaction.user.mention} got verified.", discord.Color.green())
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to add that role.", ephemeral=True)


class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.primary, emoji="🎫", custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: Button):
        if not interaction.guild or not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message("This only works inside a server.", ephemeral=True)
            return

        category = interaction.guild.get_channel(TICKET_CATEGORY_ID)
        if not isinstance(category, discord.CategoryChannel):
            await interaction.response.send_message("Ticket category not found. Check TICKET_CATEGORY_ID.", ephemeral=True)
            return

        existing = discord.utils.get(interaction.guild.text_channels, name=f"ticket-{interaction.user.id}")
        if existing:
            await interaction.response.send_message(f"You already have a ticket: {existing.mention}", ephemeral=True)
            return

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, attach_files=True),
        }

        staff_role = interaction.guild.get_role(STAFF_ROLE_ID)
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_channels=True)

        channel = await interaction.guild.create_text_channel(
            name=f"ticket-{interaction.user.id}",
            category=category,
            overwrites=overwrites,
            topic=f"Ticket for {interaction.user}"
        )

        embed = make_embed(
            "Support Ticket",
            f"Welcome {interaction.user.mention}\nPlease write your problem and staff will help you soon.",
            discord.Color.green(),
        )
        await channel.send(embed=embed, view=CloseTicketView())
        await interaction.response.send_message(f"Ticket created: {channel.mention}", ephemeral=True)
        await send_log(interaction.guild, "Ticket Created", f"{interaction.user.mention} created {channel.mention}", discord.Color.green())


class CloseTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        if not interaction.guild or not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message("This only works inside a server.", ephemeral=True)
            return

        if not interaction.channel or not interaction.channel.name.startswith("ticket-"):
            await interaction.response.send_message("This is not a ticket channel.", ephemeral=True)
            return

        if not is_staff(interaction.user) and str(interaction.user.id) not in interaction.channel.name:
            await interaction.response.send_message("You cannot close this ticket.", ephemeral=True)
            return

        await interaction.response.send_message("Closing ticket in 5 seconds...")
        await send_log(interaction.guild, "Ticket Closed", f"{interaction.user.mention} closed {interaction.channel.mention}")
        await discord.utils.sleep_until(discord.utils.utcnow() + timedelta(seconds=5))
        await interaction.channel.delete(reason=f"Ticket closed by {interaction.user}")


# ===================== EVENTS =====================
@bot.event
async def on_ready():
    bot.add_view(VerifyView())
    bot.add_view(TicketView())
    bot.add_view(CloseTicketView())

    try:
        guild = discord.Object(id=GUILD_ID)
        synced = await bot.tree.sync(guild=guild)
        print(f"Synced {len(synced)} commands to guild {GUILD_ID}")
    except Exception:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} global commands")

    await bot.change_presence(activity=discord.Game(name=BOT_STATUS))
    print(f"Logged in as {bot.user} | {bot.user.id}")


@bot.event
async def on_member_join(member: discord.Member):
    auto_role = member.guild.get_role(AUTO_ROLE_ID)
    if auto_role:
        try:
            await member.add_roles(auto_role, reason="Auto role on join")
        except discord.Forbidden:
            pass

    channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        embed = make_embed(
            "Welcome",
            f"Welcome {member.mention} to **{member.guild.name}**\nPlease read the rules and verify to unlock the server.",
            discord.Color.green(),
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Member Count", value=str(member.guild.member_count), inline=True)
        embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
        if WELCOME_IMAGE:
            embed.set_image(url=WELCOME_IMAGE)
        await channel.send(embed=embed)

    try:
        await member.send(f"Welcome to {member.guild.name}! Please verify yourself in the server.")
    except Exception:
        pass

    await send_log(member.guild, "Member Joined", f"{member.mention} joined the server.", discord.Color.green())


@bot.event
async def on_member_remove(member: discord.Member):
    channel = member.guild.get_channel(GOODBYE_CHANNEL_ID)
    if channel:
        embed = make_embed("Goodbye", f"{member} left the server.", discord.Color.red())
        await channel.send(embed=embed)

    await send_log(member.guild, "Member Left", f"{member} left the server.", discord.Color.red())


@bot.event
async def on_message_delete(message: discord.Message):
    if not message.guild or message.author.bot:
        return

    content = message.content[:1000] if message.content else "No text"
    await send_log(
        message.guild,
        "Message Deleted",
        f"Author: {message.author.mention}\nChannel: {message.channel.mention}\nContent: {content}",
        discord.Color.orange(),
    )


@bot.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    if not before.guild or before.author.bot or before.content == after.content:
        return

    await send_log(
        before.guild,
        "Message Edited",
        f"Author: {before.author.mention}\nChannel: {before.channel.mention}\nBefore: {before.content[:500]}\nAfter: {after.content[:500]}",
        discord.Color.blurple(),
    )


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission for this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You missed a required argument.")
    elif isinstance(error, commands.CommandNotFound):
        return
    else:
        await ctx.send(f"Error: {error}")


# ===================== PREFIX COMMANDS =====================
@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")


@bot.command()
async def verify(ctx):
    role = ctx.guild.get_role(VERIFIED_ROLE_ID)
    if role is None:
        await ctx.send("Verified role not found.")
        return

    if role in ctx.author.roles:
        await ctx.send("You are already verified.")
        return

    await ctx.author.add_roles(role)
    await ctx.send("You are now verified!")


@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    deleted = await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"Deleted {len(deleted)-1} messages.")
    await send_log(ctx.guild, "Messages Cleared", f"{ctx.author.mention} deleted {len(deleted)-1} messages in {ctx.channel.mention}")
    await msg.delete(delay=3)


@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason"):
    await member.kick(reason=reason)
    await ctx.send(f"{member.mention} was kicked.")
    await send_log(ctx.guild, "Member Kicked", f"Moderator: {ctx.author.mention}\nMember: {member.mention}\nReason: {reason}", discord.Color.orange())


@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason"):
    await member.ban(reason=reason)
    await ctx.send(f"{member.mention} was banned.")
    await send_log(ctx.guild, "Member Banned", f"Moderator: {ctx.author.mention}\nMember: {member.mention}\nReason: {reason}", discord.Color.red())


@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, minutes: int, *, reason="No reason"):
    until = discord.utils.utcnow() + timedelta(minutes=minutes)
    await member.timeout(until, reason=reason)
    await ctx.send(f"{member.mention} timed out for {minutes} minute(s).")
    await send_log(ctx.guild, "Member Timed Out", f"Moderator: {ctx.author.mention}\nMember: {member.mention}\nMinutes: {minutes}\nReason: {reason}")


@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = make_embed("User Info", color=discord.Color.blurple())
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="Name", value=str(member), inline=True)
    embed.add_field(name="ID", value=str(member.id), inline=True)
    embed.add_field(name="Top Role", value=member.top_role.mention, inline=True)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S") if member.joined_at else "Unknown", inline=False)
    embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild
    embed = make_embed("Server Info")
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="Name", value=guild.name, inline=True)
    embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
    embed.add_field(name="Members", value=str(guild.member_count), inline=True)
    embed.add_field(name="Roles", value=str(len(guild.roles)), inline=True)
    embed.add_field(name="Channels", value=str(len(guild.channels)), inline=True)
    embed.add_field(name="Created", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
    await ctx.send(embed=embed)


@bot.command()
async def suggest(ctx, *, text):
    channel = ctx.guild.get_channel(SUGGESTION_CHANNEL_ID)
    if not channel:
        await ctx.send("Suggestion channel not found.")
        return

    embed = make_embed("New Suggestion", text)
    embed.add_field(name="Author", value=ctx.author.mention, inline=True)
    msg = await channel.send(embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")
    await ctx.send("Your suggestion was sent.")


@bot.command()
async def helpme(ctx):
    embed = make_embed("Bot Commands", "Main commands:")
    embed.add_field(name="General", value="!ping, !userinfo, !serverinfo, !helpme", inline=False)
    embed.add_field(name="Moderation", value="!clear, !kick, !ban, !timeout", inline=False)
    embed.add_field(name="Community", value="!verify, !suggest", inline=False)
    embed.add_field(name="Panels", value="Use slash setup commands for verify and ticket panels.", inline=False)
    await ctx.send(embed=embed)


# ===================== SLASH COMMANDS =====================
@bot.tree.command(name="setup_verify", description="Send verify panel", guild=discord.Object(id=GUILD_ID))
@app_commands.checks.has_permissions(administrator=True)
async def setup_verify(interaction: discord.Interaction):
    embed = make_embed("Verification Panel", "Click the button below to verify.")
    await interaction.channel.send(embed=embed, view=VerifyView())
    await interaction.response.send_message("Verify panel sent.", ephemeral=True)


@bot.tree.command(name="setup_tickets", description="Send ticket panel", guild=discord.Object(id=GUILD_ID))
@app_commands.checks.has_permissions(administrator=True)
async def setup_tickets(interaction: discord.Interaction):
    embed = make_embed("Support Tickets", "Click the button below to create a private ticket.")
    await interaction.channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message("Ticket panel sent.", ephemeral=True)


@bot.tree.command(name="bothelp", description="Show bot help", guild=discord.Object(id=GUILD_ID))
async def bothelp(interaction: discord.Interaction):
    embed = make_embed("Bot Systems", "This bot includes:")
    embed.add_field(name="Security", value="Logs, moderation, timeout, verify", inline=False)
    embed.add_field(name="Community", value="Welcome, goodbye, suggestions, tickets", inline=False)
    embed.add_field(name="Commands", value="Prefix commands + slash commands", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)


# ===================== RUN =====================
if __name__ == "__main__":
    if not TOKEN:
        raise ValueError("BOT_TOKEN is missing. Add it to Railway/Replit Variables.")
    bot.run(MTQ4MDM5MjkxNTQ0MzI1NzQxNg.GJ_0pi.NmUlqLFQQQi02NBxqbRDXgw8mcgLwNyTU256tY)
