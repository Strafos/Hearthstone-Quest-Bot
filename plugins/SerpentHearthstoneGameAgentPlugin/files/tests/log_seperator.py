import re
import io

from GameReader import GameReader

# from tests.sample import coins
from tests.coin_state import coins

class LogSeperator():
    
    match = "CREATE_GAME"
    def __init__(self, file):
        with io.open(file, "r", encoding='utf8') as logs:
            k = 0
            lines = logs.readlines()
            for line in lines:
                k += 1
                if "GameState.DebugPrintPower() - CREATE_GAME" in line:
                    start = k
            parsed_lines = lines[start-1:]

            gr = GameReader("Linux", ''.join(parsed_lines))
            # gr = GameReader("Linux", (coins))
            


a = LogSeperator('/home/zaibo/code/Hearthstone-Quest-Bot/plugins/SerpentHearthstoneGameAgentPlugin/files/tests/many_games.log')