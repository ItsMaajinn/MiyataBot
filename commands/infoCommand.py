import discord

# Fonction pour formater la différence de temps
def format_time_difference(days):
    if days < 1:
        return f"{int(days * 24)} heures"
    elif days < 365:
        return f"{int(days)} jours"
    else:
        return f"{int(days // 365)} ans"

# Fonction pour récupérer la liste des serveurs communs
async def count_common_servers(bot, member):
    """Retourne une liste des serveurs communs entre le bot et l'utilisateur."""
    common_servers = []
    for guild in bot.guilds:
        if member in guild.members:
            common_servers.append(guild.name)
    return common_servers

# Fonction pour la commande infoCommand
async def infoCommand(ctx, bot, member: discord.Member = None):
    """Affiche les informations d'un utilisateur."""
    if member is None:
        member = ctx.author  # Si aucun utilisateur n'est mentionné, utiliser l'auteur de la commande

    try:
        # Récupérer l'avatar de l'utilisateur
        avatar_url = member.display_avatar.url  # Utilisation de display_avatar pour obtenir l'URL de l'avatar

        # Récupérer les informations complètes de l'utilisateur
        user = await bot.fetch_user(member.id)

        # Récupérer la bannière de l'utilisateur si disponible
        banner_url = user.banner.url if user.banner else None  # Vérification pour la bannière

        # Informations supplémentaires
        creation_date = member.created_at  # Date de création du compte
        account_age = (ctx.message.created_at - creation_date).days  # Âge du compte en jours
        join_date = member.joined_at  # Date d'arrivée sur le serveur
        server_age = (ctx.message.created_at - join_date).days if join_date else None  # Âge sur le serveur
        display_name = member.display_name  # Pseudo d'affichage
        real_name = member.name  # Vrai pseudo

        # Obtenir la liste des serveurs communs
        common_servers = await count_common_servers(bot, member)

        # Formater la liste des serveurs communs
        server_list_str = "\n".join([f"- {server}" for server in common_servers]) if common_servers else "Aucun serveur commun."

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
        embed.add_field(name="ID", value=member.id, inline=False)
        embed.add_field(name="Nombre de serveurs en commun", value=f"{len(common_servers)}", inline=False)
        embed.add_field(name="Serveurs communs", value=server_list_str, inline=False)  # Liste des serveurs

        # Si l'utilisateur a une bannière, l'ajouter à l'embed
        if banner_url:
            embed.set_image(url=banner_url)  # Afficher la bannière directement dans l'embed
            embed.add_field(name="Bannière", value=f"[Lien de la bannière]({banner_url})", inline=True)

        # Envoyer l'embed
        await ctx.send(embed=embed)

    except discord.NotFound:
        await ctx.send(f"Membre non trouvé. Veuillez vérifier que l'ID est correct et que l'utilisateur est dans ce serveur.")
    except discord.HTTPException as e:
        await ctx.send(f"Erreur HTTP : {str(e)}")
    except Exception as e:
        await ctx.send(f"Erreur : {str(e)}")
