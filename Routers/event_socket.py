from fastapi import APIRouter
from sqlalchemy.orm import Session
import oauth2, models
from database import engine
import socketio
import random, logging
from sqlalchemy import desc, update

router = APIRouter(prefix="/ws/events", tags=['event_websocket'])
blogger = logging.getLogger('backend_logger')

sio_server = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins=[])
sio_app = socketio.ASGIApp(socketio_path='sockets', socketio_server=sio_server)

connected_users = set()

async def broadcast_alert(alert: str):
    for user in connected_users:
        await sio_server.emit('alert', {'message': alert}, to=user)

async def broadcast_count_data():
    data = [{ 'camera_number': x, 'camera_name': f"Entry{x}", 'entry': random.randint(0, 5000), 'exit': random.randint(0, 5000), 'total': random.randint(0, 10000)} for x in range(5)]
    for user in connected_users:
        await sio_server.emit('updateCountData', data, to=user)

async def check_for_event(db):
    # await broadcast_count_data()

    send_alerts = []
    new_alerts = db.query(models.Events.camera_number, models.Events.event, models.Events.id).\
                filter_by(wb_created=False).order_by(desc(models.Events.id)).limit(10).all()

    for alert in new_alerts:
        send_alerts.append(alert)

    stmt = update(models.Events).where(models.Events.wb_created == False).values(wb_created=True)
    db.execute(stmt)
    db.commit()

    for alert in send_alerts:
        caption = f"New Alert for camera {alert[0]} {alert[1]}"
        await broadcast_alert(caption)


@sio_server.event
async def connect(sid, environ, auth):
    token = auth['token']
    if not token:
        return False  # No token provided, reject the connection.

    with Session(engine) as db:
        oauth2.get_current_user(token=token, db=db)
        connected_users.add(sid)
        print(sid,'connected successfully')

@sio_server.event
async def disconnect(sid):
    if sid in connected_users:
        connected_users.remove(sid)