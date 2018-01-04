from serpent.game_agent import GameAgent
from serpent.input_controller import MouseButton, InputController

from hslog import LogParser
from hslog.export import EntityTreeExporter
from io import StringIO
from hearthstone.enums import GameTag, Step
from hearthstone.entities import Player

import json
import io
import time

class GameReader:
    # TODO clean up self.logs and logs

    def __init__(self):
        log_dir = r"C:\Program Files (x86)\Hearthstone\Logs\Power.log"
        with io.open(log_dir, "r", encoding='utf8') as logs:
            lines = logs.readlines()
            self.logs = ''.join(lines)
        self.game = self.get_game(self.logs)

    def get_card_data(self):
        json_dir = r"C:\Users\Zaibo\Desktop\playground\sai\plugins\SerpentHearthstoneGameAgentPlugin\files\cards.json"
        with io.open(json_dir, 'r', encoding='utf8') as json_file:
            json_str = json_file.read()
        return json.loads(json_str)

    def get_card_name(self, all_cards, card_id):
        for card in all_cards:
            if card['id'] == card_id:
                return card

    def get_game(self, logs):
        parser = LogParser()

        parser.read(StringIO(logs))
        parser.flush()

        packet_tree = parser.games[-1]
        self.game = EntityTreeExporter(packet_tree).export().game
        return self.game

    def get_game_step(self, logs=None):
        if logs:
            game = self.get_game(logs)
        else:
            game = self.get_game(self.logs)
        return game.tags[GameTag.STEP]

    def get_current_state(self, logs):
        game = self.get_game(logs)
        all_cards = self.get_card_data()

        # Hand: (Name, Hand Position, Cost, Card_ID)
        hand = []
        for hand_card in game.in_zone(3):
            if hand_card.card_id:
                ID_card = self.get_card_name(all_cards, hand_card.card_id)
                hand.append((ID_card['name'], hand_card.tags[GameTag.ZONE_POSITION], ID_card['cost'], hand_card.card_id))
        hand.sort(key=lambda x: x[2])

        return hand, game.current_player

    def get_state(self):
        hand, player = self.get_current_state(self.logs)
        my_turn = player.name == 'strafos'
        return hand, my_turn

class SerpentHearthstoneGameAgent(GameAgent):
    X_RES = 840
    Y_RES = 473

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.frame_handlers["PLAY"] = self.handle_play

        self.frame_handler_setups["PLAY"] = self.setup_play

        self.analytics_client = None

    def click_play(self, mouse):
        mouse.click()
        mouse.move(400, 180, .25)
        mouse.click()
        time.sleep(2)
        mouse.move(600, 460, .25)
        mouse.click()
    
    def end_turn(self, mouse, mull=False):
        if mull:
            mouse.move(432, 369, .25)
        else:
            mouse.move(678, 216, .25)
        mouse.click()
    
    def get_mulligan(self, hand):
        mull = []
        for card in hand:
            if card[2] >= 2:
                mull.append(card[1])
        return mull

    def mull_card(self, mouse, hand, mull):
        card_location = [
            [(0, 0), (274, 221), (421, 220), (573, 221)],
            [(0, 0), (252, 214), (370, 214), (480, 220), (585, 220)]
        ]

        print(len(hand))
        if len(hand) == 3:
            hand_loc = card_location[0]
        else:
            hand_loc = card_location[1]
        for mull_pos in mull:
            mouse.move(hand_loc[mull_pos][0], hand_loc[mull_pos][1], .25)
            mouse.click()
        self.end_turn(mouse, True)


    def play_card(self, mouse, handsize, card_pos):
        card_location = [
            [(0, 0)],
            [(0, 0), (400, 430)],
            [(0, 0), (375, 432), (423, 435)],
            [(0, 0), (344, 429), (405, 432), (458, 438)],
            [(0, 0), (316, 443), (375, 432), (427, 432), (487, 437)],
            [(0, 0), (309, 443), (353, 435), (398, 436), (442, 439), (508, 448)],
            [(0, 0), (295, 440), (340, 439), (370, 440), (416, 438), (462, 436), (502, 439)],
            [(0, 0), (293, 446), (323, 441), (358, 440), (396, 432), (428, 432), (467, 430), (503, 447)],
            [(0, 0), (284, 456), (316, 444), (346, 441), (375, 437), (405, 428), (439, 435), (466, 437), (505, 448)],
            [(0, 0), (281, 455), (309, 448), (340, 442), (365, 439), (390, 436), (419, 431), (447, 431), (471, 438), (509, 450)],
            [(0, 0), (275, 462), (300, 455), (328, 448), (352, 444), (376, 435), (396, 434), (426, 436), (450, 437), (472, 444), (503, 446)]
        ]

        if card_pos == 0 or card_pos > handsize:
            return None

        coords = card_location[handsize][card_pos]
        mouse.move(coords[0], coords[1], .3)
        mouse.click()
        self.move_board(mouse)
    
    def move_board(self, mouse):
        board = (235, 159)
        mouse.move(board[0], board[1], .2)
        mouse.click()

    def setup_play(self):
        mouse = InputController(game = self.game)

    def handle_play(self, game_frame):
        mouse = InputController(game = self.game)
        game_reader = GameReader()
        hand, turn = game_reader.get_state()
        game_step = game_reader.get_game_step()
        print(game_reader.get_game_step())
        if game_step == Step.BEGIN_MULLIGAN:
            time.sleep(10)
            mull = self.get_mulligan(hand)
            self.mull_card(mouse, hand, mull)
            time.sleep(2)
        elif turn:
            handsize = len(hand)
            time.sleep(4)
            for card in hand:
                self.play_card(mouse, handsize, card[1])
                hand, turn = game_reader.get_state()
                handsize = len(hand)
                print("Handsize: " + str(handsize))
                # print("card_pos: " + str(card_pos))
            time.sleep(2)
            self.end_turn(mouse)