import discord

async def findCommand(ctx, id: int, bot):
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