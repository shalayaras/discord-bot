import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = os.getenv("MTQ4MDM5MjkxNTQ0MzI1NzQxNg.GJ_0pi.NmUlqLFQQQi02NBxqbRDXgw8mcgLwNyTU256tY")

@bot.event
async def on_ready():
    print(f"{"Qaysar.QA} is online!")

@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    if channel:
        await channel.send(f"Welcome {member.mention}!")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

bot.run("MTQ4MDM5MjkxNTQ0MzI1NzQxNg.GJ_0pi.NmUlqLFQQQi02NBxqbRDXgw8mcgLwNyTU256tY")
