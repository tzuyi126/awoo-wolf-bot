import sys
from models.Character import Character
import uuid

class Game:
    def __init__(self, channel_id):
        self.id = str(uuid.uuid4())
        self.channel_id = channel_id
        self.players = set()
        self.num_players = 0

        self.game_state = "starting"  # Possible states: starting, day, night, finished
    
    def add_player(self, player):
        if not self.game_state == "starting" or self.num_players >= 12:
            return False
        
        if player not in self.players:
            self.players.add(player)
            self.num_players += 1

            return True
        else:
            return False

    def check_start_conditions(self):
        if not self.game_state == "starting":
            return False

        if not 6 <= self.num_players <= 12:
            return False
        
        return True

    def start(self):
        print(f"Starting game {self.id} in channel {self.channel_id}.")
        print(f"Welcome to the game! There are {self.num_players} players.")

        self.game_state = "day"