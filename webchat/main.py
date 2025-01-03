import jinja2
import aiohttp_jinja2
import aiohttp
from aiohttp import web
import aiohttp_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from views import index
from chat_service import broadcast_message_to_clients, ws_key
import redis.asyncio as redis
import asyncio
import os


async def init_app():

    app = web.Application()

    app[ws_key] = {}
    app['redis'] = await redis.from_url('redis://redis:6379')
    app['redis_pubsub_task'] = asyncio.create_task(
        broadcast_message_to_clients(app, app['redis'].pubsub()))

    app.on_shutdown.append(shutdown)

    secret_key = b'Thirty  two  length  bytes  key.'
    aiohttp_session.setup(app, EncryptedCookieStorage(secret_key))

    aiohttp_jinja2.setup(
        app, loader=jinja2.FileSystemLoader(os.getcwd() + '/webchat/template'))

    app.router.add_get('/', index)

    return app


async def shutdown(app):
    app['redis_pubsub_task'].cancel()

    try:
        await app['redis_pubsub_task']
    except asyncio.CancelledError:
        pass

    for ws in app[ws_key].values():
        await ws.close(code=aiohttp.WSCloseCode.GOING_AWAY)

    await app['redis'].close()


async def get_app():
    """Used by aiohttp-devtools for local development."""
    import aiohttp_debugtoolbar
    app = await init_app()
    aiohttp_debugtoolbar.setup(app)
    return app


def main():
    app = init_app()
    web.run_app(app, reuse_port=True)


if __name__ == '__main__':
    main()
