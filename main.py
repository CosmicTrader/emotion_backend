from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import logging
import json

from Routers import auth, user, camera, events, event_socket, student, course, reports
from Routers.event_socket import sio_app, check_for_event
import models
from database import engine
from backend_utils import initialise_change, get_ip
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

with open('backend_values.json', 'r+') as f:
    backend_values = json.loads(f.read())

blogger = logging.getLogger('backend_logger')
blogger.setLevel(backend_values['log_level'])
file_handler = logging.FileHandler(filename='backend_log.log', mode='a', encoding='utf-8')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
file_handler.setFormatter(formatter)
blogger.addHandler(file_handler)

app = FastAPI()

origins = ["*"]
methods = ["*"]
headers = ["*"]

app.add_middleware(CORSMiddleware, allow_origins=origins,
                   allow_credentials=True, allow_methods=methods, allow_headers=headers)

app.include_router(user.router)
app.include_router(reports.router)
app.include_router(student.router)
app.include_router(auth.router)
app.include_router(camera.router)
app.include_router(events.router)
app.include_router(event_socket.router)
app.include_router(course.router)

app.mount("/ws", app = sio_app)
# app.mount("/camera_feed", StaticFiles(directory="camera"), name='camera')

with Session(engine) as db:
    initialise_change(db)
    host = get_ip(db)


# async def periodic_function():
#     with Session(engine) as db:
#         while True:
#             print('getting new values')
#             await check_for_event(db)
#             await asyncio.sleep(10)

# @app.on_event("startup")
# async def startup_event():
#     asyncio.create_task(periodic_function())

if __name__ == '__main__':
    uvicorn.run(app=app, port=8000, host=host)