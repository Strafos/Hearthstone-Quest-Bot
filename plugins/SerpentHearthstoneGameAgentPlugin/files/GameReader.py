from hslog import LogParser
from hslog.export import EntityTreeExporter
from hearthstone.enums import GameTag, Step
from hearthstone.entities import Player, Card

import json
import io 
import time

import entities
from tests.board_state_data import board_state

# Reads information from game logs using hslog and relays to the GameAgent
class GameReader:
    def __init__(self, os, linux_log=board_state):
        self.os = os
        parser = LogParser()

        if self.os == "Windows":
            log_dir = r"C:\Program Files (x86)\Hearthstone\Logs\Power.log"
            with io.open(log_dir, "r", encoding='utf8') as logs:
                k = 0
                lines = logs.readlines()
                for line in lines:
                    k += 1
                    if "GameState.DebugPrintPower() - CREATE_GAME" in line:
                        start = k
                parsed_lines = lines[start-1:]
                self.logs = ''.join(parsed_lines)
            parser.read(io.StringIO(self.logs))
        elif self.os == "Linux":
            parser.read(io.StringIO(linux_log))
            self.linux_log = linux_log
        parser.flush()

        packet_tree = parser.games[-1]
        while True:
            try:
                self.game = EntityTreeExporter(packet_tree).export().game
            except:
                print("Trapped")
                continue
            else:
                break
        self.player_names = ['Strafos', 'strafos']
        self.card_data = self.get_card_data()
        self.friendly_player, self.enemy_player = self.read_players()

    ## Read card.json for Hearthstone card data
    def get_card_data(self):
        if self.os == "Windows":
            json_dir = r"C:\Users\Zaibo\Desktop\playground\sai\plugins\SerpentHearthstoneGameAgentPlugin\files\cards.json"
        elif self.os == "Linux":
            json_dir = "/home/zaibo/code/Hearthstone-Quest-Bot/plugins/SerpentHearthstoneGameAgentPlugin/files/cards.json"
        else:
            raise Exception("Invalid OS")
        with io.open(json_dir, 'r', encoding='utf8') as json_file:
            json_str = json_file.read()
        return json.loads(json_str)

    ## Access json for card data given card_id
    def get_card_info(self, card_id):
        for card in self.card_data:
            if card['id'] == card_id:
                return card

    def get_current_player(self):
        return self.game.current_player

    def get_game(self):
        return self.game

    def get_game_step(self):
        return self.game.tags.get(GameTag.STEP, 0)

    # Return Hand of BaseCard objects sorted by increasing cost
    def get_current_hand(self, hp, board):
        hand = entities.Hand()
        for card_in_hand in self.game.in_zone(3):
            id = card_in_hand.card_id
            if id:
                card_info = self.get_card_info(id)
                card_type = card_info['type']
                tags = card_in_hand.tags
                if card_type == "MINION":
                    minion = entities.HandMinion(
                        card_info['name'], 
                        id, 
                        tags.get(GameTag.COST, 0), 
                        tags.get(GameTag.ZONE_POSITION, 0), 
                        card_info['attack'], 
                        card_info['health'], 
                        card_info.get('mechanics', None))
                    hand.add_card(minion)
                elif card_type == "SPELL":
                    spell = entities.HandSpell(
                        card_info['name'], 
                        id, 
                        tags.get(GameTag.COST, 0), 
                        tags.get(GameTag.ZONE_POSITION, 0),
                        card_info.get('playRequirements', None))
                    hand.add_card(spell)
                elif card_type == "WEAPON":
                    weapon = entities.HandWeapon(
                        card_info['name'], 
                        id, 
                        tags.get(GameTag.COST, 0), 
                        tags.get(GameTag.ZONE_POSITION, 0), 
                        card_info['attack'], 
                        card_info['durability'])
                    hand.add_card(weapon)
        if hp and board.enemy:
            hero_power = entities.HeroPower('Hero Power', 2, -2, 'Hunter', board.enemy.health)
            hand.add_card(hero_power)
        hand.sort_by_cost()
        return hand
    
    ## Create board object
    def get_current_board(self):
        minions = []
        weapons = []
        heroes = []
        for board_card in self.game.in_zone(1):
            if type(board_card) == Card:
                id = board_card.card_id
                if id:
                    card_info = self.get_card_info(id)
                    card_type = card_info['type']
                    if card_info and card_type != "HERO_POWER":
                        tags = board_card.tags
                        if card_type == 'WEAPON':
                            weapon = entities.BoardWeapon(
                                card_info['name'], 
                                id, 
                                tags.get(GameTag.ZONE_POSITION, 0), 
                                board_card.controller, 
                                tags.get(GameTag.ATK, 0), 
                                tags.get(GameTag.DURABILITY, 0))
                            weapons.append(weapon)
                        elif card_type == 'MINION':
                            exhaust = tags.get(GameTag.EXHAUSTED, not tags.get(GameTag.CHARGE, 0))
                            if tags.get(GameTag.FROZEN):
                                exhaust = 1
                            minion = entities.BoardMinion(
                                card_info['name'], 
                                id, 
                                tags[GameTag.ZONE_POSITION], 
                                board_card.controller, 
                                tags.get(GameTag.ATK, 0), 
                                tags.get(GameTag.HEALTH, 0), 
                                tags.get(GameTag.TAUNT, 0), 
                                exhaust)
                            minions.append(minion)
                        elif card_type == 'HERO':
                            hero = entities.BoardHero(
                                card_info['name'],
                                id,
                                None,
                                board_card.controller,
                                tags.get(GameTag.HEALTH, 30) - tags.get(GameTag.DAMAGE, 0),
                                tags.get(GameTag.EXHAUSTED, 0)
                            )
                            heroes.append(hero)
        return entities.Board(minions, heroes, weapons)

    ## Update Game object by rereading logs
    def update_state(self, hp=1):
        parser = LogParser()
        if self.os == "Windows":
            log_dir = r"C:\Program Files (x86)\Hearthstone\Logs\Power.log"
            with io.open(log_dir, "r", encoding='utf8') as logs:
                lines = logs.readlines()
                self.logs = ''.join(lines)
            parser.read(io.StringIO(self.logs))
        elif self.os == "Linux":
            parser.read(io.StringIO(self.linux_log))
        parser.flush()

        packet_tree = parser.games[-1]
        while True:
            try:
                self.game = EntityTreeExporter(packet_tree).export().game
            except:
                print("Trapped")
                continue
            else:
                break

        packet_tree = parser.games[-1]
        self.friendly_player, self.enemy_player = self.read_players()

        turn = self.get_current_player().name in self.player_names
        board = self.get_current_board()
        hand = self.get_current_hand(hp, board)
        game_step = self.get_game_step()
        mana = self.get_current_mana()
        return hand, turn, board, game_step, mana

    def read_players(self):
        friendly = None
        enemy = None
        for player in self.game.players:
            if player.name in self.player_names:
                friendly = player
            else:
                enemy = player
        return friendly, enemy

    def get_current_mana(self):
        if self.friendly_player:
            tags = self.friendly_player.tags
            return tags.get(GameTag.RESOURCES, 0) - tags.get(GameTag.RESOURCES_USED, 0) + tags.get(GameTag.TEMP_RESOURCES, 0)
        return 0