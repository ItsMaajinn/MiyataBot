import discord

async def purgeCommand(ctx, amount: int, bot):
    if amount < 1:
        await ctx.send(f"{ctx.author.mention} Merci de rentrer un nombre supérieur ou égal à **1**")
        return

    # Vérification des permissions
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send(f"{ctx.author.mention}, vous n'avez pas la permission de gérer (et supprimer) les messages.")
        return

    try:
        deleted = await ctx.channel.purge(limit=amount + 1)  # +1 pour supprimer le message de commande aussi
        await ctx.send(f"{ctx.author.mention} J'ai supprimé **{len(deleted) - 1}** message(s).",
                       delete_after=5)  # Supprime le message de confirmation après 5 secondes
    except Exception as e:
        await ctx.send(f"{ctx.author.mention} Une erreur s'est produite : {str(e)}")