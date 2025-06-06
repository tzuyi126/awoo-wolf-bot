import discord
import asyncio
from collections import Counter
import random

from discordui.vote_selection import send_dm_action
from load_env_var import EnvConfig

envConfig = EnvConfig()


async def hunt(ctx, game):
    await ctx.channel.send(
        "🐺 The Wolves are gathering to decide their victim..."
    )

    wolves = [
        player for player in game.players.values() if player.is_wolf()
    ]
    alive_players = [player for player in game.players.values() if player.is_alive]

    embed = discord.Embed(
        title="Choose a player to eliminate:",
        description=f"You have **{envConfig.ACTION_TIMEOUT_SEC}** seconds to take action.",
        color=discord.Color.dark_red(),
    )

    vote_tasks = {
        wolf.user.id: asyncio.create_task(
            send_dm_action(alive_players, wolf, wolves, embed)
        )
        for wolf in wolves
    }

    # Wait for all vote tasks to complete (timeout is handled in send_wolf_vote_dm)
    results = await asyncio.gather(*vote_tasks.values(), return_exceptions=True)

    # Store votes in the game object for this night
    night_votes = {}

    for wolf, voted_id in zip(wolves, results):
        if isinstance(voted_id, Exception):
            pass
        elif voted_id:
            night_votes[wolf.user.id] = voted_id
        elif wolf.is_alive:
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
                msg = f"Multiple players received the highest votes. Your victim has been picked randomly: {target.user.display_name}."
            else:
                target_id = candidates[0]
                target = game.players.get(target_id)
                msg = (
                    f"You have chosen your victim: {target.user.display_name}."
                )

            for wolf in wolves:
                try:
                    await wolf.user.send(msg)
                except Exception:
                    pass  # Ignore DM failures

        await ctx.channel.send("🐺 The Wolves have made their choice.")

        return target
    
    await ctx.channel.send(
        "🐺 The Wolves failed to agree on a victim tonight."
    )

    return None
