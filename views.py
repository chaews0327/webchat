import logging

import aiohttp
import aiohttp_jinja2
from aiohttp import web
from faker import Faker

log = logging.getLogger(__name__)

ws_key = web.AppKey("ws_key", dict[str, web.WebSocketResponse])


def get_random_name():
    fake = Faker()
    return fake.name()


def set_user_id(request, response):
    user_id = get_random_name()
    response.set_cookie('user_id', user_id, max_age=60*60*24)
    return response


async def handle_websocket(request, user_id):
    ws_current = web.WebSocketResponse()
    ws_ready = ws_current.can_prepare(request)
    if not ws_ready.ok:
        return aiohttp_jinja2.render_template('index.html', request, {})   
    
    await ws_current.prepare(request)
    await ws_current.send_json({'action': 'connect', 'name': user_id})
    
    for ws in request.app[ws_key].values():
        await ws.send_json({'action': 'join', 'name': user_id})
        
    request.app[ws_key][user_id] = ws_current

    while True:
        msg = await ws_current.receive()

        if msg.type == aiohttp.WSMsgType.text:
            for ws in request.app[ws_key].values():
                if ws is not ws_current:
                    await ws.send_json(
                        {'action': 'sent', 'name': user_id, 'text': msg.data})
        else:
            break
        
    if user_id in request.app[ws_key]:
        del request.app[ws_key][user_id]
    log.info('%s disconnected.', user_id)
    for ws in request.app[ws_key].values():
        await ws.send_json({'action': 'disconnect', 'name': user_id})

    return ws_current


async def index(request):  
    user_id = request.cookies.get('user_id')
    
    if not user_id:
        response = web.Response()
        user_id = set_user_id(request, response)
        await handle_websocket(request, user_id)
        return response

    return await handle_websocket(request, user_id)