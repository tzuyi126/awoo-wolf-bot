class Character:
    def __init__(self, role, personality, description, pic=None):
        self.role = role
        self.personality = personality # "good" | "evil"
        self.description = f"You are a {role} and you are {personality}. {description}"
        self.pic = pic

class Villager(Character):
    def __init__(self):
        super().__init__("Villager", "good", "Your job is to execute all of the wolves.", "./pic/villager-icon.png")

class Werewolf(Character):
    def __init__(self):
        super().__init__("Werewolf", "evil", "Your job is to kill either all the villagers or all the gods.", "./pic/werewolf-icon.png")

class Seer(Character):
    def __init__(self):
        super().__init__("Seer", "good", "You can see the true nature of one player each night.", "./pic/seer-icon.png")

class Witch(Character):
    def __init__(self):
        super().__init__("Witch", "good", "You have two potions - one to heal and one to kill. Use them wisely to protect the villagers or eliminate wolves.", "./pic/witch-icon.png")

class Hunter(Character):
    def __init__(self):
        super().__init__("Hunter", "good", "If you're either killed by the wolves or executed by the villagers, you can take one player down with you.", "./pic/hunter-icon.png")

def get_character_by_name(name):
    characters = {
        "Villager": Villager(),
        "Werewolf": Werewolf(),
        "Seer": Seer(),
        "Witch": Witch(),
        "Hunter": Hunter()
    }
    
    if name not in characters:
        raise ValueError(f"Character '{name}' does not exist.")
    
    return characters[name]