from flask import Flask
from gomoku import gomoku
from os import chdir, popen

app = Flask(__name__)
app.secret_key = "659c3f0694471be93c48282dc201a3d3a51ca106c4ee6a4da5a8a30989386fd4"
app.register_blueprint(gomoku, url_prefix='/gomoku')


@app.route("/reload-website")
def reload():
    chdir("/home/RuochenFu/site")
    popen("git stash")
    popen("git stash drop")
    return popen("git pull https://github.com/GomokuApp/GomokuApp.git").read()


# noinspection PyUnresolvedReferences
import login
