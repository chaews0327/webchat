import logging

import aiohttp
import aiohttp_jinja2
from aiohttp import web
from faker import Faker

import asyncio
import json


log = logging.getLogger(__name__)
ws_key = web.AppKey("ws_key", dict[str, web.WebSocketResponse])


def get_random_name():
    fake = Faker()
    return fake.name()


def set_user_id(request, response):
    user_id = get_random_name()
    response.set_cookie('user_id', user_id, max_age=60*60*24)
    return user_id


async def handle_redis_message(app, pubsub):
    await pubsub.subscribe('chat_room')
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
                    

async def handle_websocket(request, user_id):
    ws_current = web.WebSocketResponse()
    ws_ready = ws_current.can_prepare(request)
    if not ws_ready.ok:
        return aiohttp_jinja2.render_template('index.html', request, {})   
    
    await ws_current.prepare(request)
    
    request.app[ws_key][user_id] = ws_current
    
    channel_name = 'chat_room'
    await request.app['redis'].publish(channel_name, json.dumps({'action': 'join', 'name': user_id}))
    
    await ws_current.send_json({'action': 'connect', 'name': user_id})
    
    try:
        while True:
            msg = await ws_current.receive()
            if msg.type == aiohttp.WSMsgType.TEXT:
                msg_data = {
                    'action': 'sent',
                    'name': user_id,
                    'message': msg.data
                }
                await request.app['redis'].publish(channel_name, json.dumps(msg_data))
            elif msg.type == aiohttp.WSMsgType.CLOSE:
                break
    except asyncio.CancelledError:
        pass
    finally:
        if user_id in request.app[ws_key]:
            del request.app[ws_key][user_id]
        log.info(f'{user_id} disconnected.')
        await request.app['redis'].publish(channel_name, json.dumps({'action': 'disconnect', 'name': user_id}))

    return ws_current


async def index(request):
    user_id = request.cookies.get('user_id')
    
    if not user_id:
        response = web.Response()
        user_id = set_user_id(request, response)
        return await handle_websocket(request, user_id)

    return await handle_websocket(request, user_id)