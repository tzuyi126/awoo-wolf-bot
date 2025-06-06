import discord

from discordui.vote_selection import send_dm_action
from methods import check_if_role_exists
from load_env_var import EnvConfig

envConfig = EnvConfig()


async def heal_or_kill(ctx, game, victim):
    if not check_if_role_exists(game, "Witch"):
        return None

    await ctx.channel.send(
        "🧪 The Witch considers using the potion, pondering whether to alter the fate of the night..."
    )

    witch = next(player for player in game.players.values() if player.character.role == "Witch")

    alive_players = [player for player in game.players.values() if player.is_alive]

    if victim:
        title = (
            f"**{victim.user.display_name}** has been killed! "
            f"Choose **{victim.user.display_name}** to heal or another player to poison:"
        )
    else:
        title = "No one has been killed. Choose a player to poison:"

    embed = discord.Embed(
        title=title,
        description=f"You have **{envConfig.ACTION_TIMEOUT_SEC}** seconds to take action.",
        color=discord.Color.dark_red(),
    )

    target_id = await send_dm_action(alive_players, witch, [], embed)

    if target_id:
        target = game.players.get(target_id)

        if target == victim:
            await witch.user.send(f"You healed {target.user.display_name}.")
        else:
            await witch.user.send(f"You poisoned {target.user.display_name}.")

    await ctx.channel.send(
        "🧪 The Witch has made a choice, and only for the good."
    )

    return target if target_id else None
