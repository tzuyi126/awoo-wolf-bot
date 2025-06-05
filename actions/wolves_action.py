import discord
import asyncio
from collections import Counter
from dotenv import load_dotenv
import os
import random

load_dotenv(override=True)
ACTION_TIMEOUT_SEC = int(os.getenv("ACTION_TIMEOUT_SEC", "15"))


class WolfVoteView(discord.ui.View):
    def __init__(self, wolf, wolves, alive_players):
        super().__init__(timeout=ACTION_TIMEOUT_SEC)
        self.value = None
        self.wolf = wolf
        self.wolves = wolves
        self.alive_players = alive_players

        for player in alive_players:
            self.add_item(self.WolfVoteButton(player))

    class WolfVoteButton(discord.ui.Button):
        def __init__(self, player):
            super().__init__(label=player.name, style=discord.ButtonStyle.secondary)
            self.player = player

        async def callback(self, interaction: discord.Interaction):
            view: WolfVoteView = self.view

            # Reset all buttons to secondary style
            for item in view.children:
                if isinstance(item, WolfVoteView.WolfVoteButton):
                    item.style = discord.ButtonStyle.secondary

            # Set the clicked button to success
            self.style = discord.ButtonStyle.success
            view.value = self.player.id

            await interaction.response.edit_message(view=view)

            for wolf in view.wolves:
                try:
                    await wolf.user.send(f"{view.wolf.name} has voted {self.player.name}.")
                except Exception:
                    pass  # Ignore DM failures


async def send_wolf_vote_dm(wolf, wolves, alive_players):
    view = WolfVoteView(wolf, wolves, alive_players)

    embed = discord.Embed(
        title="Choose a player to eliminate:",
        description=f"You have **{ACTION_TIMEOUT_SEC}** seconds to vote.",
        color=discord.Color.dark_red()
    )
    
    message = await wolf.user.send(embed=embed, view=view)

    for remaining in range(ACTION_TIMEOUT_SEC - 1, -1, -1):
        await asyncio.sleep(1)
        embed.description = f"You have **{remaining}** seconds to vote."
        try:
            await message.edit(embed=embed, view=view)
        except Exception:
            break  # DM closed or deleted

    return view.value


async def hunt(interaction, game):
    await interaction.channel.send("🐺 The wolves are gathering to decide their victim...")

    wolves = [player for player in game.players.values() if player.is_wolf and player.is_alive]
    alive_players = [player for player in game.players.values() if player.is_alive]

    # Store votes in the game object for this night
    night_votes = {}

    vote_tasks = {
        wolf.id: asyncio.create_task(send_wolf_vote_dm(wolf, wolves, alive_players))
        for wolf in wolves
    }

    # Wait for all vote tasks to complete (timeout is handled in send_wolf_vote_dm)
    results = await asyncio.gather(*vote_tasks.values(), return_exceptions=True)

    for wolf, voted_id in zip(wolves, results):
        if isinstance(voted_id, Exception):
            await interaction.channel.send(f"❌ Could not send DM to {wolf.mention}.")
        elif voted_id:
            night_votes[wolf.id] = voted_id
        else:
            try:
                await wolf.user.send("You did not vote in time.")
            except Exception:
                pass

    # Tally votes and process elimination after all wolves have voted or timeout
    if night_votes:
        vote_counts = Counter(night_votes.values())
        max_votes = max(vote_counts.values())
        candidates = [(player_id, max_votes) for player_id, count in vote_counts.items() if count == max_votes]

        if candidates:
            if len(candidates) > 1:
                chosen = random.choice(candidates)
                target_id, _ = chosen
                target = game.players.get(target_id)
                msg = f"Multiple players received the highest votes. Randomly chosen victim: {target.name}."
            else:
                target_id, _ = candidates[0]
                target = game.players.get(target_id)
                msg = f"The wolves have chosen their victim: {target.name} has been eliminated!"

            target.kill()

            for wolf in wolves:
                try:
                    await wolf.user.send(msg)
                except Exception:
                    pass  # Ignore DM failures
        
        return target
    else:
        await interaction.channel.send("🐺 The wolves failed to agree on a victim tonight.")

    return None