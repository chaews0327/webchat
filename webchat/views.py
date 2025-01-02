import aiohttp_session
from faker import Faker
from chat_service import manage_websocket_connection


async def index(request):
    session = await aiohttp_session.get_session(request)
    user_id = session.get('user_id')

    if not user_id:
        user_id = Faker().name()
        session['user_id'] = user_id

    return await manage_websocket_connection(request, user_id)
