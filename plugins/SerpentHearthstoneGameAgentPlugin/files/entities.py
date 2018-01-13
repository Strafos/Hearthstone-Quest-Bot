class BaseHandCard:
    def __init__(self, name, id, cost, position):
        self.id = id
        self.cost = cost
        self.name = name
        self.position = position

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
        for mechanic in self.mechanics:
            if mechanic == "CHARGE":
                value += self.attack
            else:
                value += 1
        # if self.mechanics:
            # for mechanic in ["TAUNT", "BATTLECRY", "DEATHRATTLE", "CHARGE"]:
            #     if mechanic in self.mechanics:
            #         value += 1
        return value

class HandSpell(BaseHandCard):
    def __init__(self, name, id, cost, position):
        # print(position)
        super().__init__(name, id, cost, position)
        self.value = self.cost + .5

class HandWeapon(BaseHandCard):
    def __init__(self, name, id, cost, position, attack, durability):
        super().__init__(name, id, cost, position)
        self.attack = attack
        self.durability = durability
        self.value = self.attack * self.durability

class HeroPower():
    # Hunter HP
    def __init__(self, name, cost, hero, enemy_health):
        self.name = name
        self.cost = cost
        self.value = 0
        self.hero = hero
        if enemy_health <= 15:
            self.value += 1.2**(15 - enemy_health)

class Hand:
    def __init__(self):
        self.hand = []
        self.size = 0

    def add_card(self, card):
        self.hand.append(card)
        if card.name != 'Hero Power':
            self.size += 1
    
    def sort_by_cost(self):
        # for i in self.hand:
        #     print(i.name)
        self.hand.sort(key=lambda card: card.cost)
        # for i in self.hand:
        #     print(i.name)

class BaseBoardCard:
    def __init__(self, name, id, position, controller):
        self.name = name
        self.id = id
        self.position = position
        self.controller = controller

class BoardMinion(BaseBoardCard):
    def __init__(self, name, id, position, controller, attack, health, taunt, exhausted):
        super().__init__(name, id, position, controller)
        self.attack = attack
        self.health = health
        self.taunt = taunt
        self.exhausted = exhausted
        # self.card = card

class BoardWeapon(BaseBoardCard):
    def __init__(self, name, id, position, controller, attack, durability):
        super().__init__(name, id, position, controller)
        self.attack = attack
        self.durability = durability
        # self.card = card

class BoardHero(BaseBoardCard):
    def __init__(self, name, id, position, controller, health):
        super().__init__(name, id, position, controller)
        self.health = health

# class BoardEnchantments(BaseBoardCard):

class Board:
    def __init__(self, board_minions, weapons=None, heroes):
        self.ally_minions, self.enemy_minions = self.divide_minions(board_minions)
        self.weapon = self.find_friendly_weapon(weapons)
        self.ally, self.enemy = divide_heroes(self, heroes)
    
    def divide_heroes(self, heroes):
        for hero in heroes:
            if heroes.controller.name.lower() == 'strafos':
                ally = hero
            else:
                enemy = hero
        return ally, enemy

    def divide_minions(self, board_minions):
        ally_minions = []
        enemy_minions = []
        for minion in board_minions:
            if minion.controller.name == 'strafos' or minion.controller.name == 'Strafos':
                ally_minions.append(minion)
            else:
                enemy_minions.append(minion)
        return ally_minions, enemy_minions

    def find_friendly_weapon(self, weapons):
        if weapons:
            for weapon in weapons:
                if weapon.controller.name == 'strafos' or weapon.controller.name == 'Strafos':
                    return weapon
        return None