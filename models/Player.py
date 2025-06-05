from models.Character import Character

class User:
    def __init__(self, id, name, mention):
        self.id = id
        self.name = name
        self.mention = mention

class Player:
    def __init__(self, user):
        self.user = user
        self.id = user.id
        self.name = user.name
        self.mention = user.mention

        self.character = None  # Will be set when the game starts
        self.is_alive = True
        self.is_wolf = False  # Will be set based on the character role
        self.is_god = False  # Will be set based on the character role

    def __str__(self):
        return f"{self.character.description}\nYou are {'ALIVE' if self.is_alive else 'DEAD'}!"

    def set_character(self, character: 'Character'):
        self.character = character
        self.is_wolf = (character.role == "Werewolf")
        self.is_god = (character.role in ["Seer", "Witch", "Hunter"])

    def kill(self):
        self.is_alive = False