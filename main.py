import asyncio
import uuid
from uuid import UUID

import sanic
from Chessnut.game import InvalidMove
from sanic import response
from sanic.request import Request
from websockets.protocol import WebSocketCommonProtocol
from classes import ChessGame, GameOptions
from config import baseurl, default_port
from gameManager import GameManager

app = sanic.Sanic(name="Neos Chess Websocket")
gm = GameManager()


@app.route(f"{baseurl}/newgame", methods=["POST"])
async def new_game(request: Request):
    """
    takes body json for the ai's piece color, and the AI's difficulty, as in `{'ai_is_white': false, 'ai_diff': 10}`
    """
    opts = GameOptions(**request.json)

    uid = uuid.uuid4()
    gm.start_game(uid, opts)
    move = ""
    if opts.ai_is_white:
        move = await gm.do_ai_move(uid)
    return response.text(f"{uid} {move}")


@app.route(f"{baseurl}/move/<uid:uuid>/<move:[a-h][1-8][a-h][1-8][r,b,q,n]?>", methods=["POST"])
async def move(request: Request, uid: UUID, move: str):
    if uid not in gm.games:
        return response.text("invalid game ID", 400)
    try:
        return response.text(await gm.make_move(uid, move))
    except InvalidMove:
        return response.text("invalid move", 400)


@app.route(f"{baseurl}/endgame/<uid:uuid>", methods=["POST"])
async def endgame(request: Request, uid: UUID):
    if uid not in gm.games:
        return response.text("invalid game ID", 400)
    del gm.games[uid]
    return response.text("deleted")


@app.route(f"{baseurl}/listGames")
async def listgames(request: Request):
    return response.json({str(i): gm.games[i].game.get_fen() for i in gm.games})


@app.route(f"{baseurl}/board/<uid:uuid>")
async def board(request: Request, uid: UUID):
    if uid not in gm.games:
        return response.text("invalid game ID", 400)
    return response.text(gm.games[uid].game.get_fen())


@app.websocket(f'{baseurl}/spectate/<uid:uuid>')
async def spectate(request: Request, ws: WebSocketCommonProtocol, uid: UUID):
    async def informMoves(game: ChessGame):
        await ws.send(game.game.get_fen())

    game = gm.games[uid]
    game.subscribers.append(informMoves)
    await ws.send(game.game.get_fen())
    while uid in gm.games.keys():
        await asyncio.sleep(10)


if __name__ == "__main__":
    app.run(port=default_port)
