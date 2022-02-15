from pymongo import MongoClient
from fastapi import FastAPI, Query
from fastapi import HTTPException
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import time


app = FastAPI()

myClient = MongoClient('mongodb://localhost', 27017)

db = myClient["toilet"]
collection1 = db["user1"]
collection2 = db["user2"]
collection3 = db["user3"]

class Toilet(BaseModel):
    room: int
    state: int


@app.post("/toilet")
def update_input(toilet : Toilet):
    print(toilet.room)
    print(toilet.state)
    if (toilet.room == 1):
        toiletroom = collection1
    if (toilet.room == 2):
        toiletroom = collection2
    if (toilet.room == 3):
        toiletroom = collection3
    
    timein = time.time()

    if (toilet.state == 1):
        fromdatabase = toiletroom.find_one({"room" : toilet.room},{"_id":0})
        print(timein)
        query = {"room": toilet.room}
        new = {"$set": {"state": toilet.state , "timein": timein , "timeall": fromdatabase["timeall"] , "people" : fromdatabase["people"]}}
        toiletroom.update_one(query,new)
    elif (toilet.state == 0):
        fromdatabase = toiletroom.find_one({"room" : toilet.room},{"_id":0})
        print(fromdatabase["timeall"])
        query = {"room" : toilet.room}
        new = {"$set": {"state": toilet.state , "timein" : timein , "timeall" : fromdatabase["timeall"] + timein - fromdatabase["timein"],"people" : fromdatabase["people"] + 1}}
        toiletroom.update_one(query,new)
    return {
        "result":"ok"
    }


@app.get("/toilet/{name}")
def get_output(name:str):
    if (name == '1'):
        toiletroom = collection1
    if (name == '2'):
        toiletroom = collection2
    if (name== '3'):
        toiletroom = collection3
        
    result = toiletroom.find_one({"room" : int(name)} , {"_id":0})
    result["estimate"] = result["timeall"] / result["people"]
    return result
    
    
    
