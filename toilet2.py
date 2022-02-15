from pymongo import MongoClient
from fastapi import FastAPI
from fastapi import HTTPException
from typing import Optional
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from datetime import datetime

app = FastAPI()

myClient = MongoClient('mongodb://localhost', 27017)

db = myClient["toilet"]
collection = db["user"]

class Toilet(BaseModel):
    room: int
    state: int

allpeople = [0,0,0]
to_time = [0,600,600,600]

@app.put("room/checkandupdate")
def update(toilet : Toilet):
    check = collection.find_one({"room": toilet.room}, {"_id":0})
    if check["state"]==1 and toilet.state==0:
        query = {"room" : toilet.room}
        timein = datetime.now()
        timestatus=timein.strftime("%H:%M:%S")
        new = {"$set" : {"state": toilet.state,"time_in": timestatus}}
        collection.update_one(query,new)
        return {
            "result":"OK"
        }
    elif check["state"]==0 and toilet.state==1:
        query = {"room":toilet.room}
        allpeople[toilet.room]+=1
        timein=check["time_in"]
        hour,minute,second=timein.split(':')
        totaltimein = int(hour)*3600 + int(minute)*60 + int(second)
        cc = datetime.now()
        time_out = cc.strftime("%H:%M:%S")
        hourout,minuteout,secondout=timein.split(':')
        totaltimeout = int(hourout)*3600 + int(minuteout)*60 + int(secondout)
        total_est = totaltimeout - totaltimein
        to_time[toilet.room] += total_est
        esttime = to_time[toilet.room]/to_time_num[toilet.room]
        new = {"$set" : {"status":1,"time_est" : esttime}}
        collection.update_one(query, new)
        return {
            "result":"ok"
        }
# @app.post("/toilet")
# def get_input(toilet: Toilet):
     
