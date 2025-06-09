from . import wolves_action, seer_action, witch_action, guard_action


async def start_night_phase(ctx, game):
    game.game_state.set_night()
    await ctx.send("🌕 AWOOOOO! The night has fallen!")

    guard_target = await guard_action.guard(ctx, game)

    wolves_target = await wolves_action.hunt(ctx, game)

    if guard_target == wolves_target:
        guard_target = wolves_target = None

    await seer_action.check(ctx, game)

    witch_target = await witch_action.heal_or_kill(ctx, game, wolves_target)

    if (not wolves_target and not witch_target) or wolves_target == witch_target:
        await ctx.send(
            "🌞 Dawn breaks! The village awakens to a peaceful morning. **No one** was lost in the night."
        )
    else:
        victims = [v for v in [wolves_target, witch_target] if v is not None]

        for victim in victims:
            game.kill_player(victim.user.id)

        victim_names = "** and **".join(
            sorted([victim.user.display_name for victim in victims])
        )
        await ctx.send(
            f"🌞 As the sun rises, the villagers gather and discover that **{victim_names}** got killed during the night."
        )

    game.game_state.set_day()
