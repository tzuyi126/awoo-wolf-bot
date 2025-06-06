import discord

from discordui.vote_selection import send_dm_action
from methods import check_if_role_exists
from load_env_var import EnvConfig

envConfig = EnvConfig()


async def guard(ctx, game):
    if not check_if_role_exists(game, "Guard"):
        return None

    await ctx.channel.send("🛡️ The Guard is choosing someone to protect tonight...")

    guard = next(
        player for player in game.players.values() if player.character.role == "Guard"
    )

    selectable_players = [
        player
        for player in game.players.values()
        if player.is_alive and guard.character.can_protect(player.user.id)
    ]

    embed = discord.Embed(
        title="Choose a player to protect tonight:",
        description=f"You have **{envConfig.ACTION_TIMEOUT_SEC}** seconds to take action.",
        color=discord.Color.blue(),
    )

    target_id = await send_dm_action(selectable_players, guard, [], embed)

    await ctx.channel.send(
        "🛡️ The Guard has made the choice and will protect the one at all costs."
    )

    if target_id:
        target = game.players.get(target_id)

        # Store the last protected player to prevent consecutive protection
        guard.character.protect(target.user.id)

        await guard.user.send(f"You are protecting {target.user.display_name} tonight.")
        return target

    await guard.user.send("You did not choose anyone to protect tonight.")
    return None
