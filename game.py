import uuid
import random
import json

from models.Character import get_character_by_name
from models.Player import Player, User
from load_env_var import EnvConfig

# Load roles from environment variable
envConfig = EnvConfig()


class State:
    STARTING = "starting"
    DAY = "day"
    NIGHT = "night"
    FINISHED = "finished"


class GameState:
    def __init__(self):
        self.current_state = State.STARTING

    def set_day(self):
        self.current_state = State.DAY

    def set_night(self):
        self.current_state = State.NIGHT

    def set_finished(self):
        self.current_state = State.FINISHED

    def get_state(self):
        return self.current_state


class Game:
    def __init__(self, channel_id):
        self.id = str(uuid.uuid4())
        self.channel_id = channel_id
        self.players = {}
        self.num_players = 0

        self.game_state = GameState()
        self.roles = []
        self.wolves = set()

    def add_player(self, player):
        if (
            not self.game_state.get_state() == State.STARTING
            or self.num_players >= envConfig.MAX_PLAYERS
        ):
            return False

        if player.id not in self.players:
            self.players[player.id] = Player(player)
            self.num_players += 1

            return True
        else:
            return False

    def check_start_conditions(self):
        if not self.game_state.get_state() == State.STARTING:
            return False

        """if not envConfig.MIN_PLAYERS <= self.num_players <= envConfig.MAX_PLAYERS:
            return False"""

        """ TEST CONDITION """
        while self.num_players < envConfig.MIN_PLAYERS:
            i = self.num_players
            u = User(id=str(i), name=f"Player{i}", mention=f"<@{i}>")
            self.add_player(u)  # Simulate players for testing
        """ TEST CONDITION """

        return True

    def check_end_conditions(self):
        if self.game_state.get_state() == State.STARTING:
            return False
        elif self.game_state.get_state() == State.FINISHED:
            return True

        wolves_alive = self.check_if_wolves_alive()
        villagers_alive = self.check_if_villagers_alive()
        gods_alive = self.check_if_gods_alive()

        if self.num_players <= 5:
            # For small games (<=5), wolves win if villagers and gods are all dead
            if not villagers_alive and not gods_alive:
                self.game_state.set_finished()
                self.winner = "EVIL"
                return True
            elif not wolves_alive:
                self.game_state.set_finished()
                self.winner = "GOOD"
                return True
        else:
            # For larger games (>5), wolves win if villagers or gods are all dead
            if not villagers_alive or not gods_alive:
                self.game_state.set_finished()
                self.winner = "EVIL"
                return True
            elif not wolves_alive:
                self.game_state.set_finished()
                self.winner = "GOOD"
                return True

        return False

    def get_winner(self):
        if self.game_state.get_state() != State.FINISHED:
            self.check_end_conditions()
        return getattr(self, "winner", None)

    def check_if_wolves_alive(self):
        return any(
            player.is_wolf() and player.is_alive for player in self.players.values()
        )

    def check_if_villagers_alive(self):
        return any(
            not player.is_wolf() and not player.is_god() and player.is_alive for player in self.players.values()
        )

    def check_if_gods_alive(self):
        return any(
            player.is_god() and player.is_alive for player in self.players.values()
        )

    def is_day(self):
        return self.game_state.get_state() == State.DAY

    def is_night(self):
        return self.game_state.get_state() == State.NIGHT

    def start(self):
        print(f"Starting game {self.id}. There are {self.num_players} players.")

        self.assign_characters()

        self.game_state.set_day()

    def assign_characters(self):
        # Try to read roles from env
        roles_dict = json.loads(envConfig.GAME_ROLES)
        self.roles = roles_dict.get(str(self.num_players))

        roles = self.roles.copy()  # Avoid modifying the original list
        random.shuffle(roles)

        for player in self.players.values():
            if not roles:
                break
            role = roles.pop()
            player.set_character(get_character_by_name(role))

            if role == "Werewolf":
                self.wolves.add(player.user.display_name)

    def kill_player(self, player_id):
        if player_id in self.players:
            player = self.players[player_id]
            player.kill()

            print(f"Player {player.user.display_name} has been killed.")
            return True
        else:
            print(f"Player with ID {player_id} does not exist.")
            return False
