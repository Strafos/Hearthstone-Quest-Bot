from hslog import LogParser
from hslog.export import EntityTreeExporter
from io import StringIO
import json
import io
from hearthstone.enums import GameTag
from hearthstone.entities import Player

def card_data():
    json_file = io.open('cards.json', 'r', encoding='utf8')
    json_str = json_file.read()
    return json.loads(json_str)

def get_card_name(all_cards, card_id):
    for card in all_cards:
        if card['id'] == card_id:
            return card

def get_game(logs):
    parser = LogParser()

    parser.read(StringIO(logs))
    parser.flush()

    packet_tree = parser.games[-1]
    return EntityTreeExporter(packet_tree).export().game

def current_state(logs):
    game = get_game(logs)
    all_cards = card_data()

    hand = []
    for hand_card in game.in_zone(3):
        if hand_card.card_id:
            ID_card = get_card_name(all_cards, hand_card.card_id)
            hand.append((ID_card['name'], hand_card.tags[GameTag.ZONE_POSITION], ID_card['cost'], hand_card.card_id))
    hand.sort(key=lambda x: x[1])

    return hand, game.current_player

def get_state():
    log_dir = r"C:\Program Files (x86)\Hearthstone\Logs\Power.log"
    with open(log_dir, "r") as logs:
        lines = logs.readlines()
        data = ''.join(lines)
    hand, player = current_state(data)
    # for card in hand:
    #     print(card)
    # print(player)
    my_turn = player.name = 'strafos'
    return hand, my_turn

def get_current_board(self, logs):
        game = get_game(DATA)
        board = []
        all_cards = card_data()
        # Board: (Name, Position, Controller, Taunt)
        for board_card in game.in_zone(1):
            safe = board_card
            if type(board_card) != Card:
                continue
            if board_card.card_id and "HERO" not in board_card.card_id:
                ID_card = get_card_name(all_cards, board_card.card_id)
                if ID_card:
                    board.append((ID_card['name'], board_card.tags[GameTag.ZONE_POSITION], board_card.controller.name, board_card.tags[GameTag.TAUNT]))
        return(board)

hand, turn = get_state()
for card in hand:
    print(card)
print(len(hand))