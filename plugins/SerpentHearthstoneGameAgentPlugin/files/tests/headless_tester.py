from serpent.game_agent import GameAgent

from board_state_data import board_state
from endgame_data import endgame
from midgame_data import midgame
from multi_taunt_data import taunts

game_agent = SerpentHearthstoneGameAgent(GameAgent)
game_agent.handle_play(None, True)