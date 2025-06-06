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

        self.heal_potion = 1
        self.kill_potion = 1

    def can_heal(self):
        return self.heal_potion == 1

    def can_kill(self):
        return self.kill_potion == 1

    def heal(self):
        self.heal_potion = 0

    def kill(self):
        self.kill_potion = 0


class Hunter(Character):
    def __init__(self):
        super().__init__(
            "Hunter",
            "good",
            "Help the villagers kill the wolves.",
            "If you're either killed by the wolves or executed by the villagers, you can take one down with you by using `!kill <player_name>`.",
            "./pic/hunter-icon.png",
        )


class Guard(Character):
    def __init__(self):
        super().__init__(
            "Guard",
            "good",
            "You can protect a player from being killed by the wolves each night. However, a witch's potion can override your protection.",
            "Choose a player to guard each night, but you cannot protect the same player two nights in a row.",
            "./pic/guard-icon.png",
        )

        self.last_protected = None

    def can_protect(self, player_id):
        return player_id != self.last_protected

    def protect(self, player_id):
        self.last_protected = player_id


def get_character_by_name(name):
    characters = {
        "Villager": Villager(),
        "Werewolf": Werewolf(),
        "Seer": Seer(),
        "Witch": Witch(),
        "Hunter": Hunter(),
        "Guard": Guard(),
    }

    if name not in characters:
        raise ValueError(f"Character '{name}' does not exist.")

    return characters[name]
