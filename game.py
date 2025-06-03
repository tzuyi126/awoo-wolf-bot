import sys
from models.Character import Character
import uuid

class Game:
    def __init__(self, channel_id, players):
        self.id = str(uuid.uuid4())
        self.channel_id = channel_id
        self.players = players
        self.num_players = len(players)

    def start(self):
        print(f"Starting game {self.id}.")
        print(f"Welcome to the game! There are {self.num_players} players.")
        for player in self.players:
            print(f"Player: {player.name}")

def start_game(channel_id, players):
    game = Game(channel_id, players)
    game.start()