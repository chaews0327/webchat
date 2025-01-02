import logging
import aiohttp
import aiohttp_jinja2
import aiohttp_session
from aiohttp import web
from faker import Faker
import asyncio
import json


log = logging.getLogger(__name__)
ws_key = web.AppKey("ws_key", dict[str, web.WebSocketResponse])
CHANNEL = 'chat_room'


async def broadcast_message_to_clients(app, pubsub):
    await pubsub.subscribe(CHANNEL)
    while True:
        msg = await pubsub.get_message(ignore_subscribe_messages=True)
        if msg:
            msg_data = json.loads(msg['data'].decode('utf-8'))

            sender_name = msg_data.get('name')
            action = msg_data.get('action')

            for user_id, ws in app[ws_key].items():
                if action == 'join' and user_id == sender_name:
                    continue
                if action == 'sent' and user_id == sender_name:
                    continue
                await ws.send_json(msg_data)


async def publish_to_channel(request, user_id, action, message=None):
    msg_data = {'action': action, 'name': user_id}

    if message:
        msg_data['message'] = message

    await request.app['redis'].publish(CHANNEL, json.dumps(msg_data))


async def manage_websocket_connection(request, user_id):
    ws_current = web.WebSocketResponse()
    ws_ready = ws_current.can_prepare(request)
    if not ws_ready.ok:
        return aiohttp_jinja2.render_template('index.html', request, {})

    await ws_current.prepare(request)
    request.app[ws_key][user_id] = ws_current

    await publish_to_channel(request, user_id, 'join')
    await ws_current.send_json({'action': 'connect', 'name': user_id})

    try:
        while True:
            msg = await ws_current.receive()
            if msg.type == aiohttp.WSMsgType.TEXT:
                await publish_to_channel(request, user_id, 'sent', msg.data)
            elif msg.type == aiohttp.WSMsgType.CLOSE:
                break
    except asyncio.CancelledError:
        pass
    finally:
        if user_id in request.app[ws_key]:
            del request.app[ws_key][user_id]
        log.info(f'{user_id} disconnected.')
        await publish_to_channel(request, user_id, 'disconnect')

    return ws_current


async def index(request):
    session = await aiohttp_session.get_session(request)
    user_id = session.get('user_id')

    if not user_id:
        user_id = Faker().name()
        session['user_id'] = user_id

    return await manage_websocket_connection(request, user_id)
