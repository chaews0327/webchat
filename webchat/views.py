import aiohttp_session
from uuid import uuid4 as uuid
from chat_service import manage_websocket_connection


async def index(request):
    session = await aiohttp_session.get_session(request)
    user_id = session.get('user_id')

    if not user_id:
        # user_id = Faker().name()
        user_id = uuid().hex
        session['user_id'] = str(user_id)[:4]

    return await manage_websocket_connection(request, user_id)
