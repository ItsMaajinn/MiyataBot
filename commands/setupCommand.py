import discord
import json


log_channel_id = None


async def setupCommand(ctx, bot):
    global log_channel_id
    guild = ctx.guild

    # Vérifie si un canal existe déjà pour les logs
    if log_channel_id is not None:
        log_channel = bot.get_channel(log_channel_id)
        if log_channel:
            await ctx.send(f"`Le channel de logs`  {log_channel.mention}  `existe déjà.`")
            return

    # Créer un canal textuel nommé "logs-suppression"
    log_channel = await guild.create_text_channel('logs')
    log_channel_id = log_channel.id

    await ctx.send(f"`Le channel de logs`  {log_channel.mention}  `a été créé pour les logs de suppression.`")

    # Stocker l'ID du canal pour l'utiliser dans d'autres commandes
    with open('config.json', 'r') as f:
        config = json.load(f)

    config['log_channel_id'] = log_channel.id  # Stocker l'ID du canal

    with open('config.json', 'w') as f:
        json.dump(config, f)