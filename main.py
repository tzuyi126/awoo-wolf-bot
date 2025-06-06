import discord
from discord.ext import commands
import logging
from collections import Counter

from load_env_var import EnvConfig
from game import Game
from methods import check_if_game_exists, dm_player_role, check_game_over
from actions import flow_action
from discordui.game_control import NewGameView

# Load environment variables
envConfig = EnvConfig()

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.active_game_channels = {}


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
    messages = [
        "AWOOOOO!",
        "Welcome!",
        "I'm Awoo, your Werewolf game master.",
        "This is a werewolf game on Discord!",
        "Type `!commands` to see what you can do.",
        "Thanks for playing!",
    ]

    for msg in messages:
        await ctx.send(msg)


@bot.command()
async def commands(ctx):
    help_text = (
        "AWOOOOO!\n"
        "Here are the commands you can use:\n"
        "`!new` - Start a new game.\n"
        "`!list` - List all players and all roles in the current game.\n"
        "`!check` - Check your role in the game. Awoo wolf will send you a DM with your role and abilities.\n"
        "`!night` - Start the night phase of the game.\n"
        "`!end` - End the current game.\n"
    )
    await ctx.send(help_text)


@bot.command()
async def new(ctx):
    # Prevent multiple games in the same channel
    if check_if_game_exists(bot, ctx.channel.id):
        await ctx.reply("A game is already being set up in this channel.")
        return

    if not hasattr(bot, "active_game_channels"):
        bot.active_game_channels = {}

    bot.active_game_channels[ctx.channel.id] = Game(ctx.channel.id)

    embed = discord.Embed(
        title="AWOO WEREWOLF - New Game Created!",
        description="A new game has been created!\nCome join the deception and mystery. Can you survive the night?",
        color=discord.Color.dark_red(),
    )

    view = NewGameView(bot, ctx.channel.id)

    await ctx.send(embed=embed, view=view)


@bot.command()
async def list(ctx):
    if not check_if_game_exists(bot, ctx.channel.id):
        await ctx.reply(
            "No game is currently active in this channel. Use `!new` to create a new game."
        )
        return

    game = bot.active_game_channels[ctx.channel.id]

    if game.num_players > 0:
        msg = (
            f"A total of `{game.num_players}` player(s) in the game:\n"
            f"{chr(10).join([player.user.mention for player in game.players.values()])}"
        )

        if game.roles:
            role_counts = Counter(game.roles)
            roles_str = ", ".join(
                [
                    f"{role} x {count}" if count > 1 else f"{role}"
                    for role, count in role_counts.items()
                ]
            )
            msg += f"\nRoles for this game: {roles_str}"

        await ctx.reply(msg)
    else:
        await ctx.reply("No players have joined the game yet.")


@bot.command()
async def check(ctx):
    if not check_if_game_exists(bot, ctx.channel.id):
        await ctx.reply(
            "No game is currently active in this channel. Use `!new` to create a new game."
        )
        return

    game = bot.active_game_channels[ctx.channel.id]

    if ctx.author.id in game.players:
        player = game.players[ctx.author.id]

        if player.character:
            await dm_player_role(ctx, player, game.wolves)
        else:
            await ctx.reply(
                "The game has not started yet. Please wait until the game starts."
            )
    else:
        await ctx.reply("You are not part of the current game.")


@bot.command()
async def night(ctx):
    if not check_if_game_exists(bot, ctx.channel.id):
        await ctx.reply(
            "No game is currently active in this channel. Use `!new` to create a new game."
        )
        return
    
    game = bot.active_game_channels[ctx.channel.id]

    if not game.is_day():
        await ctx.reply("Patience. It's not yet time for nightfall.")
        return

    await flow_action.start_night_phase(bot, ctx, game)


@bot.command()
async def end(ctx):
    if not check_if_game_exists(bot, ctx.channel.id):
        await ctx.reply("No game is currently active in this channel.")
        return

    await check_game_over(bot, ctx.channel, bot.active_game_channels[ctx.channel.id])
    del bot.active_game_channels[ctx.channel.id]
    await ctx.reply("The game has ended.")


bot.run(token=envConfig.DISCORD_TOKEN, log_handler=handler, log_level=logging.DEBUG)
