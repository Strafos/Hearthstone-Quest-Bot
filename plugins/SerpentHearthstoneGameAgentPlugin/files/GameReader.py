from hslog import LogParser
from hslog.export import EntityTreeExporter
from hearthstone.enums import GameTag, Step
from hearthstone.entities import Player, Card

import json
import io 

import entities
# from board_state import DATA

# Reads information from game logs using hslog and relays to the GameAgent
class GameReader:

    def __init__(self):
        log_dir = r"C:\Program Files (x86)\Hearthstone\Logs\Power.log"
        with io.open(log_dir, "r", encoding='utf8') as logs:
            lines = logs.readlines()
            self.logs = ''.join(lines)
        parser = LogParser()

        parser.read(io.StringIO(self.logs))
        # parser.read(io.StringIO(DATA))
        parser.flush()

        packet_tree = parser.games[-1]
        self.game = EntityTreeExporter(packet_tree).export().game
        self.player_names = ['Strafos', 'strafos']
        self.card_data = self.get_card_data()

    def get_card_data(self):
        json_dir = "/home/zaibo/code/Hearthstone-Quest-Bot/plugins/SerpentHearthstoneGameAgent/files/cards.json"
        json_dir = r"C:\Users\Zaibo\Desktop\playground\sai\plugins\SerpentHearthstoneGameAgentPlugin\files\cards.json"
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
                    hand.add_card(entities.HandMinion(card_info['name'], id, card_info['cost'], card_in_hand.tags[GameTag.ZONE_POSITION], card_info['attack'], card_info['health'], mechanics))
                elif card_type == "SPELL":
                    hand.add_card(entities.HandSpell(card_info['name'], id, card_info['cost'], card_in_hand.tags[GameTag.ZONE_POSITION]))
                elif card_type == "WEAPON":
                    hand.add_card(entities.HandWeapon(card_info['name'], id, card_info['cost'], card_in_hand.tags[GameTag.ZONE_POSITION], card_info['attack'], card_info['durability']))
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
                            weapons.append(board_card)
                        elif card_type == 'MINION':
                            minions.append(board_card)
        return entities.Board(minions, weapons)

    def get_current_player(self):
        return self.game.current_player

    def update_state(self):
        hand = self.get_current_hand()
        turn = self.get_current_player()
        board = self.get_current_board()
        game_step = self.get_game_step()
        mana = self.get_current_mana()
        return hand, turn, board, game_step, mana

    def get_current_mana(self):
        players = self.game.players
        for player in players:
            if player.name in self.player_names:
                self.friendly_player = player
        return self.friendly_player.tags[GameTag.RESOURCES]
        # try:
        #     return friendly_player.tags[GameTag.RESOURCES]
        # except:
        #     return 0