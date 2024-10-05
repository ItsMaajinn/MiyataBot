# This example requires the 'message_content' intent.

import discord
from discord.ext import commands
import asyncio
import json

# Opens the file in read-only mode and assigns the contents to the variable cfg to be accessed further down
with open('keys.json', 'r') as cfg:
  # Deserialize the JSON data (essentially turning it into a Python dictionary object so we can use it in our code)
  data = json.load(cfg)

with open('config.json', 'r') as cfg:
  # Deserialize the JSON data (essentially turning it into a Python dictionary object so we can use it in our code)
  confData = json.load(cfg)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=confData["prefix"], intents=intents)
bot.remove_command('help')


# Events

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    print(confData["prefix"])


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        # Si la commande n'existe pas, envoie un message avec un emoji
        await ctx.send(f":x: Commande inconnue {ctx.author.mention} :joy_cat:")
    else:
        # Si c'est une autre erreur, la rélever pour la loguer ou la traiter autrement
        raise error


# Commandes

@bot.command()
async def allobassem(ctx):
    async with ctx.typing():
        await asyncio.sleep(30)
    await ctx.send(f"{ctx.author.mention}  :clown: Oe c greg")


@bot.command()
async def help(ctx):
    # Envoie un message initial avec une question
    msg = await ctx.send(f"{ctx.author.mention}, où veux-tu recevoir les commandes ? 1️⃣ Sur le serveur 2️⃣ En MP ")

    # Ajoute les réactions au message
    await msg.add_reaction('1️⃣')  # Réaction pour dire "Serveur"
    await msg.add_reaction('2️⃣')  # Réaction pour dire "Message privé"

    # Fonction pour vérifier que c'est bien l'auteur de la commande qui réagit et que la réaction est correcte
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ['1️⃣', '2️⃣']

    try:
        # Attend la réaction de l'utilisateur (timeout après 60 secondes)
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)

        if str(reaction.emoji) == '1️⃣':
            embed = discord.Embed(
                title="Liste des commandes | MiyataBot",
                description=f"Mon préfix est : **{confData['prefix']}**",
                color=discord.Color.red()  # Tu peux changer la couleur ici
            )

            # Ajouter des champs (nom/valeur)
            embed.add_field(name=":fire: flammes", value="Viens on fait les flammes", inline=False)
            embed.add_field(name="Champ 2", value="Voici le contenu du champ 2", inline=False)

            # Ajouter un pied de page
            embed.set_footer(text="Ceci est un pied de page")

            # Ajouter un auteur (optionnel)
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)

            # Ajouter une image ou une miniature (optionnel)
            embed.set_thumbnail(url="assets/pp.jpg")  # URL d'une image pour la miniature
            embed.set_image(url="https://via.placeholder.com/300x200")  # URL d'une image pour l'image principale

            with open("assets/pp.jpg", "rb") as f:
                picture = discord.File(f, filename="pp.jpg")
                embed.set_thumbnail(url="attachment://pp.jpg")  # Utiliser l'image attachée

            # Envoyer l'embed avec l'image attachée

            # Envoyer l'embed
            await ctx.send(file=picture, embed=embed)
        elif str(reaction.emoji) == '2️⃣':
            # Charger l'image à envoyer dans le DM
            with open("assets/pp.jpg", "rb") as f:
                picture = discord.File(f, filename="pp.jpg")

                # Créer un embed avec l'image jointe
                embed = discord.Embed(
                    title="Titre de l'embed",
                    description="Ceci est une description d'exemple pour un embed.",
                    color=discord.Color.red()
                )
                embed.set_thumbnail(url="attachment://pp.jpg")

                # Envoyer le message privé
                await ctx.author.send(file=picture, embed=embed)
                await ctx.send(f"{ctx.author.mention}, je t'ai envoyé un message privé !")

    except asyncio.TimeoutError:
        # Si l'utilisateur ne réagit pas dans les 60 secondes
        await ctx.send(f"{ctx.author.mention}, tu n'as pas répondu à temps ! 😢")


@bot.command()
async def flammes(ctx):
    async with ctx.typing():
        await ctx.channel.send('Ya un mec qui vient me voir sur snap il me dit')
        await ctx.channel.send('Selem bassem vient on fait les flammes')
        await ctx.channel.send('Les flammes ? Brule toi avec sale c*nnard va')











bot.run(data["token"])
