import discord

async def protectCommand(ctx, message_id: int, bot):
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


async def unprotectCommand(ctx, bot):
    global protected_message_id
    protected_message_id = None
    await ctx.send("Le message protégé a été déprotégé.")