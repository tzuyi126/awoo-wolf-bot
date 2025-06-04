import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
from collections import Counter

from game import Game

load_dotenv(override=True)
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


@bot.command()
async def awoo(ctx):
    await ctx.send(
        "AWOOOOO!\n"
        "Welcome to the AWOO WEREWOLF game on Discord! \n"
        "Type `!commands` to see what you can do.\n"
        "This bot is developed by tzuyi126.\n"
        "Thanks for playing!\n"
    )


@bot.command()
async def commands(ctx):
    help_text = (
        "AWOOOOO! Welcome! Here are the commands you can use:\n"
        "`!new` - Start a new game.\n"
        "`!join` - Join the current game.\n"
        "`!list` - List all players and all roles in the current game.\n"
        f"`!start` - Start the game if enough players have joined (at least {os.getenv('MIN_PLAYERS')}, at most {os.getenv('MAX_PLAYERS')}).\n"
        "`!check` - Check your role in the game.\n"
        "`!end` - End the current game.\n"
    )
    await ctx.send(help_text)


def check_if_game_exists(ctx):
    return hasattr(bot, "active_game_channels") and ctx.channel.id in bot.active_game_channels.keys()


@bot.command()
async def new(ctx):
    # Prevent multiple games in the same channel
    if check_if_game_exists(ctx):
        await ctx.reply("A game is already being set up in this channel.")
        return
    
    if not hasattr(bot, "active_game_channels"):
        bot.active_game_channels = {}

    bot.active_game_channels[ctx.channel.id] = Game(ctx.channel.id)
    await ctx.reply("New game is created! Type `!join` to join the game.")


@bot.command()
async def join(ctx):
    if not check_if_game_exists(ctx):
        await ctx.reply("No game is currently active in this channel. Use `!new` to create a new game.")
        return
    
    game = bot.active_game_channels[ctx.channel.id]

    if not game.add_player(ctx.author):
        await ctx.reply(f"{ctx.author.mention}, you cannot join the game at this moment!")
        return

    await ctx.reply(f"{ctx.author.mention} has joined the game! Current players: `{game.num_players}`")


@bot.command()
async def list(ctx):
    if not check_if_game_exists(ctx):
        await ctx.reply("No game is currently active in this channel. Use `!new` to create a new game.")
        return
    
    game = bot.active_game_channels[ctx.channel.id]

    if game.num_players > 0:
        msg = (
            f"A total of `{game.num_players}` player(s) in the game:\n"
            f"{chr(10).join([player.mention for player in game.players.values()])}"
        )

        if game.roles:
            role_counts = Counter(game.roles)
            roles_str = ', '.join([f"{role} x {count}" if count > 1 else f"{role}" for role, count in role_counts.items()])
            msg += f"\nRoles for this game: {roles_str}"

        await ctx.reply(msg)
    else:
        await ctx.reply("No players have joined the game yet.")


@bot.command()
async def start(ctx):
    if not check_if_game_exists(ctx):
        await ctx.reply("No game is currently active in this channel. Use `!new` to create a new game.")
        return
    
    game = bot.active_game_channels[ctx.channel.id]

    if not game.check_start_conditions():
        await ctx.reply("Cannot start the game. Either the game is already in progress or the number of players is not sufficient.")
        return

    await ctx.send("AWOOOOO! The game is starting! Prepare yourselves!")
    game.start()

    for player in game.players.values():
        try:
            embed, file = create_embed(player, game.wolves)
            await player.user.send(embed=embed, file=file)
        except Exception:
            await ctx.send(f"Could not send DM to {player.mention}.")

    await ctx.send("Characters have been assigned and dms have been sent to players. Use `!check` to see your role.")


@bot.command()
async def check(ctx):
    if not check_if_game_exists(ctx):
        await ctx.reply("No game is currently active in this channel. Use `!new` to create a new game.")
        return
    
    game = bot.active_game_channels[ctx.channel.id]

    if ctx.author.id in game.players:
        player = game.players[ctx.author.id]

        if player.character:
            try:
                embed, file = create_embed(player, game.wolves)
                await player.user.send(embed=embed, file=file)
            except Exception:
                await ctx.send(f"Could not send DM to {player.mention}.")
        else:
            await ctx.reply("The game has not started yet. Please wait until the game starts.", ephemeral=True)
    else:
        await ctx.reply("You are not part of the current game.", ephemeral=True)


def create_embed(player, wolves):
    embed = discord.Embed(
        title=f"You are a {player.character.role}",
        description=f"{player.__str__()}",
        color=discord.Color.blue() if player.character.personality == "good" else discord.Color.red()
    )

    embed.add_field(name="Ability", value=player.character.ability, inline=False)

    embed.set_thumbnail(url=f"attachment://{os.path.basename(player.character.pic)}")

    if player.is_wolf:
        embed.add_field(name="The Wolf Pack (Only the wolves know!)", value=", ".join([wolf for wolf in wolves]), inline=False)

    file = discord.File(player.character.pic, filename=f"{os.path.basename(player.character.pic)}")

    return embed, file


@bot.command()
async def night(ctx):
    if not check_if_game_exists(ctx):
        await ctx.reply("No game is currently active in this channel. Use `!new` to create a new game.")
        return
    game = bot.active_game_channels[ctx.channel.id]

    if game.game_state != "night":
        await ctx.reply("It is not currently night time. Please wait until the night phase starts.")
        return

    # Here you would implement the logic for the night phase
    await ctx.reply("Night phase has started! Wolves, discuss and choose a player to eliminate.")


@bot.command()
async def end(ctx):
    if not check_if_game_exists(ctx):
        await ctx.reply("No game is currently active in this channel.")
        return
    
    del bot.active_game_channels[ctx.channel.id]
    await ctx.reply("The game has ended.")


bot.run(token=token, log_handler=handler, log_level=logging.DEBUG)
