import os
from dotenv import load_dotenv

class EnvConfig:
    def __init__(self):
        load_dotenv(override=True)

        self.DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
        
        self.MIN_PLAYERS = int(os.getenv('MIN_PLAYERS', "5"))
        self.MAX_PLAYERS = int(os.getenv('MAX_PLAYERS', "12"))

        self.GAME_ROLES = os.getenv("GAME_ROLES")

        self.ACTION_TIMEOUT_SEC = int(os.getenv("ACTION_TIMEOUT_SEC", "30"))
        self.UI_TIMEOUT_SEC = int(os.getenv("UI_TIMEOUT_SEC", "3600"))

