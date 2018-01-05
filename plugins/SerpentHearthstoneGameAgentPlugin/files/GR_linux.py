from hslog import LogParser
from hslog.export import EntityTreeExporter
from io import StringIO
from hearthstone.enums import GameTag, Step
from hearthstone.entities import Player, Card

import json
import io

from board_state import DATA

class GameReader:

    def __init__(self):
        # log_dir = r"C:\Program Files (x86)\Hearthstone\Logs\Power.log"
        # with io.open(log_dir, "r", encoding='utf8') as logs:
        #     lines = logs.readlines()
        #     self.logs = ''.join(lines)
        parser = LogParser()

        # parser.read(StringIO(self.logs))
        parser.read(StringIO(DATA))
        parser.flush()

        packet_tree = parser.games[-1]
        self.game = EntityTreeExporter(packet_tree).export().game

        self.card_data = self.get_card_data()

    def get_card_data(self):
        json_dir = "/home/zaibo/code/Hearthstone-Quest-Bot/plugins/SerpentHearthstoneGameAgentPlugin/files/cards.json" 
        # json_dir = r"C:\Users\Zaibo\Desktop\playground\sai\plugins\SerpentHearthstoneGameAgentPlugin\files\cards.json"
        with io.open(json_dir, 'r', encoding='utf8') as json_file:
            json_str = json_file.read()
        return json.loads(json_str)

    def get_card_name(self, card_id):
        for card in self.card_data:
            if card['id'] == card_id:
                return card

    def get_game(self):
        return self.game

    def get_game_step(self):
        return self.game.tags[GameTag.STEP]

    def get_current_hand(self):
        # Hand: (Name, Hand Position, Cost, Card_ID)
        # When returned, Hand sorts by cost
        hand = []
        for hand_card in self.game.in_zone(3):
            card_id = hand_card.card_id
            if card_id:
                ID_card = self.get_card_name(card_id)
                hand.append((ID_card['name'], hand_card.tags[GameTag.ZONE_POSITION], ID_card['cost'], card_id))
        hand.sort(key=lambda x: x[2])

        return hand
    
    def get_current_player(self):
        return self.game.current_player

    def get_current_state(self):
        hand = self.get_current_hand()
        turn = self.get_current_player()
        board = self.get_current_board()
        game_step = self.get_game_step()
        mana = self.get_current_mana()
        return hand, turn, board, game_step, mana

    def get_current_board(self):
        board = []
        # Board: (Name, Position, Controller, Taunt)
        for board_card in self.game.in_zone(1):
            if type(board_card) != Card:
                continue
            id = board_card.card.id
            if id and "HERO" not in id:
                ID_card = self.get_card_name(id)
                if ID_card and ID_card['type'] != "HERO_POWER":
                    board.append((ID_card['name'], board_card.tags[GameTag.ZONE_POSITION], board_card.controller.name, board_card.tags[GameTag.TAUNT]))
        return board

    def get_current_mana(self):
        players = self.game.players
        for player in players:
            if player.name == 'strafos':
                friendly_player = player
        return player.tags[GameTag.RESOURCES]

gr = GameReader()
hand, turn, board, game_step, mana = gr.get_current_state()
print(hand)
print(turn)
print(board)
print(mana)