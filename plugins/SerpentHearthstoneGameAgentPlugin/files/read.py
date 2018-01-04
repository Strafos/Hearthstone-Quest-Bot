from hslog import LogParser
from hslog.export import EntityTreeExporter
from io import StringIO
import json
import io
from hearthstone.enums import GameTag

def card_data():
    json_file = io.open('card.json', 'r', encoding='utf8')
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

    packet_tree = parser.games[0]
    return EntityTreeExporter(packet_tree).export().game

def current_hand(logs):
    game = get_game(logs)
    all_cards = card_data()

    hand = []
    for hand_card in game.in_zone(3):
        if hand_card.card_id:
            ID_card = get_card_name(all_cards, hand_card.card_id)
            if ID_card:
                safe = hand_card
                hand.append((ID_card['name'], hand_card.tags[GameTag.ZONE_POSITION], ID_card['cost'], hand_card.card_id))
    return hand

log_dir = r"C:\Program Files (x86)\Hearthstone\Logs\Power.log"
with open(log_dir, "r") as logs:
    lines = logs.readlines()
    data = ''.join(lines)
hand = current_hand(data)
for card in hand:
    print(card)