from hslog import LogParser
from hslog.export import EntityTreeExporter
from io import StringIO
from hearthstone.enums import GameTag, Step
from hearthstone.entities import Player, Card

import json
import io
import time

import entities
from hearthstone_AI import HearthstoneAI
import GameReader

AI = HearthstoneAI()
game_reader = GameReader.GameReader()

hand, turn, board, game_step, mana = game_reader.update_state()
if game_step == Step.BEGIN_MULLIGAN:
    # Mulligan step
    # time.sleep(4)
    mull = HearthstoneAI.get_mulligan(hand.hand)
    # time.sleep(4)
elif game_step == Step.FINAL_GAMEOVER:
    # Start new game
    # self.start_game(mouse)
    pass
elif turn:
    print(mana)
    chain, val = HearthstoneAI.play_card(hand, mana)
    print(chain)
    print(val)

    # while chain:
    #     print(mana)
    #     # print(hand.size, chain[0])
    #     # self.play_card(mouse, hand.size, chain[0])
    #     # time.sleep(3)
    #     print(chain)
    #     print(val)
    #     # hand, turn, board, game_step, mana = game_reader.update_state()
    #     hand = game_reader.get_current_hand()
    #     mana = game_reader.get_current_mana()
    #     chain, val = HearthstoneAI.play_card(hand, mana)
    #     time.sleep(3)
    
    ## ATTACK PHASE
    # Attacking strategy:
    # 1. Calculate chain of attack actions
    # 2. Execute first attack action and wait (in case of deathrattle summons)
    # 3. Repeat steps 1-2 until no minions can attack anymore
    # self.end_turn(mouse)