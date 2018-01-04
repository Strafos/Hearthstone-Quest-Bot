from serpent.game_agent import GameAgent
from serpent.input_controller import MouseButton, InputController
import time

from hslog import LogParser
from hslog.export import EntityTreeExporter
from io import StringIO
import json
import io
from hearthstone.enums import GameTag
from hearthstone.entities import Player

def card_data():
    # json_dir = r"C:\Users\Zaibo\Desktop\playground\sai\plugins\SerpentHearthstoneGameAgent\files\cards.json"
    json_dir = r"C:\Users\Zaibo\Desktop\playground\sai\plugins\SerpentHearthstoneGameAgentPlugin\files\cards.json"
    json_file = io.open(json_dir, 'r', encoding='utf8')
    json_str = json_file.read()
    json_file.close()
    return json.loads(json_str)

def get_card_name(all_cards, card_id):
    for card in all_cards:
        if card['id'] == card_id:
            return card

def get_game(logs):
    parser = LogParser()

    parser.read(StringIO(logs))
    parser.flush()

    packet_tree = parser.games[-1]
    return EntityTreeExporter(packet_tree).export().game

def current_state(logs):
    game = get_game(logs)
    all_cards = card_data()

    hand = []
    for hand_card in game.in_zone(3):
        if hand_card.card_id:
            ID_card = get_card_name(all_cards, hand_card.card_id)
            hand.append((ID_card['name'], hand_card.tags[GameTag.ZONE_POSITION], ID_card['cost'], hand_card.card_id))
    hand.sort(key=lambda x: x[2])

    return hand, game.current_player

def get_state():
    log_dir = r"C:\Program Files (x86)\Hearthstone\Logs\Power.log"
    with open(log_dir, "r") as logs:
        lines = logs.readlines()
        data = ''.join(lines)
    hand, player = current_state(data)
    # for card in hand:
    #     print(card)
    # print(player)
    my_turn = player.name == 'strafos'
    return hand, my_turn

class SerpentHearthstoneGameAgent(GameAgent):

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
    
    def end_turn(self, mouse):
        mouse.move(678, 216, .25)
        mouse.click()

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

        print("Handsize: " + str(handsize))
        print("card_pos: " + str(card_pos))
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
        hand, turn = get_state()
        if turn:
            handsize = len(hand)
            time.sleep(3)
            for card in hand:
                self.play_card(mouse, handsize, card[1])
                handsize = len(hand)
                hand, turn = get_state()
            time.sleep(2)
            self.end_turn(mouse)