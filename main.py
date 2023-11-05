from flask import Flask
from gomoku import game

app = Flask(__name__)
app.register_blueprint(game, url_prefix='/gomoku')