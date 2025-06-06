from models.Character import Character


class User:
    def __init__(self, id, name, mention):
        self.id = id
        self.name = name
        self.mention = mention
        self.display_name = name


class Player:
    def __init__(self, user):
        self.user = user

        self.character = None  # Will be set when the game starts
        self.is_alive = True

    def __str__(self):
        return f"{self.character.description}\nYou are {'ALIVE' if self.is_alive else 'DEAD'}!"

    def set_character(self, character: "Character"):
        self.character = character

    def is_wolf(self):
        return self.character and self.character.role == "Werewolf"

    def is_god(self):
        return self.character and self.character.role in [
            "Seer",
            "Witch",
            "Hunter",
            "Guard",
        ]

    def kill(self):
        self.is_alive = False

    def heal(self):
        self.is_alive = True
