import discord
import asyncio
import requests
import os
import random
import time  # ✅ Added this
import aiohttp  # ✅ Added for async API calls
from discord.ext import commands, tasks
from dotenv import load_dotenv

# Store bot startup time
start_time = time.time()

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_AUTH_TOKEN = os.getenv("TWITCH_AUTH_TOKEN")
TWITCH_USERNAME = os.getenv("TWITCH_USERNAME")
CHECK_INTERVAL = 300  # 5 minutes between checks

# Bot setup
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.presences = True  # ✅ Required for Discord API compliance
intents.members = True    # ✅ Required for fetching server members

bot = commands.Bot(command_prefix="!", intents=intents)

# Store latest YouTube video and live status
latest_video_id = None
is_live_youtube = False
is_live_twitch = False
api_call_counter = 0  # ✅ Added API call counter to monitor usage

# List of Valorant agents as of February 2025
valorant_agents = [
    "Brimstone", "Viper", "Omen", "Cypher", "Sova", "Sage",
    "Phoenix", "Jett", "Raze", "Breach", "Reyna", "Killjoy",
    "Skye", "Yoru", "Astra", "KAY/O", "Chamber", "Neon",
    "Fade", "Harbor", "Gekko", "Deadlock", "Tejo", "Clove",
    "Vyse", "Iso"
]

# Global game list for game management commands
games_list = []  # ✅ Stores the list of games

# Global storage for scheduled sessions and game queues
scheduled_sessions = []  # Each session is a dict with game, time, creator, and description.
game_queues = {}         # Mapping game names to lists of usernames.

# Helper function to check if a member is authorized (i.e. has role "Admin" or "Mintyy")
def is_authorized(ctx):
    allowed_roles = ["admin", "mintyy"]
    return any(role.name.lower() in allowed_roles for role in ctx.author.roles)

# Function to get channels for bot messages, even with emojis or special characters
def get_channel(guild, channel_name):
    """Finds a channel even if it has emojis or special characters."""
    for channel in guild.text_channels:
        if channel_name.lower() in channel.name.lower():
            return channel
    return None

# Function to check latest YouTube video with rate limit handling
def get_latest_youtube_video():
    global latest_video_id, api_call_counter
    if api_call_counter >= 50:
        print("⚠️ API request limit reached, skipping YouTube check.")
        return None

    try:
        url = (
            f"https://www.googleapis.com/youtube/v3/search?key={YOUTUBE_API_KEY}"
            f"&channelId={YOUTUBE_CHANNEL_ID}&order=date&part=snippet&type=video"
        )
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        api_call_counter += 1
    except requests.exceptions.RequestException as e:
        print(f"🚨 API Request Failed: {e}")
        return None

    if "items" in data and data["items"]:
        video_id = data["items"][0]["id"]["videoId"]
        if video_id != latest_video_id:
            latest_video_id = video_id
            return f"https://www.youtube.com/watch?v={video_id}"
    return None

# Revised function to check if the YouTube streamer is live using the search endpoint.
def is_youtube_live():
    global api_call_counter
    if api_call_counter >= 50:
        print("⚠️ API request limit reached, skipping YouTube live check.")
        return False

    try:
        # Using the search endpoint with eventType=live to check for live streams.
        url = (
            f"https://www.googleapis.com/youtube/v3/search?key={YOUTUBE_API_KEY}"
            f"&channelId={YOUTUBE_CHANNEL_ID}&part=snippet&type=video&eventType=live"
        )
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        api_call_counter += 1

        print(f"📡 YouTube API Live Response: {data}")

        # If there are any items, then the channel is live.
        if "items" in data and data["items"]:
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        print(f"🚨 API Request Failed: {e}")
        return False

# Function to check if Twitch streamer is live
def is_twitch_live():
    global api_call_counter
    if api_call_counter >= 50:
        print("⚠️ API request limit reached, skipping Twitch live check.")
        return False

    try:
        url = f"https://api.twitch.tv/helix/streams?user_login={TWITCH_USERNAME}"
        headers = {
            "Client-ID": TWITCH_CLIENT_ID,
            "Authorization": f"Bearer {TWITCH_AUTH_TOKEN}"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        api_call_counter += 1
    except requests.exceptions.RequestException as e:
        print(f"🚨 API Request Failed: {e}")
        return False

    return bool(data.get("data"))

# Task to check YouTube uploads and live status without spamming
@tasks.loop(seconds=CHECK_INTERVAL)
async def check_youtube():
    global is_live_youtube
    for guild in bot.guilds:
        channel = get_channel(guild, "announcements")
        if channel:
            video_url = get_latest_youtube_video()
            if video_url:
                await channel.send(f"@everyone📢 **New YouTube Video!** Watch here: {video_url}")

            live_status = is_youtube_live()

            # Notify only once when going live
            if live_status and not is_live_youtube:
                is_live_youtube = True
                await channel.send(
                    f"@everyone🔴 **MintyyGal is LIVE on YouTube!** Watch here: "
                    f"https://www.youtube.com/channel/{YOUTUBE_CHANNEL_ID}/live"
                )
            # Notify only once when going offline
            elif not live_status and is_live_youtube:
                is_live_youtube = False
                await channel.send("@everyone⚫ **MintyyGal is OFFLINE on YouTube.**")

# Task to check Twitch live status without spamming
@tasks.loop(seconds=CHECK_INTERVAL)
async def check_twitch():
    global is_live_twitch
    for guild in bot.guilds:
        channel = get_channel(guild, "stream-notifications")
        if channel:
            live_status = is_twitch_live()

            # Notify only once when going live
            if live_status and not is_live_twitch:
                is_live_twitch = True
                await channel.send(
                    f"@everyone 🔴 **{TWITCH_USERNAME} is LIVE on Twitch!** Watch here: "
                    f"https://www.twitch.tv/{TWITCH_USERNAME}"
                )
            # Notify only once when going offline
            elif not live_status and is_live_twitch:
                is_live_twitch = False
                await channel.send(f"@everyone⚫ **{TWITCH_USERNAME} is OFFLINE on Twitch.**")

# Fun Commands

@bot.command()
async def hello(ctx):
    await ctx.send("Hello! I'm MintyyBot! 🌿 and welcome to MintyyGal's Discord, "
                   "make sure to read the rules and be respectful! Have fun!")

@bot.command()
async def joke(ctx):
    jokes = [
        "Why don’t skeletons fight each other? They don’t have the guts!",
        "What do you call fake spaghetti? An impasta!",
        "Why did the coffee file a police report? It got mugged!"
    ]
    await ctx.send(random.choice(jokes))

# Command to check live status
@bot.command()
async def status(ctx):
    youtube_status = "LIVE" if is_live_youtube else "OFFLINE"
    twitch_status = "LIVE" if is_live_twitch else "OFFLINE"
    await ctx.send(f"📡 **Streaming Status**:\nYouTube: {youtube_status}\nTwitch: {twitch_status}")

# Command to randomly select a Valorant agent
@bot.command()
async def randomagent(ctx):
    selected_agent = random.choice(valorant_agents)
    await ctx.send(f"🎲 You should play as **{selected_agent}**!")

# Game list management commands

@bot.command()
async def addgame(ctx):
    # Check if the user has permission (by role name or username)
    if "mintyy" in [role.name.lower() for role in ctx.author.roles] or ctx.author.name.lower() == "mintyygal":
        await ctx.send("🎮 Please type the name of the game you want to add:")

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        try:
            game_msg = await bot.wait_for("message", timeout=30, check=check)
            game_name = game_msg.content
            games_list.append(game_name)
            await ctx.send(f"✅ **{game_name}** has been added to the game list!")
        except asyncio.TimeoutError:
            await ctx.send("⏳ Time ran out! Please try again.")
    else:
        await ctx.send("❌ You don't have permission to add games.")

@bot.command()
async def removegame(ctx):
    if "mintyy" in [role.name.lower() for role in ctx.author.roles] or ctx.author.name.lower() == "mintyygal":
        if not games_list:
            await ctx.send("⚠️ The game list is currently empty!")
            return

        await ctx.send(f"🗑️ Here is the current game list: {', '.join(games_list)}.\nPlease type the exact game name to remove:")

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        try:
            game_msg = await bot.wait_for("message", timeout=30, check=check)
            game_name = game_msg.content
            if game_name in games_list:
                games_list.remove(game_name)
                await ctx.send(f"✅ **{game_name}** has been removed from the game list!")
            else:
                await ctx.send("❌ Game not found in the list!")
        except asyncio.TimeoutError:
            await ctx.send("⏳ Time ran out! Please try again.")
    else:
        await ctx.send("❌ You don't have permission to remove games.")

@bot.command()
async def choosegame(ctx):
    if games_list:
        chosen_game = random.choice(games_list)
        await ctx.send(f"🎮 You should play **{chosen_game}**!")
    else:
        await ctx.send("⚠️ The game list is empty! Add some games first using !addgame.")

@bot.command(name="list")
async def list_games(ctx):
    if "mintyy" in [role.name.lower() for role in ctx.author.roles] or ctx.author.name.lower() == "mintyygal":
        if games_list:
            await ctx.send(f"📜 Current game list: {', '.join(games_list)}")
        else:
            await ctx.send("⚠️ The game list is empty!")
    else:
        await ctx.send("❌ You don't have permission to view the game list.")

# New Commands for Gaming Sessions and Player Queues

@bot.command()
async def schedule(ctx):
    """Schedule a gaming session. (Restricted to Admin/Mintyy roles)"""
    if not is_authorized(ctx):
        await ctx.send("❌ You don't have permission to schedule sessions.")
        return

    await ctx.send("🎮 Let's schedule a gaming session! What game do you want to play?")
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    
    try:
        game_msg = await bot.wait_for("message", timeout=30, check=check)
        game_name = game_msg.content
        
        await ctx.send("⏰ What time is the session? (e.g., 2025-02-15 20:00)")
        time_msg = await bot.wait_for("message", timeout=30, check=check)
        session_time = time_msg.content
        
        await ctx.send("📝 (Optional) Enter a description for the session, or type 'skip'.")
        desc_msg = await bot.wait_for("message", timeout=30, check=check)
        description = desc_msg.content if desc_msg.content.lower() != 'skip' else ""
        
        session = {
            "game": game_name,
            "time": session_time,
            "creator": ctx.author.name,
            "description": description
        }
        scheduled_sessions.append(session)
        await ctx.send(f"✅ Gaming session for **{game_name}** scheduled at **{session_time}** by **{ctx.author.name}**.")
    except asyncio.TimeoutError:
        await ctx.send("⏳ Time ran out! Please try scheduling again.")

@bot.command()
async def sessions(ctx):
    """List all scheduled gaming sessions."""
    if scheduled_sessions:
        message = "📅 **Scheduled Gaming Sessions:**\n"
        for idx, session in enumerate(scheduled_sessions, start=1):
            message += f"{idx}. **{session['game']}** at **{session['time']}** by **{session['creator']}**"
            if session['description']:
                message += f" - {session['description']}"
            message += "\n"
        await ctx.send(message)
    else:
        await ctx.send("⚠️ No gaming sessions scheduled.")

@bot.command()
async def joinqueue(ctx, *, game: str = None):
    """Join the queue for a game session."""
    if not game:
        await ctx.send("❌ Please specify a game name. Usage: `!joinqueue <game>`")
        return
    game = game.strip()
    queue = game_queues.setdefault(game, [])
    if ctx.author.name in queue:
        await ctx.send("⚠️ You are already in the queue for this game!")
    else:
        queue.append(ctx.author.name)
        await ctx.send(f"✅ {ctx.author.name} has joined the queue for **{game}**.")

@bot.command()
async def leavequeue(ctx, *, game: str = None):
    """Leave the queue for a game session."""
    if not game:
        await ctx.send("❌ Please specify a game name. Usage: `!leavequeue <game>`")
        return
    game = game.strip()
    queue = game_queues.get(game, [])
    if ctx.author.name in queue:
        queue.remove(ctx.author.name)
        await ctx.send(f"✅ {ctx.author.name} has left the queue for **{game}**.")
    else:
        await ctx.send("⚠️ You are not in the queue for that game.")

@bot.command()
async def queue(ctx, *, game: str = None):
    """Display the queue for a specific game."""
    if not game:
        await ctx.send("❌ Please specify a game name. Usage: `!queue <game>`")
        return
    game = game.strip()
    queue = game_queues.get(game, [])
    if queue:
        await ctx.send(f"🎮 **Queue for {game}:** " + ", ".join(queue))
    else:
        await ctx.send(f"⚠️ There is no queue for **{game}** currently.")

# New command for authorized roles to remove someone from a game queue.
@bot.command()
async def removefromqueue(ctx, *, args: str = None):
    """
    Remove a user from a game queue. (Restricted to Admin/Mintyy roles)
    Usage: !removefromqueue <game> @member
    """
    if not is_authorized(ctx):
        await ctx.send("❌ You don't have permission to remove people from queues.")
        return
    if not args:
        await ctx.send("❌ Please specify a game name and a user mention. Usage: `!removefromqueue <game> @member`")
        return

    # Split the args: the game name and the member mention.
    parts = args.split()
    if len(parts) < 2:
        await ctx.send("❌ Please specify both a game and a user. Usage: `!removefromqueue <game> @member`")
        return

    game = parts[0]
    # Try to extract the mentioned member.
    if ctx.message.mentions:
        member = ctx.message.mentions[0]
    else:
        await ctx.send("❌ Please mention the user you want to remove from the queue.")
        return

    queue = game_queues.get(game, [])
    if member.name in queue:
        queue.remove(member.name)
        await ctx.send(f"✅ {member.name} has been removed from the queue for **{game}**.")
    else:
        await ctx.send(f"⚠️ {member.name} is not in the queue for **{game}**.")

# Bot Ready Event
@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online!")
    await asyncio.sleep(10)
    check_youtube.start()
    check_twitch.start()

# Run the bot
bot.run(TOKEN)
