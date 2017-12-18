class BaseCard:
    def __init__(self, name, id, cost, position):
        self.id = id
        self.cost = cost
        self.name = name
        self.positon = position

class MinionCard(BaseCard):
    def __init__(self, name, id, cost, attack, health, mechanics=None):
        super().__init__(id, name, cost)
        self.attack = attack
        self.health = health
        self.tags = tags
        # race? (elemental, pirate, murloc)

class SpellCard(BaseCard):
    def __init__(self, name, id, cost):
        super().__init__(id, name, cost)

class WeaponCard(BaseCard):
    def __init__(self, name, id, cost, attack, durability):
        super().__init__(id, name, cost)
        self.attack = attack
        self.durability