import discord
from discord.ext import commands
import asyncio
import json
from helpCommand import helpCommand  # Assurez-vous d'importer la fonction correctement
import random

# Ouvrir les fichiers de configuration
with open('keys.json', 'r') as cfg:
    data = json.load(cfg)

with open('config.json', 'r') as cfg:
    confData = json.load(cfg)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=confData["prefix"], intents=intents)
bot.remove_command('help')

# Events
@bot.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.listening, name="Let it happen")
    await bot.change_presence(activity=activity)
    print(f'Logged in as {bot.user}')
    print(confData["prefix"])

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f":x: Commande inconnue {ctx.author.mention} :joy_cat:")
    else:
        raise error

# Commandes
@bot.command()
async def help(ctx):
    await helpCommand(ctx, confData)  # Appeler la fonction d'aide depuis le fichier séparé

@bot.command()
async def flammes(ctx):
    async with ctx.typing():
        await ctx.channel.send('Ya un mec qui vient me voir sur snap il me dit')
        await ctx.channel.send('Selem bassem vient on fait les flammes')
        await ctx.channel.send('Les flammes ? Brule toi avec sale c*nnard va')

@bot.command()
async def allobassem(ctx):
    async with ctx.typing():
        await asyncio.sleep(10)
    await ctx.send(f"{ctx.author.mention}  :clown: Oe c greg")



bot.run(data["token"])
