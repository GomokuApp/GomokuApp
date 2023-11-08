from flask import Flask
from gomoku import gomoku
from os import chdir, popen

app = Flask(__name__)
app.register_blueprint(gomoku, url_prefix='/gomoku')


@app.route("reload-website")
def reload():
    chdir("/home/RuochenFu/site")
    popen("git stash")
    popen("git stash drop")
    return popen("git pull https://github.com/GomokuApp/GomokuApp.git")
