import discord

async def serveursCommand(ctx, bot, member: discord.Member = None):
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