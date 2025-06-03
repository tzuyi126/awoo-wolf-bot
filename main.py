import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

from game import start_game

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logging in as {bot.user.name}!')

@bot.event
async def on_member_join(member):
    await member.send(f'Welcome to the server, {member.name}!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # Call default command in on_message method
    await bot.process_commands(message)

@bot.command()
async def start(ctx):
    # Prevent multiple games in the same channel
    if hasattr(bot, "active_game_channels") and ctx.channel.id in bot.active_game_channels:
        await ctx.reply("A game is already being set up in this channel.")
        return
    if not hasattr(bot, "active_game_channels"):
        bot.active_game_channels = set()
    bot.active_game_channels.add(ctx.channel.id)

    await ctx.reply("Game is starting! Type `!join` to join the game.")
    bot.players = set()

    try:
        while True:
            try:
                join_msg = await bot.wait_for(
                    'message',
                    timeout=120.0,
                    check=lambda m: (m.content.lower() in ["!join", "!list", "!go"]) and m.channel == ctx.channel
                )

                if join_msg.content.lower() == "!join":
                    if join_msg.author not in bot.players:
                        bot.players.add(join_msg.author)
                        await join_msg.reply(f"{join_msg.author.mention} has joined the game!")
                elif join_msg.content.lower() == "!list":
                    if bot.players:
                        await join_msg.reply("Players in the game:\n" + "\n".join([player.mention for player in bot.players]))
                    else:
                        await join_msg.reply("No players have joined the game yet.")

                elif join_msg.content.lower() == "!go":
                    if len(bot.players) < 6:
                        await join_msg.reply("Not enough players joined. At least 6 players are required to start the game.")
                    else:
                        break
            except Exception:
                break
        
        if len(bot.players) < 6:
            await ctx.send("Not enough players joined. At least 6 players are required to start the game.")
            return

        await ctx.send("Game is starting now!")
        await start_game(ctx.channel.id, list(bot.players))
    finally:
        # Clean up channel from active games
        if hasattr(bot, "active_game_channels"):
            bot.active_game_channels.discard(ctx.channel.id)
        bot.players = set()
        await ctx.send("Game has ended.")

bot.run(token=token, log_handler=handler, log_level=logging.DEBUG)
