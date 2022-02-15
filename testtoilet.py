from fastapi import FastAPI , HTTPException
from pymongo import MongoClient
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

myclient = MongoClient("localhost",27017)

db = myclient["toilet"]
collection = db["room"]

    
@app.post("/toilet/start/{room}")
def start(room :int ):
    room = collection.find({"room":room})
    if (room["done"] == 0):
        return {
            "result":"roomfull"
        }
    now = datetime.now()
    collection.insert_one(
        {
            "room" : room,
            "start": now,
            "done" : 0,
            "end" : None,
            "total_time": None
        }
    )



@app.post("/toilet/end/{room}")
def end(room :int):
    room = collection.find({"room" : room})
    if room["done"] == 1:
        return {
            "result":"roomempty"
        }
    now = datetime.now()
    room = collection.find({"room" : room})
    collection.update_one(
            {
                "room": room,
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
    
@app.get("/roomstatus/{room}")
def roomstatus(room :int):
    room = collection.find({"room": room})
    return {
        "room" : room,
        "start" : room["start"],
        "done" : room["done"],
        "end" : room["end"],
        "total_time": room["total_time"]
    }

@app.get("/estimated")
def estimated():
    room = collection.find({"done" : 1})
    total_time = 0
    people = 0
    for i in room:
        total_time += room["total_time"]
        people += 1
    return {
        "estimated time" : total_time/people,
        "allpeople": people
    }