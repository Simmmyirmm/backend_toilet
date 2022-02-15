from pymongo import MongoClient

from fastapi import FastAPI, HTTPException
from typing import Optional
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
import datetime, time
from fastapi.middleware.cors import CORSMiddleware


client = MongoClient('mongodb://localhost', 27017) 

class Reservation(BaseModel):
    room_No : int

# TODO fill in database name
db = client["project"]

# TODO fill in collection name
toilet = db["toilet"]
toilet_savetime = db["toilet_savetime"]

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TODO complete all endpoint.
@app.get("/")
def get_root():  
    return "toilet"

@app.get("/get_room/{room_No}")
def get_room(room_No: int):  
    room = toilet.find_one({"room_No":room_No},{"_id":0})
    if room != None :
        return room
    raise HTTPException( status_code = 405 , detail = { "msg" : "no room" } )

@app.get("/get_time")
def get_time():  
    roomtime = toilet_savetime.find({},{"_id":0})
    if roomtime != [] :
        alltime = 0
        people = 0
        for i in roomtime :
            alltime += i["time"]
            people += i["number"]
        if people == 0 :
            return 0
        return alltime/people
    raise HTTPException( status_code = 405 , detail = { "msg" : "no room" } )

@app.get("/get_time/{room_No}")
def get_time(room_No: int):  
    roomtime = toilet_savetime.find_one({"room_No":room_No},{"_id":0})
    if roomtime != None :
        return roomtime
    raise HTTPException( status_code = 405 , detail = { "msg" : "no room" } )
    
    
@app.post("/make/{room_No}")
def make(room_No : int):
    room = toilet.find_one({"room_No":room_No},{"_id":0})
    if room != None :
        return room
    raise HTTPException( status_code = 405 , detail = { "msg" : "already have this room" } )
    


@app.put("/update_in")
def update_in(reservation: Reservation):
    room_No = reservation.room_No
    room = toilet.find_one({"room_No":room_No},{"_id":0})
    if room != None :
        if(room["status"]==1):
            raise HTTPException( status_code = 417 , detail = { "msg" : "Not Empty" } )
            '''return {
                "result" : "Not Empty"
            }'''
        myquery = {"room_No":room_No}
        newvalues = { "$set": { "status": 1,"datetime" : datetime.datetime.now() } }
        toilet.update_one(myquery, newvalues)
        return {
            "result" : "Success"
        }
    raise HTTPException( status_code = 405 , detail = { "msg" : "no room" } )
    
@app.put("/update_out")
def update_out(reservation: Reservation):
    room_No = reservation.room_No
    room = toilet.find_one({"room_No":room_No},{"_id":0})
    if room != None :
        room_savetime = toilet_savetime.find_one({"room_No":room_No},{"_id":0})
        if(room["status"]==0):
            raise HTTPException( status_code = 417 , detail = { "msg" : "No people in the room" } )
            '''return {
                "result" : "No people in the room"
            }'''
        myquery = {"room_No":room_No}
        x = (datetime.datetime.now() - room["datetime"]) 
        #print(type(x)) print(x)    print(y)
        y = x.total_seconds() 
        
        x = y + room_savetime["time"]
        newvalues1 = { "$set": { "status": 0} }
        newvalues2 = { "$set": { "time" : x, "number" : room_savetime["number"]+1 } }
        toilet.update_one(myquery, newvalues1)
        toilet_savetime.update_one(myquery,newvalues2)
        return{
            "result" : "Success"
        }
    raise HTTPException( status_code = 405 , detail = { "msg" : "no room" } )

'''toilet
_id : ...
room_No : int
status : ...
datetime : ...
'''

'''savetime
_id : ...
room_No : int
time : ...
number : ...
'''