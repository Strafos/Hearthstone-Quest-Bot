from serpent.game_agent import GameAgent
from serpent.input_controller import MouseButton, InputController
import time

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

    def get_card_location(self, handsize, card):
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
        board = (235, 159)

        if card == 0 or card > handsize:
            return None

        coords = card_location[handsize][card]
        return coords

    def setup_play(self):
        mouse = InputController(game = self.game)
        # self.click_play(mouse)

    def handle_play(self, game_frame):
        print("Hello")        

        # Visual Debugger
        # for i, game_frame in enumerate(self.game_frame_buffer.frames):
        #     self.visual_debugger.store_image_data(
        #         game_frame.frame,
        #         game_frame.frame.shape,
        #         str(i)
        #     