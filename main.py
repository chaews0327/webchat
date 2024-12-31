import logging

import jinja2

import aiohttp_jinja2
from aiohttp import web
from views import index, ws_key

import redis.asyncio as redis

import os


async def init_app():

    app = web.Application()

    app[ws_key] = {}
    app['redis'] = await redis.from_url('redis://localhost:6379')

    app.on_shutdown.append(shutdown)

    aiohttp_jinja2.setup(
        app, loader=jinja2.FileSystemLoader(os.getcwd() + '/template'))

    app.router.add_get('/', index)

    return app


async def shutdown(app):
    # TODO
    await app['redis'].close()
    


async def get_app():
    """Used by aiohttp-devtools for local development."""
    import aiohttp_debugtoolbar
    app = await init_app()
    aiohttp_debugtoolbar.setup(app)
    return app


def main():
    logging.basicConfig(level=logging.DEBUG)

    app = init_app()
    web.run_app(app)


if __name__ == '__main__':
    main()