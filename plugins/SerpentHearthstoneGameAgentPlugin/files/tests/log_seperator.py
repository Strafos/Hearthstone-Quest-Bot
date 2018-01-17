import re
import io

class LogSeperator():
    
    match = "CREATE_GAME"
    def __init__(self, file):
        with io.open(file) as logs:
            pass