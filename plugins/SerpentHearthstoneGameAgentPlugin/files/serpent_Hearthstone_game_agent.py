from serpent.game_agent import GameAgent
from serpent.input_controller import MouseButton, InputController

from hearthstone.enums import GameTag, Step, PlayState

import json
import io
import time
from io import StringIO
import hashlib

import entities
import locations
from hearthstone_AI import HearthstoneAI
import GameReader

# Preforms in-game actions using input controller
class SerpentHearthstoneGameAgent(GameAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.frame_handlers["PLAY"] = self.handle_play
        self.frame_handler_setups["PLAY"] = self.setup_play
        self.analytics_client = None

    def handle_start_menu(self, mouse, option):
        menu_items = locations.menu_items
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
        card_location = locations.mulligan_locations

        if hand.size == 3:
            hand_loc = card_location[0]
        else:
            hand_loc = card_location[1]
        for mull_pos in mull:
            mouse.move(hand_loc[mull_pos][0], hand_loc[mull_pos][1], .25)
            mouse.click()
        self.end_turn(mouse, True)

    # attack_pos examples: 
    # (5, 3)
    # (2, 0)
    def attack(self, mouse, ally_board_size, enemy_board_size, attack_pos):
        card_locations_x = locations.board_locations_x
        enemy_y = 170
        ally_y = 258

        # Friendly
        if attack_pos[0] == 0:
            # Friendly Hero coordinates
            x1 = 416
            y1 = 357
        else:
            x1 = card_locations_x[ally_board_size][attack_pos[0]]
            y1 = ally_y
        mouse.move(x1, y1, .25)
        mouse.click()

        # Enemy
        if attack_pos[1] == 0:
            x2 = 416
            y2 = 88
        else:
            x2 = card_locations_x[enemy_board_size][attack_pos[1]]
            y2 = enemy_y
        mouse.move(x2, y2, .25)
        mouse.click()

    def play_card(self, mouse, handsize, card_pos):
        hand_card_locations = locations.hand_card_locations
        if card_pos == -1:
            self.hero_power(mouse)

        if card_pos == 0 or card_pos > handsize:
            return None

        coords = hand_card_locations[handsize][card_pos]
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
    
    def hero_power(self, mouse):
        loc = locations.hero_power_loc
        mouse.move(loc[0], loc[1], .25)
        mouse.click()

    def concede(self, mouse, game_reader):
        for i in range(1):
            hand, turn, board, game_step, mana = game_reader.update_state()
            while game_step != Step.BEGIN_MULLIGAN:
                self.start_game(mouse)
                hand, turn, board, game_step, mana = game_reader.update_state()
            mouse.move(820, 464, .25)
            mouse.click()
            mouse.move(412, 171, .25)
            mouse.click()
            time.sleep(3)


    def setup_play(self):
        mouse = InputController(game = self.game)
        self.handle_start_menu(mouse, "PLAY")
        # self.handle_deck_select(mouse, 13)

    def handle_play(self, game_frame):
        mouse = InputController(game = self.game)
        AI = HearthstoneAI()
        game_reader = GameReader.GameReader("Windows")

        # with open('Logs/wins.log', 'r') as f:
        with io.open(r'Logs\wins.log', 'r') as f:
            data = []
            for line in f.readlines():
                string = line.split(' ')
                data.append((string[-1].strip()))
            wins, losses, total, hash = (int)(data[0]), (int)(data[1]), (int)(data[2]), data[3]

        hashcode = hash
        hand, turn, board, game_step, mana = game_reader.update_state()
        if board.ally and board.enemy:
            hash_input = board.ally.name + board.enemy.name
            hashcode = hashlib.md5(hash_input.encode('utf-8')).hexdigest()
        # print(game_step)
        if game_step == Step.BEGIN_MULLIGAN:
            # Mulligan step
            time.sleep(2)
            mull = HearthstoneAI.get_mulligan(hand.hand)
            self.mull_card(mouse, hand, mull)
            # time.sleep(4)
        elif game_step == Step.FINAL_GAMEOVER:
            # Start new game
            self.start_game(mouse)
        elif turn:
            ## CARD PLAY PHASE
            # 1. Calculate best chain of cards to play using HearthstoneAI.play_cards
            # 2. Play first card and wait in case of drawing card
            # 3. Repeat steps 1-2
            time.sleep(2)
            chain, val= HearthstoneAI.play_card(hand, mana)
            timeout = 0
            hp = 1
            while chain and turn and len(board.ally_minions) != 7 and timeout < 11:
                self.play_card(mouse, hand.size, chain[0])
                hp = chain[0] != -1
                time.sleep(1)
                hand, turn, board, game_step, mana = game_reader.update_state(hp)
                if mana == 0:
                    break
                chain, val = HearthstoneAI.play_card(hand, mana)
                timeout += 1
            
            ## ATTACK PHASE
            # Attacking strategy:
            # 1. Calculate chain of attack actions
            # 2. Execute first attack action and wait (in case of deathrattle summons)
            # 3. Repeat steps 1-2 until no minions can attack anymore
            hand, turn, board, game_step, mana = game_reader.update_state()
            chain = HearthstoneAI.simple_smorc(board)
            timeout = 0
            while chain and turn and timeout < 10:
                timeout += 1
                self.attack(mouse, len(board.ally_minions), len(board.enemy_minions), chain[0])
                time.sleep(1)
                hand, turn, board, game_step, mana = game_reader.update_state()
                chain = HearthstoneAI.simple_smorc(board)

            ## Second play phase (in case board was full before)
            chain, val= HearthstoneAI.play_card(hand, mana)
            timeout = 0
            hp = 1
            while chain and turn and len(board.ally_minions) != 7 and timeout < 11:
                self.play_card(mouse, hand.size, chain[0])
                hp = chain[0] != -1
                time.sleep(1)
                hand, turn, board, game_step, mana = game_reader.update_state(hp)
                if mana == 0:
                    break
                chain, val = HearthstoneAI.play_card(hand, mana)
                timeout += 1
            chain, val= HearthstoneAI.play_card(hand, mana)
            
            if mana >= 2:
                self.hero_power(mouse)

            self.end_turn(mouse)
        
        playstate = game_reader.friendly_player.tags.get(GameTag.PLAYSTATE, None)
        if playstate == PlayState.WON or playstate == PlayState.LOST:
            print(hash)
            print(hashcode)
            if hashcode != hash:
                if playstate == PlayState.WON:
                    self.concede(mouse, game_reader)
                    wins += 1
                elif playstate == PlayState.LOST:
                    losses += 1
                total += 1
                print("Win ratio: " + str(wins/total))
                with io.open(r'Logs/wins.log', 'w') as f:
                    f.write('Wins: ' + str(wins) + '\n')
                    f.write('Losses: ' + str(losses) + '\n')
                    f.write('Total: ' + str(total) + '\n')
                    f.write('Hash: ' + hashcode + '\n')