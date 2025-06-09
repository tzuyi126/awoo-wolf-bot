import os
import discord
import logging


def check_if_game_exists(bot, channel_id):
    # Prevent multiple games in the same channel
    return channel_id in bot.active_game_channels.keys()


def check_if_role_exists(game, role):
    return role in game.roles


async def dm_player_role(channel, player, wolves):
    try:
        embed, file = create_player_role_embed(player, wolves)
        await player.user.send(embed=embed, file=file)
    except Exception as e:
        await channel.send(f"❌ Could not send DM to {player.user.mention}.")
        print(f"Error sending DM to player: {e}")


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

    if player.is_wolf():
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
