import discord
import asyncio
from collections import Counter
import random

from discordui.vote_selection import ActionView
from load_env_var import EnvConfig

envConfig = EnvConfig()


async def send_wolf_vote_dm(alive_players, wolf, alive_wolves):
    view = ActionView(alive_players, wolf, alive_wolves)

    embed = discord.Embed(
        title="Choose a player to eliminate:",
        description=f"You have **{envConfig.ACTION_TIMEOUT_SEC}** seconds to vote.",
        color=discord.Color.dark_red(),
    )

    message = await wolf.user.send(embed=embed, view=view)

    for remaining in range(envConfig.ACTION_TIMEOUT_SEC - 1, -1, -1):
        await asyncio.sleep(1)
        embed.description = f"You have **{remaining}** seconds to vote."

        try:
            await message.edit(embed=embed, view=view)
        except Exception:
            break  # DM closed or deleted

    return view.value


async def hunt(interaction, game):
    await interaction.channel.send(
        "🐺 The wolves are gathering to decide their victim..."
    )

    alive_wolves = [
        player for player in game.players.values() if player.is_wolf and player.is_alive
    ]
    alive_players = [player for player in game.players.values() if player.is_alive]

    vote_tasks = {
        wolf.user.id: asyncio.create_task(
            send_wolf_vote_dm(alive_players, wolf, alive_wolves)
        )
        for wolf in alive_wolves
    }

    # Wait for all vote tasks to complete (timeout is handled in send_wolf_vote_dm)
    results = await asyncio.gather(*vote_tasks.values(), return_exceptions=True)

    # Store votes in the game object for this night
    night_votes = {}

    for wolf, voted_id in zip(alive_wolves, results):
        if isinstance(voted_id, Exception):
            pass
        elif voted_id:
            night_votes[wolf.user.id] = voted_id
        else:
            try:
                await wolf.user.send("You did not vote in time.")
            except Exception:
                pass

    # Tally votes and process elimination after all wolves have voted or timeout
    if night_votes:
        vote_counts = Counter(night_votes.values())
        max_votes = max(vote_counts.values())
        candidates = [
            player_id for player_id, count in vote_counts.items() if count == max_votes
        ]

        if candidates:
            if len(candidates) > 1:
                target_id = random.choice(candidates)
                target = game.players.get(target_id)
                msg = f"Multiple players received the highest votes. Your victim has been picked randomly: {target.user.name}."
            else:
                target_id = candidates[0]
                target = game.players.get(target_id)
                msg = (
                    f"You have chosen your victim: {target.user.name} has been killed!"
                )

            target.kill()

            for wolf in alive_wolves:
                try:
                    await wolf.user.send(msg)
                except Exception:
                    pass  # Ignore DM failures

        await interaction.channel.send("🐺 The wolves have made their choice.")

        return target
    else:
        await interaction.channel.send(
            "🐺 The wolves failed to agree on a victim tonight."
        )

    return None
