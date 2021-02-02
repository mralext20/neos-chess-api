from gameManager import ChessGame, GameManager


import sanic
from sanic import response
from sanic.websocket import WebSocketProtocol
from sanic.request import Request
import uuid
from classes import GameOptions

app = sanic.Sanic(name="Neos Chess Websocket")
gm = GameManager()


@app.route("/newgame", methods=["POST"])
async def new_game(request: Request):
    """
    takes body json for the ai's piece color, and the AI's difficulty, as in `{'ai_is_white': false, 'ai_diff': 10}`
    """
    opts = GameOptions(**request.json)

    uid = str(uuid.uuid4())
    gm.start_game(uid, opts)
    return response.text(uid)


# @app.route("/debug")
# async def debug(request: Request):
#     pass
#     return response.text("ok")


app.run()
