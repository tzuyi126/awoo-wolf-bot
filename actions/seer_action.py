import discord

from discordui.vote_selection import send_dm_action
from methods import check_if_role_exists
from load_env_var import EnvConfig

envConfig = EnvConfig()


async def check(ctx, game):
    if not check_if_role_exists(game, "Seer"):
        return

    await ctx.channel.send(
        "🔮 The Seer wakes at night and sees through the veil of secrets...", silent=True
    )

    seer = next(
        player for player in game.players.values() if player.character.role == "Seer"
    )

    alive_players = [
        player for player in game.players.values() if player.is_alive and player != seer
    ]

    embed = discord.Embed(
        title="Choose a player to reveal their personality:",
        description=f"You have **{envConfig.ACTION_TIMEOUT_SEC}** seconds to take action.",
        color=discord.Color.blue(),
    )

    target_id = await send_dm_action(alive_players, seer, [], embed)

    if target_id:
        target = game.players.get(target_id)

        if target.is_wolf():
            await seer.user.send(f"{target.user.display_name} is a **Wolf**! 👎", silent=True)
        else:
            await seer.user.send(f"{target.user.display_name} is **not** a wolf. 👍", silent=True)

    await ctx.channel.send(
        "🔮 The Seer peers into the shadows and uncovers hidden truths about the chosen one.", silent=True
    )
