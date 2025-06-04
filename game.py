import sys
from models.Character import Villager, Werewolf, Seer, Witch
from models.Player import Player, User
import uuid
import random
import os
import json

class Game:
    def __init__(self, channel_id):
        self.id = str(uuid.uuid4())
        self.channel_id = channel_id
        self.players = {}
        self.num_players = 0

        self.game_state = "starting"  # Possible states: starting, day, night, finished
    
    def add_player(self, player):
        if not self.game_state == "starting" or self.num_players >= 12:
            return False
        
        if player.id not in self.players:
            self.players[player.id] = Player(player)
            self.num_players += 1

            return True
        else:
            return False

    def check_start_conditions(self):
        if not self.game_state == "starting":
            return False

        '''if not 6 <= self.num_players <= 12:
            return False'''
        while self.num_players < 6:
            i = self.num_players
            u = User(id=str(i), name=f"Player{i}", mention=f"<@{i}>")
            self.add_player(Player(u))  # Simulate players for testing
        
        return True

    def start(self):
        print(f"Starting game {self.id}. There are {self.num_players} players.")

        self.assign_characters()

        self.game_state = "night"

    def assign_characters(self):
        # Try to read roles from env
        roles_env = os.getenv("GAME_ROLES")
        roles_dict = json.loads(roles_env)
        roles = roles_dict.get(str(self.num_players))

        roles = roles.copy()  # Avoid modifying the original list
        random.shuffle(roles)

        for player in self.players.values():
            if not roles:
                break
            role = roles.pop()

            if role == "Villager":
                player.set_character(Villager())
            elif role == "Werewolf":
                player.set_character(Werewolf())
            elif role == "Seer":
                player.set_character(Seer())
            elif role == "Witch":
                player.set_character(Witch())