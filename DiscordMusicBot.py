import os
import discord
from discord.ext import commands
import wavelink

TOKEN = os.getenv("DISCORD_TOKEN")  # رح نحطه في Render Environment

# ضع هنا بيانات Lavalink (مؤقتاً نستخدم سيرفر عام)
LAVALINK_URI = os.getenv("LAVALINK_URI", "http://lavalink.jirayu.net:2333")
LAVALINK_PASSWORD = os.getenv("LAVALINK_PASSWORD", "jirayu")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="a", intents=intents)  # prefix = a


@bot.event
async def on_ready():
    # اتصال Lavalink
    nodes = [wavelink.Node(uri=LAVALINK_URI, password=LAVALINK_PASSWORD)]
    await wavelink.Pool.connect(client=bot, nodes=nodes)
    print(f"✅ Logged in as {bot.user}")
    print("✅ Lavalink connected")


@bot.command()
async def join(ctx: commands.Context):
    if not ctx.author.voice:
        return await ctx.send("❌ ادخل روم صوتي أولاً")

    if ctx.voice_client:
        return await ctx.send("✅ أنا داخل بالفعل")

    await ctx.author.voice.channel.connect(cls=wavelink.Player)
    await ctx.send("✅ دخلت الروم")


@bot.command()
async def leave(ctx: commands.Context):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        return await ctx.send("✅ طلعت من الروم")
    await ctx.send("❌ أنا مو داخل روم")


@bot.command()
async def play(ctx: commands.Context, *, search: str):
    if not ctx.author.voice:
        return await ctx.send("❌ ادخل روم صوتي أولاً")

    player: wavelink.Player
    if not ctx.voice_client:
        player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
    else:
        player = ctx.voice_client

    # بحث يوتيوب
    track = await wavelink.YouTubeTrack.search(search, return_first=True)
    if not track:
        return await ctx.send("❌ ما لقيت شي")

    await player.play(track)
    await ctx.send(f"▶️ يشغل: **{track.title}**")


@bot.command()
async def stop(ctx: commands.Context):
    if not ctx.voice_client:
        return await ctx.send("❌ ماكو تشغيل")
    ctx.voice_client.stop()
    await ctx.send("⏹️ تم الإيقاف")


@bot.command()
async def ping(ctx: commands.Context):
    await ctx.send("🏓 Pong!")


if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is not set!")

bot.run(TOKEN)
