from serpent.game_agent import GameAgent

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
from serpent_Hearthstone_game_agent import SerpentHearthstoneGameAgent

from board_state_data import board_state
from endgame_data import endgame
from midgame_data import midgame

game_agent = SerpentHearthstoneGameAgent(GameAgent)

game_agent.handle_play(None, True)