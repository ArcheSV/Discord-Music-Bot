import discord
from discord.ext import commands, tasks
from discord.ui import Button, View, Select
import yt_dlp as youtube_dl
import asyncio

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

# YT-DLP 
ytdl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'noplaylist': True,
}
ytdl = youtube_dl.YoutubeDL(ytdl_opts)

# Song class
class Song:
    def __init__(self, title, url, audio):
        self.title = title
        self.url = url
        self.audio = audio

# MusicPlayer class
class MusicPlayer:
    def __init__(self):
        self.queue = []
        self.current = None
        self.volume = 1.0

    async def play_next(self, ctx):
        if self.queue:
            self.current = self.queue.pop(0)
            ffmpeg_options = f"-filter:a volume={self.volume}"
            ctx.voice_client.play(
                self.current.audio,
                after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), bot.loop).result()
            )
            await send_controls(ctx, f"🎵 Reproduciendo ahora: **{self.current.title}**")
        else:
            self.current = None
            await ctx.voice_client.disconnect()

music_player = MusicPlayer()

# Download YT songs
async def download_audio(url):
    data = ytdl.extract_info(url, download=False)
    audio = discord.FFmpegPCMAudio(data['url'], options=f"-filter:a volume={music_player.volume}")
    return Song(title=data['title'], url=url, audio=audio)

# Buttons
async def send_controls(ctx, message):
    pause_button = Button(label="⏸ Pausar", style=discord.ButtonStyle.danger)
    resume_button = Button(label="▶️ Reanudar", style=discord.ButtonStyle.success)
    skip_button = Button(label="⏭ Siguiente", style=discord.ButtonStyle.primary)
    stop_button = Button(label="⏹ Detener", style=discord.ButtonStyle.danger)

    view = View()
    view.add_item(pause_button)
    view.add_item(resume_button)
    view.add_item(skip_button)
    view.add_item(stop_button)

    async def pause_callback(interaction):
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await interaction.response.send_message("⏸ Canción pausada.")

    async def resume_callback(interaction):
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await interaction.response.send_message("▶️ Canción reanudada.")

    async def skip_callback(interaction):
        await music_player.play_next(ctx)
        await interaction.response.send_message("⏭ Reproduciendo la siguiente canción.")

    async def stop_callback(interaction):
        music_player.queue.clear()
        await ctx.voice_client.disconnect()
        await interaction.response.send_message("⏹ Bot desconectado y cola vaciada.")

    pause_button.callback = pause_callback
    resume_button.callback = resume_callback
    skip_button.callback = skip_callback
    stop_button.callback = stop_callback

    await ctx.send(message, view=view)

# Play songs from a URL
@bot.command(name="play")
async def play(ctx, *, url: str):
    if not ctx.author.voice:
        await ctx.send("¡Debes estar en un canal de voz para usar este comando!")
        return

    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()

    song = await download_audio(url)
    music_player.queue.append(song)

    if ctx.voice_client.is_playing():
        await ctx.send(f"🎶 **{song.title}** ha sido añadida a la cola.")
    else:
        await music_player.play_next(ctx)

# Search songs command
@bot.command(name="search")
async def search(ctx, *, query: str):
    if not ctx.author.voice:
        await ctx.send("¡Debes estar en un canal de voz para usar este comando!")
        return

    async with ctx.typing():  # Mostrar que el bot está escribiendo mientras busca
        results = ytdl.extract_info(f"ytsearch5:{query}", download=False)["entries"]

    if not results:
        await ctx.send("No se encontraron resultados para tu búsqueda.")
        return

    options = [result["title"] for result in results]
    urls = [result["webpage_url"] for result in results]

    select = Select(placeholder="Selecciona una canción...", options=[
        discord.SelectOption(label=title[:100], value=url) for title, url in zip(options, urls)
    ])

    async def select_callback(interaction):
        url = interaction.data["values"][0]
        await interaction.response.send_message(f"Seleccionaste: {url}")
        await play(ctx, url=url)

    select.callback = select_callback

    view = View()
    view.add_item(select)
    await ctx.send("🎵 Aquí tienes los resultados:", view=view)

# Detect Inactivity
@tasks.loop(seconds=30)
async def check_inactivity():
    for vc in bot.voice_clients:
        if not vc.is_playing() and not vc.is_paused():
            await vc.disconnect()

@bot.event
async def on_ready():
    print(f"Conectado como {bot.user}")
    if not check_inactivity.is_running():
        check_inactivity.start()

bot.run("Put ur token here")
