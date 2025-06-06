class Character:
    def __init__(self, role, personality, description, ability, pic=None):
        self.role = role
        self.personality = personality  # "good" | "evil"
        self.description = description
        self.ability = ability
        self.pic = pic


class Villager(Character):
    def __init__(self):
        super().__init__(
            "Villager",
            "good",
            "Your job is to execute all the wolves.",
            "Vote to eliminate players during the day.",
            "./pic/villager-icon.png",
        )


class Werewolf(Character):
    def __init__(self):
        super().__init__(
            "Werewolf",
            "evil",
            "Your job is to kill either all the villagers or all the gods.",
            "Discuss with you wolf pack and kill a player each night.",
            "./pic/werewolf-icon.png",
        )


class Seer(Character):
    def __init__(self):
        super().__init__(
            "Seer",
            "good",
            "You can see the true nature of a player.",
            "Choose one player and see if their are good or evil each night.",
            "./pic/seer-icon.png",
        )


class Witch(Character):
    def __init__(self):
        super().__init__(
            "Witch",
            "good",
            "Use your potions wisely to protect the villagers or eliminate wolves.",
            "You have two potions - one to heal and one to kill. You can use either one during the night.",
            "./pic/witch-icon.png",
        )

        self.heal_potion = True
        self.kill_potion = True

    def can_heal(self):
        return self.heal_potion

    def can_kill(self):
        return self.kill_potion

    def heal(self):
        self.heal_potion = False

    def kill(self):
        self.kill_potion = False


class Hunter(Character):
    def __init__(self):
        super().__init__(
            "Hunter",
            "good",
            "Help the villagers kill the wolves.",
            "If you're either killed by the wolves or executed by the villagers, you can take one player down with you.",
            "./pic/hunter-icon.png",
        )


def get_character_by_name(name):
    characters = {
        "Villager": Villager(),
        "Werewolf": Werewolf(),
        "Seer": Seer(),
        "Witch": Witch(),
        "Hunter": Hunter(),
    }

    if name not in characters:
        raise ValueError(f"Character '{name}' does not exist.")

    return characters[name]
