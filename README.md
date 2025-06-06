# Awoo Wolf Bot
A Discord bot designed to play Werewolf game on Discord.

## Features

- Host and manage Werewolf games in Discord servers
- Automated role assignment and night/day cycles
- Customizable game settings
- Fun and interactive commands

## Roles

- **Villager**: Ordinary player with no special abilities. Works with others to find the werewolves.
- **Seer**: Each night, can choose one player to reveal whether they are a werewolf or not.
- **Witch**: Has two potions—one to save a player from death, one to eliminate a player. Each potion can be used once per game.
- **Hunter**: If eliminated, can take one player down with them.
- **Guard**: Each night, can protect one player from being eliminated (cannot guard the same player two nights in a row).

## Getting Started

1. Invite the bot to your Discord server.
2. Use `/start` to begin a new game.
3. Follow the prompts to add players and play the game.

## Commands

- `!new` — Start a new Werewolf game.
- `!list` — Display all players and their assigned roles in the current game.
- `!check` — Privately receive your role and abilities via DM.
- `!night` — Initiate the night phase.
- `!kill <player_name>` — Eliminate a player during the day.
- `!end` — End the ongoing game session.