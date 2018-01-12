from serpent.game_agent import GameAgent
from serpent.input_controller import MouseButton, InputController

from hearthstone.enums import GameTag, Step
# from hearthstone.entities import Player, Card

import json
import io
import time
from io import StringIO

import entities
from hearthstone_AI import HearthstoneAI
import GameReader


# TODO remove Log folder

# Preforms in-game actions using input controller
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

        if hand.size == 3:
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
        return
        self.handle_start_menu(mouse, "PLAY")
        self.handle_deck_select(mouse, 13)

    def handle_play(self, game_frame):
        mouse = InputController(game = self.game)
        AI = HearthstoneAI()
        game_reader = GameReader.GameReader("Windows")

        hand, turn, board, game_step, mana = game_reader.update_state()
        print(game_step)
        if game_step == Step.BEGIN_MULLIGAN:
            # Mulligan step
            time.sleep(4)
            mull = HearthstoneAI.get_mulligan(hand.hand)
            self.mull_card(mouse, hand, mull)
            time.sleep(4)
        elif game_step == Step.FINAL_GAMEOVER:
            # Start new game
            self.start_game(mouse)
        elif turn:
            ## CARD PLAY PHASE
            chain, val= HearthstoneAI.play_card(hand, mana)
            time.sleep(5)
            while chain and turn:
                # 1. Calculate best chain of cards to play using HearthstoneAI.play_cards
                # 2. Play first card and wait in case of drawing card
                # 3. Repeat steps 1-2
                self.play_card(mouse, hand.size, chain[0])
                time.sleep(3)
                hand, turn, board, game_step, mana = game_reader.update_state()
                if mana == 0:
                    break
                chain, val = HearthstoneAI.play_card(hand, mana)
            
            ## ATTACK PHASE
            # Attacking strategy:
            # 1. Calculate chain of attack actions
            # 2. Execute first attack action and wait (in case of deathrattle summons)
            # 3. Repeat steps 1-2 until no minions can attack anymore
            self.end_turn(mouse)
            time.sleep(2)