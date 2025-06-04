import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

from game import Game

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # Call default command in on_message method
    await bot.process_commands(message)


@bot.command(name="gamehelp")
async def gamehelp(ctx):
    help_text = (
        "AWOOOOO! Welcome! Here are the commands you can use:\n"
        "`!new` - Start a new game.\n"
        "`!join` - Join the current game.\n"
        "`!list` - List all players in the current game.\n"
        "`!start` - Start the game if enough players have joined (at least 6, at most 12).\n"
        "`!check` - Check your role in the game.\n"
        "`!end` - End the current game.\n"
    )
    await ctx.send(help_text)


@bot.command()
async def new(ctx):
    # Prevent multiple games in the same channel
    if hasattr(bot, "active_game_channels") and ctx.channel.id in bot.active_game_channels.keys():
        await ctx.reply("A game is already being set up in this channel.")
        return
    
    if not hasattr(bot, "active_game_channels"):
        bot.active_game_channels = {}

    bot.active_game_channels[ctx.channel.id] = Game(ctx.channel.id)
    await ctx.reply("New game is created! Type `!join` to join the game. (At least 6 players are required to start the game.)")


@bot.command()
async def join(ctx):
    if hasattr(bot, "active_game_channels") and ctx.channel.id in bot.active_game_channels.keys():
        game = bot.active_game_channels[ctx.channel.id]

        if not game.add_player(ctx.author):
            await ctx.reply(f"{ctx.author.mention}, you cannot join the game at this moment!")
            return

        await ctx.reply(f"{ctx.author.mention} has joined the game! Current players: `{game.num_players}`")
    else:
        await ctx.reply("No game is currently active in this channel. Use `!new` to create a new game.")


@bot.command()
async def list(ctx):
    if hasattr(bot, "active_game_channels") and ctx.channel.id in bot.active_game_channels.keys():
        game = bot.active_game_channels[ctx.channel.id]

        if game.num_players > 0:
            msg = (
                f"A total of `{game.num_players}` player(s) in the game:\n"
                f"{chr(10).join([player.mention for player in game.players.values()])}"
            )

            if game.roles:
                msg += f"\nRoles for this game: {', '.join(game.roles)}"

            await ctx.reply(msg)
        else:
            await ctx.reply("No players have joined the game yet.")
    else:
        await ctx.reply("No game is currently active in this channel. Use `!new` to create a new game.")


@bot.command()
async def start(ctx):
    if hasattr(bot, "active_game_channels") and ctx.channel.id in bot.active_game_channels.keys():
        game = bot.active_game_channels[ctx.channel.id]

        if not game.check_start_conditions():
            await ctx.reply("Cannot start the game. Either the game is already in progress or the number of players is not sufficient (6-12).")
            return

        await ctx.send("AWOOOOO! The game is starting! Prepare yourselves!")
        game.start()

        await ctx.send("Characters have been assigned. Use `!check` to see your role.")
    else:
        await ctx.reply("No game is currently active in this channel. Use `!new` to create a new game.")


@bot.command()
async def check(ctx):
    if hasattr(bot, "active_game_channels") and ctx.channel.id in bot.active_game_channels.keys():
        game = bot.active_game_channels[ctx.channel.id]

        if ctx.author.id in game.players:
            player = game.players[ctx.author.id]

            if player.character:
                embed = discord.Embed(
                    title=f"{player.character.role}",
                    description=f"{player.__str__()}",
                    color=discord.Color.blue() if player.character.personality == "good" else discord.Color.red()
                )

                embed.set_thumbnail(url=f"attachment://{os.path.basename(player.character.pic)}")  # fallback if file not found

                file = discord.File(player.character.pic, filename=f"{os.path.basename(player.character.pic)}")

                await ctx.reply(embed=embed, file=file, ephemeral=True)
            else:
                await ctx.reply("The game has not started yet. Please wait until the game starts.", ephemeral=True)
        else:
            await ctx.reply("You are not part of the current game.", ephemeral=True)
    else:
        await ctx.reply("No game is currently active in this channel. Use `!new` to create a new game.")


@bot.command()
async def end(ctx):
    if hasattr(bot, "active_game_channels") and ctx.channel.id in bot.active_game_channels.keys():
        del bot.active_game_channels[ctx.channel.id]
        await ctx.reply("The game has ended.")
    else:
        await ctx.reply("No game is currently active in this channel.")


bot.run(token=token, log_handler=handler, log_level=logging.DEBUG)
