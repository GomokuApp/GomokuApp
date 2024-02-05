# A very simple Flask Hello World game for you to get started with...

from flask import Blueprint, render_template, redirect, request, jsonify
from user import User, GuestUser, get_current_user
from secrets import token_hex
from enum import Enum
from time import time
from typing import Optional
from urllib.parse import quote

gomoku: Blueprint = Blueprint('gomoku', __name__)

timeout_seconds: int = 600


class GomokuColor(Enum):
    BLACK = "black"
    WHITE = "white"


class GomokuGame:
    game_id: str
    online_players: dict[GomokuColor, Optional[User]]
    board: list[list[Optional[GomokuColor]]]
    turn: GomokuColor
    ended: bool
    won_color: Optional[GomokuColor]

    def __init__(self, game_id: str):
        self.game_id = game_id
        self.online_players = {GomokuColor.BLACK: None, GomokuColor.WHITE: None}
        self.board = [[None for _ in range(15)] for _ in range(15)]
        self.turn = GomokuColor.BLACK
        self.ended = False
        self.won_color = None

    def is_full(self) -> bool:
        return all(self.online_players.values())

    def is_empty(self) -> bool:
        return not any(self.online_players.values())

    def add_player(self, player: User, color) -> None:
        if not self.ended:
            self.online_players[color] = player

    def refresh_player(self, player: User) -> None:
        if self.ended:
            return

        player.refresh()

    def remove_offline_players(self) -> None:
        for color, player in self.online_players.items():
            if player is None:
                continue
            if time() - player.last_checkin > timeout_seconds:
                self.online_players[color] = None
                continue

    def place_piece(self, row, column, color) -> None:
        if self.ended:
            return
        if self.online_players[self.turn] != get_current_user():
            return
        if self.board[row][column] is None:
            self.board[row][column] = color
            self.check_wins(row, column)
            self.turn = GomokuColor.BLACK if self.turn == GomokuColor.WHITE else GomokuColor.WHITE

    def check_wins(self, row, column) -> None:
        def is_same(x, y, reference_color):
            if not (0 <= x < 15 and 0 <= y < 15):
                return False
            return self.board[x][y] == reference_color

        color: GomokuColor = self.board[row][column]

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


gomoku_games: dict[str, GomokuGame] = {}


def get_client_ip() -> str:
    return request.headers['X-Real-IP'] \
        if 'X-Real-IP' in request.headers \
        else request.remote_addr  # When run on local


@gomoku.before_request
def check_offline_player():
    for code, game in gomoku_games.copy().items():
        game.remove_offline_players()
        if game.is_empty():
            del gomoku_games[code]


def create_game_for_player(game_id) -> GomokuGame:
    if game_id not in gomoku_games.keys():
        gomoku_games[game_id] = GomokuGame(game_id)
        print("CREATED GAME " + game_id)
        print("GAMES: ", gomoku_games)
    game = gomoku_games[game_id]
    return game


@gomoku.route('/<game_id>')
def gomoku_game(game_id):
    create_game_for_player(game_id)
    return render_template("gomoku.html", game_id=game_id, url=quote(request.full_path))


@gomoku.route('/')
def redirect_to_random_game():
    return redirect(token_hex(6))


@gomoku.route('/api/<game_id>/refresh')
def check_online(game_id):
    game = create_game_for_player(game_id)
    game.refresh_player(get_current_user())  # Get current player?
    possible_client_color = [color for color, player in game.online_players.items() if
                             player == get_current_user()]
    status = {
        "current_players": {color.value: player and player.get_displayed_name() 
                            for color, player in game.online_players.items()},
        "is_your_turn":
            game.online_players[game.turn] != get_current_user(),
        "your_color": possible_client_color[0].value if len(possible_client_color) == 1 else game.turn.value if len(
            possible_client_color) == 2 else None,
        "spectating": get_client_ip() in game.online_players.values(),
        "current_board": [[None if point is None else point.value for point in line] for line in game.board],
        "ended": game.ended,
        "won_color": game.won_color and game.won_color.value
    }

    if game.ended:
        del gomoku_games[game_id]

    return jsonify(status)


@gomoku.route('/api/<game_id>/<color>/join')
def join_player(game_id, color):
    game = create_game_for_player(game_id)
    game.add_player(get_current_user(), GomokuColor(color))
    return ""


@gomoku.route('/api/<game_id>/place_piece/<row>/<column>')
def place_piece(game_id, row, column):
    game = create_game_for_player(game_id)

    game.place_piece(int(row), int(column), game.turn)

    return ""
