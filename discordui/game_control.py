import discord

from methods import dm_player_role, start_night_phase
from load_env_var import EnvConfig

envConfig = EnvConfig()


class NewGameView(discord.ui.View):
    def __init__(self, bot, channel_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.channel_id = channel_id

        self.add_item(self.JoinGameButton())
        self.add_item(self.StartGameButton())

    class JoinGameButton(discord.ui.Button):
        def __init__(self):
            super().__init__(
                label="Join The Game", style=discord.ButtonStyle.primary, emoji="🤝"
            )

        async def callback(self, interaction: discord.Interaction):
            try:
                game = self.view.bot.active_game_channels[self.view.channel_id]
                user = interaction.user

                if not game.add_player(user):
                    await interaction.response.send_message(
                        f"{user.mention}, you cannot (re)join the game at this moment!",
                        ephemeral=True,
                    )
                    return

                await interaction.response.send_message(
                    f"{user.mention} has joined the game! Current players: `{game.num_players}`",
                    ephemeral=False,
                )

            except Exception:
                self.disabled = True
                await interaction.response.edit_message(view=self.view)
                await interaction.followup.send(
                    "You cannot interact with this button at the time.", ephemeral=True
                )

    class StartGameButton(discord.ui.Button):
        def __init__(self):
            super().__init__(
                label="Game Start", style=discord.ButtonStyle.success, emoji="🚀"
            )

        async def callback(self, interaction: discord.Interaction):
            try:
                game = self.view.bot.active_game_channels[self.view.channel_id]

                if not game.check_start_conditions():
                    await interaction.response.send_message(
                        f"Cannot start the game. Either the game is already in progress or the number of players is not sufficient (at least {envConfig.MIN_PLAYERS}, at most {envConfig.MAX_PLAYERS}).",
                        ephemeral=False,
                    )
                    return

                self.disabled = True
                await interaction.response.edit_message(view=self.view)
                await interaction.followup.send(
                    "The game is starting! Prepare yourselves!", ephemeral=False
                )
                game.start()

                for player in game.players.values():
                    await dm_player_role(interaction.channel, player, game.wolves)

                await interaction.channel.send(
                    "💡 You can mute your mic during the night to avoid spoilers.\n"
                    "⬇️ Whenever you are ready, press the button below to start the night.",
                    view=StartNightButton(self.view.bot),
                )

            except Exception:
                self.disabled = True
                await interaction.response.edit_message(view=self.view)
                await interaction.followup.send(
                    "You cannot interact with this button at the time.", ephemeral=True
                )


class StartNightButton(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(
        label="The night has fallen.",
        style=discord.ButtonStyle.danger,
        custom_id="start_night_phase",
        emoji="🌑",
    )
    async def start_night(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        try:
            game = self.bot.active_game_channels[interaction.channel.id]

            if not game.is_day():
                await interaction.response.send_message(
                    "Patience. It's not yet time for nightfall.", ephemeral=True
                )
                return

            button.disabled = True
            await interaction.response.edit_message(view=self)

            await start_night_phase(self.bot, interaction, game)

        except Exception:
            button.disabled = True
            await interaction.response.edit_message(view=self)
            await interaction.followup.send(
                "You cannot interact with this button at the time.", ephemeral=True
            )
