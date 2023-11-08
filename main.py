from flask import Flask
from gomoku import gomoku

app = Flask(__name__)
app.register_blueprint(gomoku, url_prefix='/gomoku')
