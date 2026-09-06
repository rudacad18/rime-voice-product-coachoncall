import os
import uuid

from aiohttp import web
from dotenv import load_dotenv
from livekit import api

load_dotenv()


async def token(request: web.Request) -> web.Response:
    room = request.query.get("room")
    if not room:
        return web.json_response({"error": "room is required"}, status=400)

    identity = f"player-{uuid.uuid4().hex[:8]}"
    access_token = (
        api.AccessToken()
        .with_identity(identity)
        .with_name("Football player")
        .with_grants(api.VideoGrants(room_join=True, room=room))
        .to_jwt()
    )
    return web.json_response({"token": access_token})


app = web.Application()
app.router.add_get("/token", token)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("TOKEN_SERVER_PORT", "8000")))