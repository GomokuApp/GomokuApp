
# A very simple Flask Hello World game for you to get started with...

from flask import Blueprint, render_template, redirect, request, jsonify
from util import Player
from secrets import token_hex
from enum import Enum
from time import time

game = Blueprint('gomoku', __name__)

gomoku_games = {}


timeout_seconds = 600

class GomokuColor(Enum):
    BLACK = "black"
    WHITE = "white"

class GomokuGame:
    def __init__(self, game_id):
        self.game_id = game_id
        self.online_players = {GomokuColor.BLACK: None, GomokuColor.WHITE: None}
        self.board = [[None for i in range(15)] for i in range(15)]
        self.turn = GomokuColor.BLACK
        self.ended = False
        self.won_color = None

    def is_full(self):
        return all(self.online_players.values())

    def is_empty(self):
        return not any(self.online_players.values())

    def add_player(self, player, color):
        if not self.ended:
            self.online_players[color] = player

    def contains_player(self, ip):
        for color, player in self.online_players.items():
            if player is None:
                continue
            if player.ip == ip:
                return True
        return False

    def refresh_player(self, ip):
        if not self.ended:
            for color, player in self.online_players.items():
                if player is None:
                    continue
                if player.ip == ip:
                    self.online_players[color].refresh()

    def remove_offline_players(self):
        for color, player in self.online_players.items():
            if player is None:
                continue
            if time() - player.last_checkin > timeout_seconds:
                self.online_players[color] = None
                continue

    def place_piece(self, row, column, color):
        if not self.ended:
            if self.online_players[self.turn] == None:
                return
            if self.online_players[self.turn].ip != get_client_ip():
                return
            if (self.board[row][column] == None):
                self.board[row][column] = color
                self.check_wins(row, column)
                self.turn = GomokuColor.BLACK if self.turn == GomokuColor.WHITE else GomokuColor.WHITE

    def check_wins(self, row, column):
        color = self.board[row][column];
        def is_same(row, column, color):
            if not (0 <= row < 15 and 0 <= column < 15):
                return False
            return self.board[row][column] == color

        for correction in range(5):
            if all([is_same(row - i + correction, column, color) for i in range(5)]):
                self.ended = True
                break
            if all([is_same(row, column - i + correction, color) for i in range(5)]):
                self.ended = True
                break
            if all([is_same(row - i + correction, column - i + correction, color) for i in range(5)]):
                self.ended = True
                break
            if all([is_same(row + i - correction, column - i + correction, color) for i in range(5)]):
                self.ended = True
                break

        if self.ended:
            print("GAME ENDED! ", row, ", ", column, ", color: ", color)
            self.won_color = color

def get_client_ip():
    return request.headers['X-Real-IP']

@game.before_request
def check_offline_player():
    for id, game in gomoku_games.copy().items():
        game.remove_offline_players()
        if game.is_empty():
            del gomoku_games[id]

def create_game_for_player(game_id):
    if game_id not in gomoku_games.keys():
        gomoku_games[game_id] = GomokuGame(game_id)
        print("CREATED GAME " + game_id)
        print("GAMES: ", gomoku_games)
    game = gomoku_games[game_id]
    return game

@game.route('/<game_id>')
def gomoku_game(game_id):
    create_game_for_player(game_id)
    return render_template("gomoku.html", game_id=game_id)

@game.route('/')
def redirect_to_random_game():
    return redirect(token_hex(6))

@game.route('/api/<game_id>/refresh')
def check_online(game_id):
    game = create_game_for_player(game_id)
    game.refresh_player(get_client_ip())
    possible_client_color = [color for color, player in game.online_players.items() if player != None and player.ip == get_client_ip()]
    status = {
        "current_players" : {color.value : player.ip if player is not None else None for color, player in game.online_players.items()},
        "is_your_turn" : game.online_players[game.turn] != None and game.online_players[game.turn].ip == get_client_ip(),
        "your_color" : possible_client_color[0].value if len(possible_client_color) == 1 else game.turn.value if len(possible_client_color) == 2 else None,
        "spectating" : get_client_ip() in game.online_players.values(),
        "current_board" : [[None if point == None else point.value for point in line] for line in game.board],
        "ended": game.ended,
        "won_color": game.won_color.value if game.won_color is not None else None
    }

    if game.ended:
        del gomoku_games[game_id]

    return jsonify(status)

@game.route('/api/<game_id>/<color>/join')
def join_player(game_id, color):
    game = create_game_for_player(game_id)
    game.add_player(Player(get_client_ip()), GomokuColor(color))
    return ""

@game.route('/api/<game_id>/place_piece/<row>/<column>')
def place_piece(game_id, row, column):
    game = create_game_for_player(game_id)

    game.place_piece(int(row), int(column), game.turn)

    return ""


