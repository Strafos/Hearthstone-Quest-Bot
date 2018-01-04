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

# Necessary?
# class GameState:
#     def __init__(self, player, hand, board):

# Reads information from game logs using hslog and relays to the GameAgent
class GameReader:

    def __init__(self):
        log_dir = r"C:\Program Files (x86)\Hearthstone\Logs\Power.log"
        with io.open(log_dir, "r", encoding='utf8') as logs:
            lines = logs.readlines()
            self.logs = ''.join(lines)
        parser = LogParser()

        parser.read(StringIO(self.logs))
        parser.flush()

        packet_tree = parser.games[-1]
        self.game = EntityTreeExporter(packet_tree).export().game

        self.card_data = get_card_data

    def get_card_data(self):
        json_dir = r"C:\Users\Zaibo\Desktop\playground\sai\plugins\SerpentHearthstoneGameAgentPlugin\files\cards.json"
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
        game = self.get_game(self.logs)
        return game.tags[GameTag.STEP]

    def get_current_hand(self):
        # Hand: (Name, Hand Position, Cost, Card_ID)
        hand = []
        for hand_card in self.game.in_zone(3):
            card_id = hand_card.card.id
            if card_id:
                ID_card = self.get_card_name(card_id)
                hand.append((ID_card['name'], hand_card.tags[GameTag.ZONE_POSITION], ID_card['cost'], card_id))
        hand.sort(key=lambda x: x[2])

        return hand
    
    def get_current_player(self):
        return self.game.current_player

    def get_current_state(self):
        hand = self.get_current_hand
        turn = self.get_current_player
        board = self.get_current_board
        game_step = self.get_game_step
        mana = self.get_mana
        return hand, turn, board, game_step, mana

    def get_current_board(self):
        board = []
        # Board: (Name, Position, Controller, Taunt)
        for board_card in self.game.in_zone(1):
            if type(board_card) != Card:
                continue
            if board_card.card_id and "HERO" not in board_card.card_id:
                ID_card = get_card_name(self.card_data, board_card.card_id)
                if ID_card:
                    board.append((ID_card['name'], board_card.tags[GameTag.ZONE_POSITION], board_card.controller.name, board_card.tags[GameTag.TAUNT]))
        return board

    def get_current_mana(self):
        players = game.players
        for player in players:
            if player.name == 'strafos':
                friendly_player = player
        return player.tags[GameTag.RESOURCES]


# Handles actions that require thinking
class HearthstoneAI:
    def __init__(self):
        pass

    @staticmethod
    def get_mulligan(hand):
        mull = []
        for card in hand:
            if card[2] >= 2:
                mull.append(card[1])
        return mull


# Preforms all actions
class SerpentHearthstoneGameAgent(GameAgent):
    X_RES = 840
    Y_RES = 473

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.frame_handlers["PLAY"] = self.handle_play

        self.frame_handler_setups["PLAY"] = self.setup_play

        self.analytics_client = None

    def handle_start_menu(self, mouse, option):
        menu_items = {
            "PLAY" : (422, 142),
            "SOLO" : (419, 176),
            "ARENA" : (421, 209),
            "TAVERN" : (418, 247),
            "QUESTS" : (230, 414),
            "PACKS" : (336, 396),
            "COLLECTION" : (453, 392)
        }
        mouse.click()
        mouse.move(menu_items[option][0], menu_items[option][1], .25)
        mouse.click()
        time.sleep(2)
    
    def handle_deck_select(self, mouse, option):
        items = [
            (0, 0), 
            (208, 127), (313, 130), (420, 127), # 1 2 3
            (203, 229), (314, 223), (418, 227), # 4 5 6
            (203, 324), (311, 328), (421, 328), # 7 8 9 
        ]
        # (612, 22), # wild_toggle 10
        # (572, 72), # casual mode 11
        # (655, 80), # ranked 12
        next_page = (492, 228) # next 13
        prev_page = (132, 225) # prev 14
        if option > 9:
            option -= 9
            mouse.move(next_page[0], next_page[1], .25)
            mouse.click()
        else:
            mouse.move(prev_page[0], prev_page[1], .25)
            mouse.click()


        selected_option = items[option]
        mouse.move(selected_option[0], selected_option[1], .25)
        mouse.click()
    
    def end_turn(self, mouse, mull=False):
        if mull:
            mouse.move(432, 369, .25)
        else:
            mouse.move(678, 216, .25)
        mouse.click()
    
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
        self.move_to_board(mouse)
    
    def start_game(self, mouse):
        mouse.move(612, 385, .25)
        mouse.click()
        time.sleep(3)
    
    def move_to_board(self, mouse):
        board = (235, 159)
        mouse.move(board[0], board[1], .2)
        mouse.click()

    def setup_play(self):
        mouse = InputController(game = self.game)
        self.handle_start_menu(mouse, "PLAY")
        self.handle_deck_select(mouse, 13)

    def handle_play(self, game_frame):
        mouse = InputController(game = self.game)
        AI = HearthstoneAI()
        game_reader = GameReader()

        hand, board, turn, game_step, mana = game_reader.get_current_state()
        print("Game step: " + str(game_reader.get_game_step()))
        if game_step == Step.BEGIN_MULLIGAN:
            # Mulligan step
            time.sleep(4)
            mull = HearthstoneAI.get_mulligan(hand)
            self.mull_card(mouse, hand, mull)
            time.sleep(4)
        elif game_step == Step.FINAL_GAMEOVER:
            # Start new game
            self.start_game(mouse)
        elif turn:
            # Turn logic
            handsize = len(hand)
            time.sleep(4)
            for card in hand:
                self.play_card(mouse, handsize, card[1])
                hand, turn = game_reader.get_state()
                handsize = len(hand)
                # print("Handsize: " + str(handsize))
                # print("card_pos: " + str(card_pos))
            time.sleep(50)
            self.end_turn(mouse)
            time.sleep(4)