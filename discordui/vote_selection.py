import discord
import os

from load_env_var import EnvConfig

envConfig = EnvConfig()


class ActionView(discord.ui.View):
    def __init__(self, button_players, decision_maker, result_recipients):
        super().__init__(timeout=envConfig.ACTION_TIMEOUT_SEC)
        self.value = None
        self.button_players = button_players
        self.decision_maker = decision_maker
        self.result_recipients = result_recipients

        for player in button_players:
            self.add_item(self.PlayerButton(player))

    class PlayerButton(discord.ui.Button):
        def __init__(self, player):
            super().__init__(label=player.user.name, style=discord.ButtonStyle.secondary)
            self.player = player

        async def callback(self, interaction: discord.Interaction):
            view: ActionView = self.view

            # If this button is already selected (success), unselect it (withdraw vote)
            if self.style == discord.ButtonStyle.success:
                self.style = discord.ButtonStyle.secondary
                view.value = None
                await interaction.response.edit_message(view=view)

                for result_recipient in view.result_recipients:
                    try:
                        await result_recipient.user.send(f"{view.decision_maker.user.name} has withdrawn their vote.")
                    except Exception:
                        await interaction.channel.send(f"Failed to notify {result_recipient.user.name} about the vote withdrawal.")
                return

            # Reset all buttons to secondary style
            for item in view.children:
                if isinstance(item, ActionView.PlayerButton):
                    item.style = discord.ButtonStyle.secondary

            # Set the clicked button to success
            self.style = discord.ButtonStyle.success
            view.value = self.player.user.id

            await interaction.response.edit_message(view=view)

            for result_recipient in view.result_recipients:
                try:
                    await result_recipient.user.send(f"{view.decision_maker.user.name} has voted {self.player.user.name}.")
                except Exception:
                    await interaction.channel.send(f"Failed to notify {result_recipient.user.name} about the vote.")