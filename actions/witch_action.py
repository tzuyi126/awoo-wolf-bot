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

    title += f"\nYou have {witch.character.heal_potion} healing potion and {witch.character.kill_potion} poison left."

    embed = discord.Embed(
        title=title,
        description=f"You have **{envConfig.ACTION_TIMEOUT_SEC}** seconds to take action.",
        color=discord.Color.dark_red(),
    )

    target_id = await send_dm_action(alive_players, witch, [], embed)

    await ctx.channel.send(
        "🧪 The Witch has made a choice, and only for the good."
    )

    if target_id:
        target = game.players.get(target_id)

        if target == victim and witch.character.can_heal():
            await witch.user.send(f"You healed {target.user.display_name}.")
            witch.character.heal()
            return target

        if target != victim and witch.character.can_kill():
            await witch.user.send(f"You poisoned {target.user.display_name}.")
            witch.character.kill()
            return target

        await witch.user.send("You couldn't use a potion, probably because you're out of that type.")

    return None
