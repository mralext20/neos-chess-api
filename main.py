import uuid
from Chessnut.game import InvalidMove

import sanic
from sanic import response
from sanic.request import Request

from classes import GameOptions
from gameManager import GameManager
from uuid import UUID

app = sanic.Sanic(name="Neos Chess Websocket")
gm = GameManager()


@app.route("/newgame", methods=["POST"])
async def new_game(request: Request):
    """
    takes body json for the ai's piece color, and the AI's difficulty, as in `{'ai_is_white': false, 'ai_diff': 10}`
    """
    opts = GameOptions(**request.json)

    uid = uuid.uuid4()
    gm.start_game(uid, opts)
    move = ""
    if opts.ai_is_white is None:
        move = await gm.do_ai_move(uid)
    return response.text(f"{uid}{move}")


@app.route("/move/<uid:uuid>/<move:[a-h][1-8][a-h][1-8]>", methods=["POST"])
async def move(request: Request, uid: UUID, move: str):
    if uid not in gm.games:
        return response.text("invalid game ID", 400)
    try:
        return response.text(await gm.make_move(uid, move))
    except InvalidMove:
        return response.text("invalid move", 400)


@app.route("/endgame/<uid:uuid>")
async def endgame(request: Request, uid: UUID):
    if uid not in gm.games:
        return response.text("invalid game ID", 400)
    del gm.games[uid]
    return response.text("deleted")


# @app.route("/debug")
# async def debug(request: Request):
#     pass
#     return response.text("ok")


app.run()
