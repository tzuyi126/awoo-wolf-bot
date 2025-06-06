
from methods import check_game_over

from . import wolves_action, seer_action, witch_action

async def start_night_phase(bot, ctx, game):
    if await check_game_over(bot, ctx.channel, game):
        return

    game.game_state.set_night()
    await ctx.send("AWOOOOO! The night has fallen!")

    victim = await wolves_action.hunt(ctx, game)

    await seer_action.check(ctx, game)

    target = await witch_action.heal_or_kill(ctx, game, victim)

    if target == victim:
        # The victim got healed by the witch
        victim = target = None

    await ctx.send("🌞 The day has dawned!")


    