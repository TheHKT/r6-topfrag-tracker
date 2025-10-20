import os
import discord
from dotenv import load_dotenv
from discord.ext import commands, tasks

from utils.matchparser import construct_message, check_for_matches

load_dotenv()

# Replace with your bot token
TOKEN = os.getenv("DISCORD_TOKEN")
ALERT_CHANNEL_ID = int(os.getenv("ALERT_CHANNEL_ID"))
USERNAME = os.getenv("R6_USERNAME")

# Intents let your bot access certain events
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Variable to store the channel where results should be sent
result_channel = None

@bot.event
async def on_ready():
    global result_channel
    result_channel = bot.get_channel(ALERT_CHANNEL_ID)
    periodic_task.start()

@tasks.loop(minutes=12)
async def periodic_task():
    """
    This task runs periodically and checks a condition
    """
    # Check if there is a new match on the page
    match_data = await check_for_matches(USERNAME)
    if(match_data is None):
        return
    
    msg = construct_message(match_data, USERNAME)
    if(msg is None):
        return

    global result_channel
    await result_channel.send(msg)

@periodic_task.before_loop
async def before_periodic_task():
    """Wait until the bot is ready before starting the task"""
    await bot.wait_until_ready()

bot.run(TOKEN)