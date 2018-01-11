class BaseHandCard:
    def __init__(self, name, id, cost, position):
        self.id = id
        self.cost = cost
        self.name = name
        self.positon = position

class HandMinion(BaseHandCard):
    def __init__(self, name, id, cost, position, attack, health, mechanics=None):
        super().__init__(name, id, cost, position)
        self.attack = attack
        self.health = health
        self.mechanics = mechanics
        self.value = self.calc_value()
        # race? (elemental, pirate, murloc)
    
    def calc_value(self):
        value = self.attack*1.1 + self.health # + 1 To weight playing more cards
        if self.mechanics:
            for mechanic in ["TAUNT", "BATTLECRY", "DEATHRATTLE", "CHARGE"]:
                if mechanic in self.mechanics:
                    value += 1

class HandSpell(BaseHandCard):
    def __init__(self, name, id, cost, position):
        super().__init__(id, name, cost, position)
        self.value = self.cost

class HandWeapon(BaseHandCard):
    def __init__(self, name, id, cost, position, attack, durability):
        super().__init__(id, name, cost, position)
        self.attack = attack
        self.durability = durability
        self.value = self.attack * self.durability

class Hand:
    def __init__(self):
        self.hand = []
        self.size = 0

    def add_card(self, card):
        self.hand.append(card)
        self.size += 1

class BaseBoardCard:
    def __init__(self, name, id, position, controller):
        self.name = name
        self.id = id
        self.position = position
        self.controller = controller

class BoardMinion(BaseBoardCard):
    def __init__(self, name, id, position, controller, attack, health):
        super().__init__(name, id, position, controller)
        self.attack = attack
        self.health = health

# class BoardEnchantments(BaseBoardCard):

class Board:
    def __init__(self, board_minions, weapons=None):
        self.friendly_minions, self.enemy_minions = self.divide_minions(board_minions)
        self.weapon = self.find_friendly_weapon(weapons)
    
    def divide_minions(self, board_minions):
        friendly_minions = []
        enemy_minions = []
        for minion in board_minions:
            if minion.controller == 'strafos' or minion.controller == 'Strafos':
                friendly_minions.append(minion)
            else:
                enemy_minions.append(minion)
        return friendly_minions, enemy_minions

    def find_friendly_weapon(self, weapons):
        if weapons:
            for weapon in weapons:
                if weapon.controller == 'strafos' or weapon.controller == 'Strafos':
                    return weapon
        return None

# TODO?
class GameState:
    def __init__():
        pass