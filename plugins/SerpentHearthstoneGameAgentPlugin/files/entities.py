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
        self.mechanics = mechanics
        self.value = self.calc_value()
        # race? (elemental, pirate, murloc)
    
    def calc_value(self):
        value = self.attack*1.1 + self.health # + 1 To weight playing more cards
        for mechanic in ["TAUNT", "BATTLECRY", "DEATHRATTLE", "CHARGE"]:
            if mechanic in self.mechanics:
                value += 1


class SpellCard(BaseCard):
    def __init__(self, name, id, cost):
        super().__init__(id, name, cost)

class WeaponCard(BaseCard):
    def __init__(self, name, id, cost, attack, durability):
        super().__init__(id, name, cost)
        self.attack = attack
        self.durability