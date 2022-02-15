from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pydantic import BaseModel
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

MAXIMUM_ROOM = 3

app = FastAPI()
client = MongoClient('mongodb://localhost', 27017)
db = client["mini-project"]
collection = db["room"]


origins = [
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/start/{room_number}")
def start(room_number: int):
    # check room
    if room_number not in [i for i in range(1, MAXIMUM_ROOM+1)]:
        raise HTTPException(404, "Room not found")

    # check if room is currently in use or not
    room = collection.find({"room": room_number}).sort("_id", -1)[0]
    if room["done"] == 0:
        raise HTTPException(400, f"room {room_number} is currently in use")

    now = datetime.now()
    collection.insert_one({
        "room": room_number,
        "done": 0,
        "start": now.strftime("%Y-%m-%d %H:%M:%S"),
        "end": None,
        "total_time": None
    })
    return {
        "msg": f"room {room_number} is currently in use"
    }


@app.post("/end/{room_number}")
def end(room_number: int):
    # check room
    if room_number not in [i for i in range(1, MAXIMUM_ROOM+1)]:
        raise HTTPException(404, "Room not found")

    # check if room is currently in use or not
    room = collection.find({"room": room_number}).sort("_id", -1)[0]
    if room["done"] == 1:
        raise HTTPException(400, f"room {room_number} is empty now")

    now = datetime.now()
    room = collection.find({"room": room_number}).sort("_id", -1)[0]
    collection.update_one(
            {
                "room": room_number,
                "start": room["start"]
            }, 
            {
                "$set": {
                    "done": 1,
                    "end": now.strftime("%Y-%m-%d %H:%M:%S"),
                    "total_time": (now - datetime.strptime(room["start"], "%Y-%m-%d %H:%M:%S")).total_seconds()
                }
            }
        )

    return {
        "msg": f"room {room_number} is empty"
    }

@app.get("/room-status/{room_number}")
def room_status(room_number: int):
    if room_number not in [i for i in range(1, MAXIMUM_ROOM+1)]:
        raise HTTPException(404, "Room not found")

    room = collection.find({"room": room_number}).sort("_id", -1)[0]
    return {
        "room": room["room"],
        "done": room["done"],
        "start": room["start"],
        "end": room["end"],
        "total_time": room["total_time"]
    }

@app.get("/estimate")
def estimate():
    """Average time of all completed session in seconds."""
    room = collection.find({"done": 1})

    total_time = 0
    count = 0
    for r in room:
        total_time += r["total_time"]
        count += 1

    return {
        "estimate": total_time / count,
        "completed_session": count
    }