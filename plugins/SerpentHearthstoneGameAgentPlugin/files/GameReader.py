from hslog import LogParser
from hslog.export import EntityTreeExporter
from hearthstone.enums import GameTag, Step
from hearthstone.entities import Player, Card

import json
import io 

import entities
from board_state import DATA

# Reads information from game logs using hslog and relays to the GameAgent
class GameReader:

    def __init__(self, os):
        self.os = os
        parser = LogParser()
        if self.os == "Windows":
            log_dir = r"C:\Program Files (x86)\Hearthstone\Logs\Power.log"
            with io.open(log_dir, "r", encoding='utf8') as logs:
                lines = logs.readlines()
                self.logs = ''.join(lines)
            parser.read(io.StringIO(self.logs))
        elif self.os == "Linux":
            parser.read(io.StringIO(DATA))
        parser.flush()

        packet_tree = parser.games[-1]
        self.game = EntityTreeExporter(packet_tree).export().game
        self.player_names = ['Strafos', 'strafos']
        self.card_data = self.get_card_data()
        self.friendly_player = self.get_friendly()

    def get_card_data(self):
        if self.os == "Windows":
            json_dir = r"C:\Users\Zaibo\Desktop\playground\sai\plugins\SerpentHearthstoneGameAgentPlugin\files\cards.json"
        elif self.os == "Linux":
            json_dir = "/home/zaibo/code/Hearthstone-Quest-Bot/plugins/SerpentHearthstoneGameAgentPlugin/files/cards.json"
        else:
            raise Exception("Invalid OS")
        with io.open(json_dir, 'r', encoding='utf8') as json_file:
            json_str = json_file.read()
        return json.loads(json_str)

    def get_card_info(self, card_id):
        for card in self.card_data:
            if card['id'] == card_id:
                return card

    def get_game(self):
        return self.game

    def get_game_step(self):
        return self.game.tags[GameTag.STEP]

    # Return Hand of BaseCard objects sorted by increasing cost
    def get_current_hand(self):
        hand = entities.Hand()
        for card_in_hand in self.game.in_zone(3):
            id = card_in_hand.card_id
            if id:
                card_info = self.get_card_info(id)
                card_type = card_info['type']
                if card_type == "MINION":
                    try:
                        mechanics = card_info['mechanics']
                    except:
                        mechanics = None
                    hand.add_card(entities.HandMinion(card_info['name'], id, card_in_hand.tags[GameTag.COST], card_in_hand.tags[GameTag.ZONE_POSITION], card_info['attack'], card_info['health'], mechanics))
                elif card_type == "SPELL":
                    hand.add_card(entities.HandSpell(card_info['name'], id, card_in_hand.tags[GameTag.COST], card_in_hand.tags[GameTag.ZONE_POSITION]))
                elif card_type == "WEAPON":
                    hand.add_card(entities.HandWeapon(card_info['name'], id, card_in_hand.tags[GameTag.COST], card_in_hand.tags[GameTag.ZONE_POSITION], card_info['attack'], card_info['durability']))
        hand.sort_by_cost()
        return hand
    
    def get_current_board(self):
        minions = []
        weapons = []
        for board_card in self.game.in_zone(1):
            if type(board_card) == Card:
                id = board_card.card_id
                if id and "HERO" not in id:
                    card_info = self.get_card_info(id)
                    card_type = card_info['type']
                    if card_info and card_type != "HERO_POWER":
                        if card_type == 'WEAPON':
                            weapon = entities.BoardWeapon(card_info['name'], id, board_card.tags[GameTag.ZONE_POSITION], board_card.controller, board_card.tags[GameTag.ATK], board_card.tags[GameTag.DURABILITY])
                            weapons.append(weapon)
                            # weapons.append(board_card)
                        elif card_type == 'MINION':
                            minion = entities.BoardMinion(self, card_info['name'], id, board_card.tags[GameTag.ZONE_POSITION], board_card.controller, board_card.tags[GameTag.ATK], board_card.tags[GameTag.HEALTH], board_card.tags[GameTag.TAUNT])
                            minions.append(minion)
                            # minions.append(board_card)
        return entities.Board(minions, weapons)

    def get_current_player(self):
        return self.game.current_player

    ## Update Game object by rereading logs
    def update_state(self):
        parser = LogParser()
        if self.os == "Windows":
            log_dir = r"C:\Program Files (x86)\Hearthstone\Logs\Power.log"
            with io.open(log_dir, "r", encoding='utf8') as logs:
                lines = logs.readlines()
                self.logs = ''.join(lines)
            parser.read(io.StringIO(self.logs))
        elif self.os == "Linux":
            parser.read(io.StringIO(DATA))
        parser.flush()

        packet_tree = parser.games[-1]
        self.game = EntityTreeExporter(packet_tree).export().game
        self.friendly_player = self.get_friendly()

        hand = self.get_current_hand()
        turn = self.get_current_player()
        board = self.get_current_board()
        game_step = self.get_game_step()
        mana = self.get_current_mana()
        return hand, turn, board, game_step, mana

    def get_friendly(self):
        for player in self.game.players:
            if player.name in self.player_names:
                return player

    def get_current_mana(self):
        try:
            used = self.friendly_player.tags[GameTag.RESOURCES_USED]
        except:
            used = 0
        try:
            return self.friendly_player.tags[GameTag.RESOURCES] - used
        except:
            return 0