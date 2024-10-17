import discord
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

load_dotenv()

# Configurer les informations d'authentification Spotify
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = 'https://annually-comic-eagle.ngrok-free.app/callback'
SCOPE = "user-library-read user-read-playback-state user-modify-playback-state playlist-modify-public"

sp_oauth = SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                        client_secret=SPOTIFY_CLIENT_SECRET,
                        redirect_uri=REDIRECT_URI,
                        scope=SCOPE)

user_tokens = {}

async def linkspotifyCommand(ctx):
    auth_url = sp_oauth.get_authorize_url()
    await ctx.author.send(f"Pour lier ton compte Spotify, clique sur ce lien : {auth_url}\n"
                          "Après avoir autorisé l'accès, copie le code de la redirection affiché sur le site et envoie-le ici.")


async def spotifycodeCommand(ctx, code: str):
    try:
        token_info = sp_oauth.get_access_token(code)
        user_id = ctx.author.id
        user_tokens[user_id] = token_info  # Stocker le token pour l'utilisateur
        await ctx.send("Ton compte Spotify a été lié avec succès !")
    except Exception as e:
        await ctx.send(f"Erreur lors de la liaison du compte Spotify : {str(e)}")


async def findspotifyCommand(ctx, *, query):
    try:
        # Initialisation de Spotify avec les credentials de l'application
        client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
        spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        # Rechercher une chanson sur Spotify
        results = spotify.search(q=query, limit=1, type='track')

        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            song_url = track['external_urls']['spotify']
            await ctx.send(f"Voici la chanson que tu as recherchée : {song_url}")
        else:
            await ctx.send("Aucun résultat trouvé.")
    except Exception as e:
        await ctx.send(f"Une erreur s'est produite lors de la recherche : {str(e)}")