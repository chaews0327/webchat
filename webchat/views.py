import aiohttp_session
from uuid import uuid4 as uuid
from chat_service import manage_websocket_connection


async def index(request):
    redis = request.app['redis']
    session = await aiohttp_session.get_session(request)
    user_id = session.get('user_id')

    if not user_id:
        user_id = str(uuid().hex)[:4]
        
        while await redis.sismember('user_ids', user_id):
            user_id = str(uuid().hex)[:4]
            
        await redis.sadd('user_ids', user_id)
        await redis.expire(user_id, 3600)
        
        session['user_id'] = user_id
        await redis.setex(f"session:{user_id}", 3600, "active")

    return await manage_websocket_connection(request, user_id)