import discord
import asyncio

async def helpCommand(ctx, confData):
    msg = await ctx.send(f"{ctx.author.mention}, où veux-tu recevoir les commandes ? 1️⃣ Sur le serveur 2️⃣ En MP ")

    # Ajoute les réactions au message
    await msg.add_reaction('1️⃣')
    await msg.add_reaction('2️⃣')

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ['1️⃣', '2️⃣']

    try:
        reaction, user = await ctx.bot.wait_for('reaction_add', timeout=60.0, check=check)

        # Création de l'embed
        embed = discord.Embed(
            title="Liste des commandes | MiyataBot",
            description=f"Mon préfix est : **{confData['prefix']}**",
            color=discord.Color.red()
        )
        embed.add_field(name=":fire: | flammes", value="Viens on fait les flammes", inline=False)
        embed.add_field(name=":telephone_receiver: | allobassem", value="Radio Hlib :on: :top:", inline=False)
        embed.add_field(name=":camera_with_flash:  | info", value="On chope tes infos en bien gars", inline=False)
        embed.add_field(name=":japanese_castle:  | serveurs", value="Oe ça vient d'où ?", inline=False)
        embed.add_field(name=":nerd:  | emojis", value="Les emojis custom du serv", inline=False)
        embed.add_field(name=":spy:  | find", value="L'ID a qui :interrobang:", inline=False)
        embed.add_field(name=":grey_question: | help", value="Pour te carry", inline=False)
        embed.set_footer(text="Allo Selem")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)

        # Charger et attacher les images
        files = []  # Liste pour stocker les fichiers à envoyer
        try:
            with open("assets/pp.jpg", "rb") as f:
                picture1 = discord.File(f, filename="pp.jpg")
                embed.set_thumbnail(url="attachment://pp.jpg")
                files.append(picture1)  # Ajouter le fichier à la liste

            with open("assets/pp2.jpg", "rb") as f:
                picture2 = discord.File(f, filename="pp2.jpg")
                embed.set_image(url="attachment://pp2.jpg")
                files.append(picture2)  # Ajouter le fichier à la liste

            # Envoie l'embed avec les images attachées
            if str(reaction.emoji) == '1️⃣':
                await ctx.send(files=files, embed=embed)  # Envoi sur le serveur
            elif str(reaction.emoji) == '2️⃣':
                await ctx.author.send(files=files, embed=embed)  # Envoi en MP
                await ctx.send(f"{ctx.author.mention}, je t'ai envoyé un message privé !")

        except FileNotFoundError as e:
            await ctx.send(f"Erreur : {str(e)}. Assurez-vous que les fichiers existent dans le dossier `assets`.")

    except asyncio.TimeoutError:
        await ctx.send(f"{ctx.author.mention}, tu n'as pas répondu à temps ! 😢")


