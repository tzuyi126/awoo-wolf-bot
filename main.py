import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
from collections import Counter
import actions.wolves_action

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
    messages = [
        "AWOOOOO!",
        "Welcome!",
        "I'm Awoo, your Werewolf game master.",
        "This is a werewolf game on Discord!",
        "Type `!commands` to see what you can do.",
        "Thanks for playing!"
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
        "`!check` - Check your role in the game.\nAwoo wolf will send you a DM with your role and abilities.\n"
        "`!end` - End the current game.\n"
    )
    await ctx.send(help_text)


def check_if_game_exists(channel_id):
    return hasattr(bot, "active_game_channels") and channel_id in bot.active_game_channels.keys()


@bot.command()
async def new(ctx):
    # Prevent multiple games in the same channel
    if check_if_game_exists(ctx.channel.id):
        await ctx.reply("A game is already being set up in this channel.")
        return

    if not hasattr(bot, "active_game_channels"):
        bot.active_game_channels = {}

    bot.active_game_channels[ctx.channel.id] = Game(ctx.channel.id)

    embed = discord.Embed(
        title="AWOO WEREWOLF - New Game Created!",
        description="A new game has been created!\nCome join the deception and mystery. Can you survive the night?",
        color=discord.Color.red()
    )

    view = JoinGameButton(bot, ctx.channel.id)
    view.add_item(StartGameButton(bot, ctx.channel.id).children[0])

    await ctx.send(embed=embed, view=view)


class JoinGameButton(discord.ui.View):
    def __init__(self, bot, channel_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.channel_id = channel_id

    @discord.ui.button(label="Join Game", style=discord.ButtonStyle.primary, custom_id="join_game_button", emoji="🤝")
    async def join_game(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not check_if_game_exists(interaction.channel.id):
            button.disabled = True
            await interaction.response.edit_message(view=self)
            await interaction.followup.send("No game is currently active in this channel.", ephemeral=True)
            return

        game = self.bot.active_game_channels[self.channel_id]
        user = interaction.user

        if not game.add_player(user):
            await interaction.response.send_message(f"{user.mention}, you cannot (re)join the game at this moment!", ephemeral=True)
            return

        await interaction.response.send_message(f"{user.mention} has joined the game! Current players: `{game.num_players}`", ephemeral=False)


class StartGameButton(discord.ui.View):
    def __init__(self, bot, channel_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.channel_id = channel_id

    @discord.ui.button(label="Start Game", style=discord.ButtonStyle.success, custom_id="start_game_button", emoji="🚀")
    async def start_game(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not check_if_game_exists(interaction.channel.id):
            button.disabled = True
            await interaction.response.edit_message(view=self)
            await interaction.followup.send("No game is currently active in this channel. Use `!new` to create a new game.", ephemeral=True)
            return

        game = self.bot.active_game_channels[self.channel_id]

        if not game.check_start_conditions():
            await interaction.response.send_message(
                f"Cannot start the game. Either the game is already in progress or the number of players is not sufficient (at least {os.getenv('MIN_PLAYERS')}, at most {os.getenv('MAX_PLAYERS')}).",
                ephemeral=False
            )
            return

        button.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.followup.send("The game is starting! Prepare yourselves!", ephemeral=False)
        game.start()

        for player in game.players.values():
            await dm_player_role(interaction.channel, player, game.wolves)

        await interaction.channel.send(
            "💡 Suggestion: You can mute your mic during the night to avoid spoilers.\n"
            "⬇️ Whenever you are ready, press the button below to start the night.",
            view=NightButton()
        )


@bot.command()
async def list(ctx):
    if not check_if_game_exists(ctx.channel.id):
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


class NightButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="The night has fallen.", style=discord.ButtonStyle.danger, custom_id="start_night_phase", emoji="🌑")
    async def start_night(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not check_if_game_exists(interaction.channel.id):
            button.disabled = True
            await interaction.response.edit_message(view=self)
            await interaction.followup.send("No game is currently active in this channel.", ephemeral=True)
            return

        game = bot.active_game_channels[interaction.channel.id]

        if not game.is_day():
            await interaction.response.send_message("Patience. It's not yet time for nightfall.", ephemeral=True)
            return

        button.disabled = True
        await interaction.response.edit_message(view=self)

        await start_night_phase(interaction, game)


async def start_night_phase(interaction, game):
    if await check_game_over(interaction.channel, game):
        return

    game.game_state.set_night()
    await interaction.channel.send("AWOOOOO! The night has fallen!")

    victim = await actions.wolves_action.hunt(interaction, game)

    if await check_game_over(interaction.channel, game):
        return


@bot.command()
async def check(ctx):
    if not check_if_game_exists(ctx.channel.id):
        await ctx.reply("No game is currently active in this channel. Use `!new` to create a new game.")
        return
    
    game = bot.active_game_channels[ctx.channel.id]

    if ctx.author.id in game.players:
        player = game.players[ctx.author.id]

        if player.character:
            await dm_player_role(ctx, player, game.wolves)
        else:
            await ctx.reply("The game has not started yet. Please wait until the game starts.")
    else:
        await ctx.reply("You are not part of the current game.")


async def dm_player_role(channel, player, wolves):
    try:
        embed, file = create_player_role_embed(player, wolves)
        await player.user.send(embed=embed, file=file)
    except Exception:
        await channel.send(f"❌ Could not send DM to {player.mention}.")


def create_player_role_embed(player, wolves):
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


async def check_game_over(channel, game):
    if game.check_end_conditions():
        winner = game.get_winner()

        if winner == "DRAW":
            embed = discord.Embed(
                title="No one wins",
                description="The game has ended in a draw.",
                color=discord.Color.greyple()
            )
        else:
            embed = discord.Embed(
                title=f"The {winner} wins!",
                description=f"Congratulations! The {winner} team has won the game!",
                color=discord.Color.green() if winner.lower() == "good" else discord.Color.red()
            )
        
        await channel.send(embed=embed)

        del bot.active_game_channels[channel.id]
        await channel.send("The game has ended. Thanks for playing!")
        return True
    
    return False


@bot.command()
async def end(ctx):
    if not check_if_game_exists(ctx.channel.id):
        await ctx.reply("No game is currently active in this channel.")
        return
    
    await check_game_over(ctx.channel, bot.active_game_channels[ctx.channel.id])
    del bot.active_game_channels[ctx.channel.id]
    await ctx.reply("The game has ended.")


bot.run(token=token, log_handler=handler, log_level=logging.DEBUG)
