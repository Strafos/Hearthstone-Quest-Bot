from hslog import LogParser
from hslog.export import EntityTreeExporter
from io import StringIO
from hearthstone.enums import GameTag, Step
from hearthstone.entities import Player, Card

import json
import io
import time
import hashlib

import entities
from hearthstone_AI import HearthstoneAI
import GameReader

from tests.mid_game_mana import data
from tests.coin_state import coins
from tests.board_state_data import board_state
from tests.endgame_data import endgame
from tests.midgame_data import midgame
from tests.multi_taunt_data import taunts
from tests.weapon_face import weapon_face
from tests.before import before
from tests.after import after

def general_bot_test():
    AI = HearthstoneAI()
    game_reader = GameReader.GameReader("Linux")
    # game_reader = GameReader.GameReader("Windows")

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
        # print(mana)
        chain, val = HearthstoneAI.play_card(hand, mana)
        # print(chain)
        # print(val)

        while chain:
            # print(hand.size, chain[0])
            # self.play_card(mouse, hand.size, chain[0])
            # time.sleep(3)
            print("Hand size: " + str(hand.size))
            print("chain: " + str(chain))
            # print(val)
            hand, turn, board, game_step, mana = game_reader.update_state()
            print("mana: " + str(mana))
            chain, val = HearthstoneAI.play_card(hand, mana)
            time.sleep(3)
        
        ## ATTACK PHASE
        # Attacking strategy:
        # 1. Calculate chain of attack actions
        # 2. Execute first attack action and wait (in case of deathrattle summons)
        # 3. Repeat steps 1-2 until no minions can attack anymore
        # self.end_turn(mouse)

def test_simple_smorcAI():
    AI = HearthstoneAI()
    # game_reader = GameReader.GameReader("Linux")
    game_reader = GameReader.GameReader("Windows")

    hand, turn, board, game_step, mana = game_reader.update_state()
    print(AI.simple_smorc(board))
    
def get_enemy_hp():
    AI = HearthstoneAI()
    game_reader = GameReader.GameReader("Linux")
    hand, turn, board, game_step, mana = game_reader.update_state()

    game = game_reader.get_game()
    for i in game.in_zone(1):
        print(i)
        if type(i) == Card and 'HERO' in i.card_id:
            for j in i.tags:
                print(j)
            print(i.tags[GameTag.HEALTH])
    # p1 = (game.players[0])
    # print(p1.tags)
    # for i in p1.tags:
    #     print(i)

def won():
    a = time.time()
    AI = HearthstoneAI()
    game_reader = GameReader.GameReader("Windows")
    b = time.time()
    print(b-a)
    # hand, turn, board, game_step, mana = game_reader.update_state()
    game = game_reader.get_game()
    print(game.tags)
    for i in game.tags:
        print(i)
    print(game.tags[GameTag.STATE])

def log_writing_test():
    f = open('Logs/test.log', 'w')
    f.write('Wins: 20\n')
    f.write('Loses: 10\n')
    f.write('Total: 5\n')

def log_read_test():
    f = open('Logs/test.log', 'r')
    wins = []
    for line in f.readlines():
        string = line.split(' ')
        wins.append((int)(string[-1].strip()))
    print(wins)
    print(hashlib.md5(b"Hello").hexdigest())

def hash_test():
    AI = HearthstoneAI()
    game_reader = GameReader.GameReader("Windows")
    hand, turn, board, game_step, mana = game_reader.update_state()
    print(board.ally)
    playstate = game_reader.friendly_player.tags.get(GameTag.PLAYSTATE, None)
    print(playstate)

def str_test():
    AI = HearthstoneAI()
    game_reader = GameReader.GameReader("Linux")
    hand, turn, board, game_step, mana = game_reader.update_state()

    print(hand)
    print(board)

def board_test():
    AI = HearthstoneAI()
    game_reader = GameReader.GameReader("Linux", board_state)
    hand, turn, board, game_step, mana = game_reader.update_state()
    print(board.weapon.name)
    print(board.weapon.position)

    print(board)
    # print(AI.smarter_smorc(board))

def play_phase_test():
    AI = HearthstoneAI()
    game_reader = GameReader.GameReader("Linux", board_state)
    hand, turn, board, game_step, mana = game_reader.update_state()
    t1 = time.time()
    chain, val = HearthstoneAI.play_card(hand, mana)
    t2 = time.time()
    print(t2-t1)
    print(chain)

def mana_test():
    AI = HearthstoneAI()
    game_reader = GameReader.GameReader("Linux", board_state)
    hand, turn, board, game_step, mana = game_reader.update_state()

    print(mana)

def multi_taunt():
    game_reader = GameReader.GameReader("Linux", taunts)
    hand, turn, board, game_step, mana = game_reader.update_state()
    print(board)
    # for i in board.ally_minions:
    #     print(i)

    chain = HearthstoneAI.smarter_smorc(board)
    print(chain)

def weapon():
    game_reader = GameReader.GameReader("Linux", before)
    hand, turn, board, game_step, mana = game_reader.update_state()

    chain = HearthstoneAI.smarter_smorc(board)
    print(chain)

    game_reader = GameReader.GameReader("Linux", after)
    hand, turn, board, game_step, mana = game_reader.update_state()

    chain = HearthstoneAI.smarter_smorc(board)
    print(chain)

def coin():
    game_reader = GameReader.GameReader("Linux", coins)
    hand, turn, board, game_step, mana = game_reader.update_state()

    game = game_reader.get_game()
    players = game.players
    print(players)
    me = players[0]

    print(mana)

def mid_gamemana():
    game_reader = GameReader.GameReader("Linux", data)
    hand, turn, board, game_step, mana = game_reader.update_state()
    print(hand)

    chain, val = HearthstoneAI.play_card(hand, mana)
    print(chain)
    print(val)

def value_trade_test():
    game_reader = GameReader.GameReader("Linux", board_state)
    hand, turn, board, game_step, mana = game_reader.update_state()
    print(board)

    trades = HearthstoneAI.value_trade(board)
    print(trades)

value_trade_test()