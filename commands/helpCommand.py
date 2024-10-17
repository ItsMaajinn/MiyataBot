import discord
import asyncio
import os
from discord.ui import Select, View

async def helpCommand(ctx, confData):
    msg = await ctx.send(f"{ctx.author.mention}, où veux-tu recevoir les commandes ? 1️⃣ Sur le serveur 2️⃣ En MP ")

    # Ajoute les réactions au message
    await msg.add_reaction('1️⃣')
    await msg.add_reaction('2️⃣')

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ['1️⃣', '2️⃣']

    try:
        reaction, user = await ctx.bot.wait_for('reaction_add', timeout=60.0, check=check)

        # Charger et attacher les images
        files = []  # Liste pour stocker les fichiers à envoyer
        base_path = os.path.dirname(__file__)  # Répertoire actuel du fichier Python
        try:
            # Charger la première image
            picture1_path = os.path.join(base_path, "../assets/pp.jpg")
            with open(picture1_path, "rb") as f:
                picture1 = discord.File(f, filename="pp.jpg")
                files.append(picture1)  # Ajouter le fichier à la liste

            # Charger la seconde image
            picture2_path = os.path.join(base_path, "../assets/pp2.jpg")
            with open(picture2_path, "rb") as f:
                picture2 = discord.File(f, filename="pp2.jpg")
                files.append(picture2)  # Ajouter le fichier à la liste

        except FileNotFoundError as e:
            await ctx.send(f"Erreur : {str(e)}. Assurez-vous que les fichiers existent dans le dossier `assets`.")
            return

        # Fonction de callback pour gérer le changement de catégorie
        async def category_select_callback(interaction):
            if interaction.user == ctx.author:
                embed = discord.Embed(
                    title=f"Commandes - {select.values[0]}",
                    description=f"Mon préfix est : **{confData['prefix']}**",
                    color=discord.Color.red()
                )
                if select.values[0] == "Commandes Fun":
                    embed.add_field(name="🎉 | flammes", value="Viens on fait les flammes", inline=False)
                    embed.add_field(name="🎉 | allobassem", value="Radio Hlib :on: :top:", inline=False)
                elif select.values[0] == "Commandes Admin":
                    embed.add_field(name="🛠️ | info", value="On chope tes infos en bien gars", inline=False)
                    embed.add_field(name="🛠️ | serveurs", value="Oe ça vient d'où ?", inline=False)
                elif select.values[0] == "Commandes Utilitaires":
                    embed.add_field(name="🔧 | emojis", value="Les emojis custom du serv", inline=False)
                    embed.add_field(name="🔧 | find", value="L'ID a qui :interrobang:", inline=False)

                # Ajout des images à l'embed
                embed.set_thumbnail(url="attachment://pp.jpg")  # Image 1 dans thumbnail
                embed.set_image(url="attachment://pp2.jpg")     # Image 2 comme image principale

                embed.set_footer(text="Allo Selem")
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)

                # Mettre à jour le message avec l'embed mis à jour sans pré-sélection dans le menu déroulant
                await interaction.response.edit_message(embed=embed, view=view)

        # Créez le menu déroulant pour les catégories
        select = Select(
            placeholder="Choisissez une catégorie de commandes...",
            options=[
                discord.SelectOption(label="Commandes Fun", description="Les commandes amusantes", emoji="🎉"),
                discord.SelectOption(label="Commandes Admin", description="Les commandes pour les admins", emoji="🛠️"),
                discord.SelectOption(label="Commandes Utilitaires", description="Commandes pour utilitaires", emoji="🔧")
            ]
        )
        select.callback = category_select_callback

        # Créez la vue et ajoutez le sélecteur
        view = View()
        view.add_item(select)

        # Envoi initial de l'embed avec la catégorie par défaut "Utilitaires"
        embed = discord.Embed(
            title="Commandes - Commandes Utilitaires",
            description=f"Mon préfix est : **{confData['prefix']}**",
            color=discord.Color.red()
        )
        embed.add_field(name="🔧 | emojis", value="Les emojis custom du serv", inline=False)
        embed.add_field(name="🔧 | find", value="L'ID a qui :interrobang:", inline=False)

        # Ajout des images à l'embed
        embed.set_thumbnail(url="attachment://pp.jpg")  # Image 1 dans thumbnail
        embed.set_image(url="attachment://pp2.jpg")     # Image 2 comme image principale

        embed.set_footer(text="Allo Selem")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)

        if str(reaction.emoji) == '1️⃣':
            await ctx.send(files=files, embed=embed, view=view)  # Envoi sur le serveur
        elif str(reaction.emoji) == '2️⃣':
            await ctx.author.send(files=files, embed=embed, view=view)  # Envoi en MP
            await ctx.send(f"{ctx.author.mention}, je t'ai envoyé un message privé !")

    except asyncio.TimeoutError:
        await ctx.send(f"{ctx.author.mention}, tu n'as pas répondu à temps ! 😢")
