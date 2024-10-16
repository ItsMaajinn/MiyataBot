import discord
from discord.ext import commands
import asyncio
from dotenv import load_dotenv
import os
import json
import time


# Importation des commandes personnalisées
from commands.helpCommand import helpCommand
from commands.infoCommand import infoCommand
from commands.serveursCommand import serveursCommand
from commands.emojisCommand import emojisCommand
from commands.setupCommand import setupCommand
from commands.findCommand import findCommand
from commands.purgeCommand import purgeCommand
from commands.protectCommands import protectCommand, unprotectCommand
from commands.spotifyCommands import linkspotifyCommand, spotifycodeCommand, findspotifyCommand

# Charger les variables d'environnement
load_dotenv()

# Configurer les informations d'authentification Spotify




# Charger les variables d'environnement pour Discord
TOKEN = os.getenv('TOKEN')

# Ouvrir le fichier de configuration
with open('config.json', 'r') as cfg:
    confData = json.load(cfg)

# Initialiser les intentions du bot Discord
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Activer l'intention pour voir les membres
intents.messages = True  # Activer l'intention pour écouter les messages
bot = commands.Bot(command_prefix=confData["prefix"], intents=intents)
bot.remove_command('help')  # Retirer la commande d'aide par défaut pour utiliser une personnalisée

# Variables globales pour stocker les ID de message protégé et de canal de logs
protected_message_id = None
# Dictionnaire pour garder une trace des messages des utilisateurs
user_messages = {}



# Événement de démarrage du bot
@bot.event
async def on_ready():
    activity = discord.Streaming(
        name="La Radio de Bassmoss",
        url="https://www.twitch.tv/ItsMaajinn"
    )
    await bot.change_presence(activity=activity)
    print(f'Logged in as {bot.user}')
    print(f"\nprefix => {confData['prefix']}")





@bot.event
async def on_message(message):
    user_id = message.author.id
    current_time = time.time()

    # Si l'utilisateur a déjà envoyé des messages récemment
    if user_id in user_messages:
        last_message_time = user_messages[user_id]
        if current_time - last_message_time < 2:
            return  # Empêche le traitement du message par d'autres commandes

    user_messages[user_id] = current_time
    await bot.process_commands(message)  # Continue à traiter les commandes après vérification


@bot.event
async def on_message_delete(message):
    global protected_message_id
    global log_channel_id

    if message.id == protected_message_id:
        guild = message.guild

        # Pause pour donner le temps aux logs d'audit d'être générés
        await asyncio.sleep(3)

        try:
            # Ouvrir le fichier config pour récupérer l'ID du canal de logs
            with open('config.json', 'r') as f:
                config = json.load(f)

            log_channel_id = config.get('log_channel_id')
            log_channel = bot.get_channel(log_channel_id)

            if not log_channel:
                print("Le canal de logs n'a pas été trouvé.")
                return

            # Rechercher les logs d'audit pour trouver qui a supprimé le message
            async for entry in guild.audit_logs(action=discord.AuditLogAction.message_delete, limit=5):
                if entry.target.id == message.author.id:
                    deleter = entry.user
                    # Envoyer un message dans le canal de logs
                    await log_channel.send(
                        f"Le message protégé de {message.author.mention} a été supprimé par {deleter.mention}.\n"
                        f"Contenu : {message.content or 'Embed supprimé.'}"
                    )

                    # Récupérer le canal d'origine du message
                    original_channel = message.channel
                    countdown_message = await original_channel.send(
                        f"Message protégé supprimé : {message.content or 'Embed supprimé.'}\n\nRéapparaîtra dans 11 secondes...")

                    # Compte à rebours avant de réafficher le message
                    for i in range(11, 0, -1):
                        await asyncio.sleep(1)
                        await countdown_message.edit(
                            content=f"Message protégé supprimé : {message.content or 'Embed supprimé.'}\n\nRéapparaîtra définitivement dans {i} secondes...")

                    # Réapparition du message après le compte à rebours
                    if message.embeds:  # Si le message contient un embed
                        for embed in message.embeds:
                            await original_channel.send(embed=embed)  # Réenvoyer chaque embed
                    elif message.content:  # Si le message est un texte simple
                        await original_channel.send(message.content)  # Réenvoyer le contenu du message texte
                    else:
                        await original_channel.send("Message protégé supprimé.")  # Si ni texte ni embed (très rare)
                    break
            else:
                await log_channel.send(
                    f"Un message protégé a été supprimé, mais l'utilisateur responsable n'a pas pu être identifié.")

        except discord.Forbidden:
            print("Erreur : permissions insuffisantes pour accéder aux logs d'audit.")
        except discord.HTTPException as e:
            print(f"Erreur HTTP lors de l'accès aux logs d'audit : {str(e)}")
        except Exception as e:
            print(f"Erreur inattendue : {str(e)}")


@bot.command()
async def linkspotify(ctx):
    await linkspotifyCommand(ctx)

# Commande pour recevoir le code d'autorisation et récupérer le token
@bot.command()
async def spotifycode(ctx, code: str):
    await spotifycodeCommand(ctx, code)

# Commande pour rechercher une chanson sur Spotify
@bot.command()
async def spotimusic(ctx, *, query):
    await findspotifyCommand(ctx, query=query)




# Commande pour protéger un message
@bot.command()
async def protect(ctx, message_id: int):
    await protectCommand(ctx, message_id, bot)


@bot.command()
async def unprotect(ctx):
    await unprotectCommand(ctx, bot)



# Commande de configuration du canal de logs
@bot.command()
@commands.has_permissions(manage_guild=True)
async def setup(ctx):
    await setupCommand(ctx, bot)


# Commande pour purger des messages
@bot.command()
async def purge(ctx, amount: int):
    await purgeCommand(ctx, amount, bot)


# Commande pour trouver un utilisateur
@bot.command()
async def find(ctx, id: int):
    await findCommand(ctx, id, bot)

# Commande d'aide personnalisée
@bot.command()
async def help(ctx):
    await helpCommand(ctx, confData)


# Commande "info"
@bot.command()
async def info(ctx, member: discord.Member = None):
    await infoCommand(ctx, bot, member)


# Commande "serveurs"
@bot.command()
async def serveurs(ctx, member: discord.Member = None):
    await serveursCommand(ctx, bot, member)


# Commande "emojis"
@bot.command()
async def emojis(ctx):
    await emojisCommand(ctx)


# Commande pour éteindre le bot
@bot.command()
@commands.is_owner()
async def shutdown(context):
    exit()


# -------------- Commandes Trolls --------------

# Commande personnalisée "flammes"
@bot.command()
async def flammes(ctx):
    await ctx.channel.send('Ya un mec qui vient me voir sur snap il me dit')
    await asyncio.sleep(1)
    await ctx.channel.send('Selem bassem vient on fait les flammes')
    await asyncio.sleep(1)
    await ctx.channel.send('Les flammes ? Brûle toi avec sale c*nnard va')


# Commande personnalisée "allobassem"
@bot.command()
async def allobassem(ctx):
    await asyncio.sleep(10)
    await ctx.send(f"{ctx.author.mention}  :clown: Oe c greg")


# Commande "nuke"
@bot.command()
async def nuke(ctx):
    await ctx.send("https://tenor.com/view/fallout76-nuke-friends-bomb-nuclear-gif-14693420697390417365")
    await ctx.send(":joy_cat: :index_pointing_at_the_viewer:")


# Lancer le bot
bot.run(TOKEN)