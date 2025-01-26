import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp
import asyncio
import requests
from discord.ui import Button, View

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

YOUTUBE_API_KEY = "YT_API KEY"

# Opciones del FFmpeg
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -ac 2 -ar 48000'

class Song:
    def __init__(self, title, url, audio):
        self.title = title
        self.url = url
        self.audio = audio

class MusicPlayer:
    def __init__(self):
        self.queue = []
        self.current = None
        self.inactivity_timeout = 30  # Tiempo de inactividad en segundos

        # Configuración de yt-dlp
        ytdl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
        }
        self.ytdl = yt_dlp.YoutubeDL(ytdl_opts)

    async def play_next(self, interaction: discord.Interaction):
        """Reproduce la siguiente canción en la cola."""
        if self.queue:
            self.current = self.queue.pop(0)
            data = self.ytdl.extract_info(self.current.url, download=False)
            audio_url = data['url']

            if interaction.guild.voice_client:
                interaction.guild.voice_client.play(
                    discord.FFmpegPCMAudio(audio_url),
                    after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(interaction), bot.loop).result()
                )
                # Enviar mensaje al canal de texto
                if interaction.channel:
                    view = create_music_controls(interaction)
                    await interaction.channel.send(f"🎵 Reproduciendo ahora: **{self.current.title}**", view=view)
        else:
            self.current = None
            await self.disconnect_after_inactivity(interaction)

    async def disconnect_after_inactivity(self, interaction: discord.Interaction):
        await asyncio.sleep(self.inactivity_timeout)
        if interaction.guild.voice_client and not interaction.guild.voice_client.is_playing():
            if interaction.channel:
                await interaction.channel.send("⏹ Bot desconectado por inactividad.")
            await interaction.guild.voice_client.disconnect()

music_player = MusicPlayer()

def search_youtube(query, max_results=5):
    params = {
        "part": "snippet",
        "q": query,
        "key": YOUTUBE_API_KEY,
        "type": "video",
        "maxResults": max_results
    }
    response = requests.get("https://www.googleapis.com/youtube/v3/search", params=params)
    data = response.json()

    results = []
    for item in data.get("items", []):
        title = item["snippet"]["title"]
        video_id = item["id"]["videoId"]
        url = f"https://www.youtube.com/watch?v={video_id}"
        results.append(Song(title=title, url=url, audio=None))
    return results

def create_music_controls(interaction: discord.Interaction):
    pause_button = Button(label="⏸ Pausar", style=discord.ButtonStyle.danger)
    resume_button = Button(label="▶️ Reanudar", style=discord.ButtonStyle.success)
    stop_button = Button(label="⏹ Detener", style=discord.ButtonStyle.danger)

    view = View()

    async def pause_callback(interaction: discord.Interaction):
        if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.pause()
            await interaction.response.send_message("⏸ Canción pausada.", ephemeral=True)

    async def resume_callback(interaction: discord.Interaction):
        if interaction.guild.voice_client and interaction.guild.voice_client.is_paused():
            interaction.guild.voice_client.resume()
            await interaction.response.send_message("▶️ Canción reanudada.", ephemeral=True)

    async def stop_callback(interaction: discord.Interaction):
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
            await interaction.response.send_message("⏹ Música detenida y bot desconectado.", ephemeral=True)

    pause_button.callback = pause_callback
    resume_button.callback = resume_callback
    stop_button.callback = stop_callback

    view.add_item(pause_button)
    view.add_item(resume_button)
    view.add_item(stop_button)

    return view

class MusicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="play", description="Reproduce una canción desde un enlace.")
    async def play(self, interaction: discord.Interaction, url: str):
        await interaction.response.defer()

        if not interaction.user.voice:
            await interaction.followup.send("¡Debes estar en un canal de voz para usar este comando!", ephemeral=True)
            return

        if interaction.guild.voice_client is None:
            await interaction.user.voice.channel.connect()

        # Obtener detalles del video
        data = music_player.ytdl.extract_info(url, download=False)
        title = data.get("title", "Audio")

        # Crear la canción con el título correcto
        song = Song(title=title, url=url, audio=None)
        music_player.queue.append(song)

        if interaction.guild.voice_client.is_playing():
            await interaction.followup.send(f"🎶 **{song.title}** ha sido añadida a la cola.")
        else:
            await music_player.play_next(interaction)

    @app_commands.command(name="search", description="Busca canciones en YouTube.")
    async def search(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()

        results = search_youtube(query)

        options = [
            discord.SelectOption(label=song.title[:100], value=song.url[:100]) for song in results
        ]

        select = discord.ui.Select(placeholder="Selecciona una canción...", options=options)

        async def select_callback(interaction: discord.Interaction):
            url = interaction.data["values"][0]
            data = music_player.ytdl.extract_info(url, download=False)
            title = data.get("title", "Audio")

            # Crear la canción con el título correcto
            song = Song(title=title, url=url, audio=None)

            if interaction.guild.voice_client is None:
                await interaction.user.voice.channel.connect()

            music_player.queue.append(song)

            if interaction.guild.voice_client.is_playing():
                if interaction.channel:
                    await interaction.channel.send(f"🎶 **{song.title}** ha sido añadida a la cola.")
            else:
                await music_player.play_next(interaction)

        select.callback = select_callback

        view = discord.ui.View()
        view.add_item(select)
        await interaction.followup.send("🎵 Aquí tienes los resultados:", view=view)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Conectado como {bot.user}")

async def setup(bot):
    await bot.add_cog(MusicCommands(bot))

bot.setup_hook = lambda: asyncio.create_task(setup(bot))
bot.run("DiscordToken")
