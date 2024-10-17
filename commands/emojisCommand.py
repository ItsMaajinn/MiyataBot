import discord

async def emojisCommand(ctx):
    emojis = ctx.guild.emojis  # Récupère la liste des émojis personnalisés du serveur
    if emojis:  # Vérifie s'il y a des émojis
        emoji_list = "\n".join([f"{str(emoji)} : {emoji.name} (ID: {emoji.id})" for emoji in emojis])  # Formate la liste des émojis

        # Découpe le message en morceaux de moins de 2000 caractères
        for chunk in [emoji_list[i:i + 2000] for i in range(0, len(emoji_list), 2000)]:
            await ctx.send(chunk)
    else:
        await ctx.send("Ce serveur n'a pas d'émojis personnalisés.")