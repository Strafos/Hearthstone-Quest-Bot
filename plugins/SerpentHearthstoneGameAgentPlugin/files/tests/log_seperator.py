import re
import io

class LogSeperator():
    
    match = "CREATE_GAME"
    def __init__(self, file):
        with io.open(file) as logs:
            k = 0
            for line in logs.readlines():
                if "GameState.DebugPrintPower() - CREATE_GAME" in line:
                    print(line)
                    k += 1
            print(k)

a = LogSeperator('/home/zaibo/code/Hearthstone-Quest-Bot/plugins/SerpentHearthstoneGameAgentPlugin/files/tests/many_games.log')
