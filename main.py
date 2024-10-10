import discord
from discord.ext import commands
import asyncio
import json
from helpCommand import helpCommand  # Assurez-vous d'importer la fonction correctement
import random
from dotenv import load_dotenv
import os

load_dotenv()

# Récupérer le token
TOKEN = os.getenv('TOKEN')


# Ouvrir les fichiers de configuration


with open('config.json', 'r') as cfg:
    confData = json.load(cfg)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Activer l'intention pour voir les membres
bot = commands.Bot(command_prefix=confData["prefix"], intents=intents)
bot.remove_command('help')

# Events
@bot.event
async def on_ready():
    activity = discord.Streaming(
        name="La Radio de Bassmoss",
        url="https://www.twitch.tv/ItsMaajinn"  # Remplace par un vrai lien vers un flux en direct
    )
    await bot.change_presence(activity=activity)
    print(f'Logged in as {bot.user}')
    print(f"\nprefix => {confData['prefix']}")


import time

# Dictionnaire pour garder une trace des messages des utilisateurs
user_messages = {}

@bot.event
async def on_message(message):
    user_id = message.author.id
    current_time = time.time()

    # Si l'utilisateur a déjà envoyé des messages récemment
    if user_id in user_messages:
        last_message_time = user_messages[user_id]

        # Si le message a été envoyé moins de 2 secondes après le dernier message
        if current_time - last_message_time < 2:
            return  # Empêche le traitement du message par d'autres commandes

    # Mettre à jour la dernière fois qu'un message a été envoyé par cet utilisateur
    user_messages[user_id] = current_time

    await bot.process_commands(message)  # Continue à traiter les commandes après vérification


# Fonction pour formater la différence de temps
def format_time_difference(days):
    if days < 1:
        return f"{int(days * 24)} heures"
    elif days < 365:
        return f"{int(days)} jours"
    else:
        return f"{int(days // 365)} ans"

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

@bot.command()
async def nuke(ctx):
    await ctx.send("https://tenor.com/view/fallout76-nuke-friends-bomb-nuclear-gif-14693420697390417365")
    await ctx.send(":joy_cat: :index_pointing_at_the_viewer:")

@bot.command()
async def info(ctx, member: discord.Member = None):
    if member is None:
        # Si aucun utilisateur n'est mentionné, utiliser l'auteur de la commande
        member = ctx.author
    else:
        # Vérifier si member est un ID (int) ou une mention
        if isinstance(member, int):
            try:
                member = await ctx.guild.fetch_member(member)  # Essayer de récupérer le membre par ID
            except discord.NotFound:
                await ctx.send("Cet ID ne correspond à aucun membre de ce serveur.")
                return

    # Récupérer l'avatar de l'utilisateur
    avatar_url = member.avatar.url if member.avatar else "Aucun avatar"

    # Récupérer les informations complètes de l'utilisateur
    user = await bot.fetch_user(member.id)

    # Récupérer la bannière de l'utilisateur si disponible
    banner_url = user.banner.url if user.banner else None

    # Informations supplémentaires
    creation_date = member.created_at  # Date de création du compte
    account_age = (ctx.message.created_at - creation_date).days  # Âge du compte en jours
    join_date = member.joined_at  # Date d'arrivée sur le serveur
    server_age = (ctx.message.created_at - join_date).days if join_date else None  # Âge sur le serveur
    display_name = member.display_name  # Pseudo d'affichage
    real_name = member.name  # Vrai pseudo

    # Créer un embed avec l'avatar
    embed = discord.Embed(title=f"Informations sur {member}", color=discord.Color.from_rgb(0, 0, 0))
    embed.set_thumbnail(url=avatar_url)  # Ajouter l'avatar en miniature

    # Ajouter les informations à l'embed
    embed.add_field(name="Avatar", value=f"[Lien de l'avatar]({avatar_url})", inline=True)
    embed.add_field(name="Date de création du compte", value=creation_date.strftime("%d/%m/%Y à %H:%M:%S"), inline=False)
    embed.add_field(name="Âge du compte", value=format_time_difference(account_age), inline=False)
    embed.add_field(name="Date d'arrivée sur le serveur", value=join_date.strftime("%d/%m/%Y à %H:%M:%S") if join_date else "Inconnu", inline=False)
    embed.add_field(name="Âge sur le serveur", value=format_time_difference(server_age) if server_age else "Inconnu", inline=False)
    embed.add_field(name="Pseudo d'affichage", value=display_name, inline=False)
    embed.add_field(name="Vrai pseudo", value=real_name, inline=False)

    # Calculer le nombre de serveurs communs et obtenir les noms des serveurs
    common_count, server_names = await count_common_servers(ctx, member)

    # Ajouter les serveurs communs à l'embed
    embed.add_field(name="Serveur(s) en commun", value=f"**{common_count}**", inline=True)
    embed.add_field(name="Liste des serveurs", value="\n".join([f"* {server}" for server in server_names]) if server_names else "Aucun serveur commun", inline=True)

    # Si l'utilisateur a une bannière, l'ajouter à l'embed
    if banner_url:
        embed.set_image(url=banner_url)  # Afficher la bannière directement dans l'embed
        embed.add_field(name="Bannière", value=f"[Lien de la bannière]({banner_url})", inline=True)

    # Envoyer l'embed
    await ctx.send(embed=embed)


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
        emoji_list = "\n".join([f"{str(emoji)} : `{emoji.name}` (ID: `{emoji.id}`)" for emoji in emojis])  # Formate la liste des émojis

        # Découpe le message en morceaux de moins de 2000 caractères
        for chunk in [emoji_list[i:i + 2000] for i in range(0, len(emoji_list), 2000)]:
            await ctx.send(chunk)
    else:
        await ctx.send("Ce serveur n'a pas d'émojis personnalisés.")


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




bot.run(TOKEN)
