class Character:
    def __init__(self, role, personality, pic=None):
        self.role = role
        self.personality = personality # "good" | "evil"
        self.description = f"{role} is a {personality} character."
        self.pic = pic

class Villager(Character):
    def __init__(self, role="Villager", personality="good", pic=None):
        super().__init__(role, personality, pic)
