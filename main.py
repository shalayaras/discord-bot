import discord
from discord.ext import commands
import os

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = os.getenv("BOT_TOKEN")

WELCOME_CHANNEL = 123456789
VERIFY_ROLE = 123456789
AUTO_ROLE = 123456789

@bot.event
async def on_ready():
    print(f"{bot.user} is online!")
    await bot.change_presence(activity=discord.Game("Protecting Server"))

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL)

    role = member.guild.get_role(AUTO_ROLE)
    if role:
        await member.add_roles(role)

    embed = discord.Embed(
        title="Welcome",
        description=f"Welcome {member.mention} to {member.guild.name}",
        color=discord.Color.green()
    )

    await channel.send(embed=embed)

@bot.command($)
async def verify(ctx):
    role = ctx.guild.get_role(VERIFY_ROLE)

    if role in ctx.author.roles:
        await ctx.send("You are already verified")
        return

    await ctx.author.add_roles(role)
    await ctx.send("You are verified!")

@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong {round(bot.latency*1000)}ms")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount:int):
    await ctx.channel.purge(limit=amount+1)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member:discord.Member):
    await member.kick()

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member:discord.Member):
    await member.ban()

@bot.command()
async def server(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=guild.name,color=discord.Color.blue())
    embed.add_field(name="Members",value=guild.member_count)
    embed.add_field(name="Owner",value=guild.owner)
    await ctx.send(embed=embed)

@bot.command()
async def user(ctx, member:discord.Member=None):
    if not member:
        member = ctx.author

    embed = discord.Embed(title=member.name,color=discord.Color.blue())
    embed.add_field(name="ID",value=member.id)
    embed.add_field(name="Joined",value=member.joined_at)
    await ctx.send(embed=embed)

@bot.command()
async def suggest(ctx,*,text):
    embed = discord.Embed(
        title="Suggestion",
        description=text,
        color=discord.Color.orange()
    )

    msg = await ctx.send(embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")

bot.run("MTQ4MDM5MjkxNTQ0MzI1NzQxNg.G7rWkj.5V2UW9r3qn6oXg8-7L6b3Endac4LOBZItimuMY")
