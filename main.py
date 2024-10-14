import discord
from discord.ext import commands
import asyncio
import json
from dotenv import load_dotenv
import os
import time
from commands.helpCommand import helpCommand
from commands.infoCommand import infoCommand

# Charger les variables d'environnement
load_dotenv()

# Récupérer le token
TOKEN = os.getenv('TOKEN')

# Ouvrir le fichier de configuration
with open('config.json', 'r') as cfg:
    confData = json.load(cfg)

# Initialiser les intentions du bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Activer l'intention pour voir les membres
intents.messages = True  # Activer l'intention pour écouter les messages
bot = commands.Bot(command_prefix=confData["prefix"], intents=intents)
bot.remove_command('help')

# Variables globales pour stocker les ID de message protégé et de canal de logs
protected_message_id = None
log_channel_id = None

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

# Dictionnaire pour garder une trace des messages des utilisateurs
user_messages = {}

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
                    countdown_message = await original_channel.send(f"Message protégé supprimé : {message.content or 'Embed supprimé.'}\n\nRéapparaîtra dans 11 secondes...")

                    # Compte à rebours avant de réafficher le message
                    for i in range(11, 0, -1):
                        await asyncio.sleep(1)
                        await countdown_message.edit(content=f"Message protégé supprimé : {message.content or 'Embed supprimé.'}\n\nRéapparaîtra définitivement dans {i} secondes...")

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
                await log_channel.send(f"Un message protégé a été supprimé, mais l'utilisateur responsable n'a pas pu être identifié.")

        except discord.Forbidden:
            print("Erreur : permissions insuffisantes pour accéder aux logs d'audit.")
        except discord.HTTPException as e:
            print(f"Erreur HTTP lors de l'accès aux logs d'audit : {str(e)}")
        except Exception as e:
            print(f"Erreur inattendue : {str(e)}")


@bot.command()
async def unprotect(ctx):
    global protected_message_id
    protected_message_id = None
    await ctx.send("Le message protégé a été déprotégé.")

# Commande pour protéger un message
@bot.command()
async def protect(ctx, message_id: int):
    global protected_message_id

    # Récupérer le message par ID
    try:
        message = await ctx.channel.fetch_message(message_id)
        protected_message_id = message.id
        await ctx.send(f"Le message avec l'ID {message_id} est maintenant protégé.")
    except discord.NotFound:
        await ctx.send("Message non trouvé. Assurez-vous que l'ID est correct et que le message existe.")
    except Exception as e:
        await ctx.send(f"Une erreur s'est produite : {str(e)}")

# Commande de configuration du canal de logs
@bot.command()
@commands.has_permissions(manage_guild=True)  # Vérifie si l'utilisateur a la permission de gérer le serveur
async def setup(ctx):
    global log_channel_id
    guild = ctx.guild

    # Vérifie si un canal existe déjà pour les logs
    existing_channel = discord.utils.get(guild.text_channels, name="logs-suppression")
    if existing_channel:
        await ctx.send("Le canal `logs-suppression` existe déjà.")
        log_channel_id = existing_channel.id
        return

    # Créer un canal textuel nommé "logs-suppression"
    log_channel = await guild.create_text_channel('logs-suppression')
    log_channel_id = log_channel.id

    await ctx.send(f"Le canal {log_channel.mention} a été créé pour les logs de suppression.")

    # Stocker l'ID du canal pour l'utiliser dans d'autres commandes
    with open('config.json', 'r') as f:
        config = json.load(f)

    config['log_channel_id'] = log_channel.id  # Stocker l'ID du canal

    with open('config.json', 'w') as f:
        json.dump(config, f)

    await ctx.send(f"Le canal de logs des suppressions de messages est prêt à l'emploi.")

@bot.command()
async def purge(ctx, amount: int):
    if amount < 1:
        await ctx.send(f"{ctx.author.mention} Merci de rentrer un nombre supérieur ou égal à **1**")
        return

    # Vérification des permissions
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send(f"{ctx.author.mention}, vous n'avez pas la permission de gérer (et supprimer) les messages.")
        return

    try:
        deleted = await ctx.channel.purge(limit=amount + 1)  # +1 pour supprimer le message de commande aussi
        await ctx.send(f"{ctx.author.mention} J'ai supprimé **{len(deleted) - 1}** message(s).", delete_after=5)  # Supprime le message de confirmation après 5 secondes

        await asyncio.sleep(5)  # Attendre 10 secondes

        # Optionnel : si vous voulez purger un message après 10 secondes, spécifiez le message ou la condition
        await ctx.channel.purge(limit=1)  # Cela supprimera le dernier message (dans ce cas, le message de confirmation)
    except Exception as e:
        await ctx.send(f"{ctx.author.mention} Une erreur s'est produite : {str(e)}")

@bot.command()
async def find(ctx, id: int):
    try:
        # Essayer de récupérer un membre du serveur actuel
        member = await ctx.guild.fetch_member(id)
        await ctx.send(f"Utilisateur trouvé dans ce serveur : {member.name}#{member.discriminator}")
    except discord.NotFound:
        # Si le membre n'est pas dans le serveur, essayer de récupérer les infos globales de l'utilisateur
        user = await bot.fetch_user(id)
        await ctx.send(f"Utilisateur trouvé globalement : {user.name}#{user.discriminator}")
    except discord.Forbidden:
        await ctx.send("Je n'ai pas la permission de récupérer les informations de cet utilisateur.")
    except Exception as e:
        await ctx.send(f"Erreur : {str(e)}")

@bot.command()
async def help(ctx):
    await helpCommand(ctx, confData)  # Appeler la fonction d'aide depuis le fichier séparé

@bot.command()
async def flammes(ctx):
    async with ctx.typing():
        await ctx.channel.send('Ya un mec qui vient me voir sur snap il me dit')
        await ctx.channel.send('Selem bassem vient sur snap.')
        await asyncio.sleep(3)  # Pause de 3 secondes
        await ctx.channel.send('J’y vais')
        await asyncio.sleep(2)  # Pause de 2 secondes
        await ctx.channel.send('Aldel veut que je le ressorte, vas-y je vais y aller')


@bot.command()
async def allobassem(ctx):
    async with ctx.typing():
        await asyncio.sleep(10)
    await ctx.send(f"{ctx.author.mention}  :clown: Oe c greg")

@bot.command()
async def nuke(ctx):
    await ctx.send("https://tenor.com/view/fallout76-nuke-friends-bomb-nuclear-gif-14693420697390417365")
    await ctx.send(":joy_cat: :index_pointing_at_the_viewer:")

@bot.command()
async def info(ctx, member: discord.Member = None):
    await infoCommand(ctx, bot, member)  # Appel de la fonction depuis le fichier séparé




# Fonction modifiée pour retourner également les noms des serveurs communs
async def count_common_servers(ctx, member):
    """Compter le nombre de serveurs partagés avec un utilisateur et obtenir leurs noms."""
    common_count = 0  # Compteur pour le nombre de guildes communes
    server_names = []  # Liste des noms des guildes communes

    # Parcourir toutes les guildes du bot
    for guild in bot.guilds:
        # Vérifier si le membre est présent dans la guilde
        if member in guild.members:  # Vérification directe de la présence du membre
            common_count += 1  # Incrémenter le compteur si l'utilisateur est dans la guilde
            server_names.append(guild.name)  # Ajouter le nom de la guilde à la liste

    return common_count, server_names



@bot.command()
async def serveurs(ctx, member: discord.Member = None):
    """Vérifie combien de serveurs sont partagés avec un utilisateur spécifié."""
    if member is None:
        member = ctx.author  # Si aucun utilisateur n'est mentionné, utiliser l'auteur de la commande

    common_count = 0  # Compteur pour le nombre de guildes communes
    noms = []  # Liste pour stocker les noms des guildes communes

    # Parcourir toutes les guildes du bot
    for guild in bot.guilds:
        # Vérifier si le membre est présent dans la guilde
        if member in guild.members:  # Vérification directe de la présence du membre
            common_count += 1  # Incrémenter le compteur si l'utilisateur est dans la guilde
            noms.append(guild.name)  # Ajouter le nom de la guilde à la liste

    # Formatage de la liste des noms de guildes
    nomStr = "\n".join([f"* {nom}" for nom in noms]) if noms else "Aucun serveur commun."

    # Envoyer le résultat
    await ctx.send(f"{member.mention} et le bot sont dans {common_count} serveurs : \n{nomStr}")



@bot.command()
async def emojis(ctx):
    emojis = ctx.guild.emojis  # Récupère la liste des émojis personnalisés du serveur
    if emojis:  # Vérifie s'il y a des émojis
        emoji_list = "\n".join([f"{str(emoji)} : {emoji.name} (ID: {emoji.id})" for emoji in emojis])  # Formate la liste des émojis

        # Découpe le message en morceaux de moins de 2000 caractères
        for chunk in [emoji_list[i:i + 2000] for i in range(0, len(emoji_list), 2000)]:
            await ctx.send(chunk)
    else:
        await ctx.send("Ce serveur n'a pas d'émojis personnalisés.")


# Lancer le bot
bot.run(TOKEN)
