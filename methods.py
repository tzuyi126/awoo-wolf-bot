import os
import discord

from actions import wolves_action, seer_action


def check_if_game_exists(bot, channel_id):
    return channel_id in bot.active_game_channels.keys()


async def start_night_phase(bot, interaction, game):
    if await check_game_over(bot, interaction.channel, game):
        return

    game.game_state.set_night()
    await interaction.channel.send("AWOOOOO! The night has fallen!")

    victim = await wolves_action.hunt(interaction, game)

    await seer_action.check(interaction, game)

    if await check_game_over(bot, interaction.channel, game):
        return


async def dm_player_role(channel, player, wolves):
    try:
        embed, file = create_player_role_embed(player, wolves)
        await player.user.send(embed=embed, file=file)
    except Exception:
        await channel.send(f"❌ Could not send DM to {player.user.mention}.")


def create_player_role_embed(player, wolves):
    embed = discord.Embed(
        title=f"You are a {player.character.role}",
        description=f"{player.__str__()}",
        color=(
            discord.Color.blue()
            if player.character.personality == "good"
            else discord.Color.red()
        ),
    )

    embed.add_field(name="Ability", value=player.character.ability, inline=False)

    embed.set_thumbnail(url=f"attachment://{os.path.basename(player.character.pic)}")

    if player.is_wolf:
        embed.add_field(
            name="The Wolf Pack (Only the wolves know!)",
            value=", ".join([wolf for wolf in wolves]),
            inline=False,
        )

    file = discord.File(
        player.character.pic, filename=f"{os.path.basename(player.character.pic)}"
    )

    return embed, file


async def check_game_over(bot, channel, game):
    if game.check_end_conditions():
        winner = game.get_winner()

        embed = discord.Embed(
            title=f"The {winner} wins!",
            description=f"Congratulations! The {winner} team has won the game!",
            color=(
                discord.Color.green()
                if winner.lower() == "good"
                else discord.Color.red()
            ),
        )

        await channel.send(embed=embed)

        del bot.active_game_channels[channel.id]
        await channel.send("The game has ended. Thanks for playing!")
        return True

    return False
