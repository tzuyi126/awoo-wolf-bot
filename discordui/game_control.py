import discord

from methods import dm_player_role
from load_env_var import EnvConfig

envConfig = EnvConfig()


class NewGameView(discord.ui.View):
    def __init__(self, bot, channel_id):
        super().__init__(timeout=envConfig.UI_TIMEOUT_SEC)
        self.bot = bot
        self.channel_id = channel_id

        self.add_item(self.JoinGameButton())
        self.add_item(self.StartGameButton())

    async def disable_all_buttons(self):
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True

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
                await self.view.disable_all_buttons()
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

                await self.view.disable_all_buttons()
                await interaction.response.edit_message(view=self.view)
                await interaction.followup.send(
                    "The game is starting! Prepare yourselves!", ephemeral=False
                )

                game.start()

                for player in game.players.values():
                    await dm_player_role(interaction.channel, player, game.wolves)

                await interaction.channel.send(
                    "Your role has been sent to your DMs! Use `!check` if you want the information resent.\n"
                    "💡 You may mute your microphone during the night to avoid spoilers.\n"
                    "🌙 When you are ready, type `!night` to begin the night.",
                )

            except Exception:
                self.view.disable_all_buttons()
                await interaction.response.edit_message(view=self.view)
                await interaction.followup.send(
                    "You cannot interact with this button at the time.", ephemeral=True
                )
