#Importing Libraries
from flask import Flask, jsonify, request, make_response
from flask_restful import Api, Resource
import os
from pymongo import MongoClient
import bcrypt

#Initializing App
app = Flask(__name__)
api = Api(app)

#Initializing Database using function for PyTest
client = None
db = None
Num_of_Users = None

def get_db():
    global client, db, Num_of_Users
    if client is None:
        client = MongoClient("mongodb://db:27017")
        db = client.SentenceDB
        Num_of_Users = db["Users"]
    return Num_of_Users

#Registration of Users
class Register(Resource):
    def post(self):
        users = get_db()
        postedData = request.get_json()
        #Get Data from the Request
        username = postedData["username"]
        password = postedData["password"]
        #Now store it in DB after Hashing the password.
        hashed_pw = bcrypt.hashpw(password.encode("utf8"),bcrypt.gensalt())
        users.insert_one({
            "Username" : username,
            "Password" : hashed_pw,
            "Sentence" : "",
            "Tokens" : 6
        })
        retJson = {
            "Message" : "You have successfully Signed Up!"
        }
        return make_response(jsonify(retJson), 200)

#Storing the Sentence in DB
class Store(Resource):
    def post(self):
        users = get_db()
        #Step 1: Get the posted data
        postedData = request.get_json()

        #Step 2: Read the Data from the request
        username = postedData["username"]
        password = postedData["password"]
        sentence = postedData["sentence"]

        #Step 3: Verify the username and password
        correctpw = verifyPW(username,password) # Need to define the function
        if not correctpw:
            retJson = {
                "Message" : "Something is not correct!"
            }
            return make_response(jsonify(retJson), 302)
        
        #Step 4: Check the number of tokens
        num_tokens = countTokens(username) # Need to define the function
        if num_tokens <=0:
            retJson = {
                "Message" : "No Tokens left!"
            }
            return make_response(jsonify(retJson), 301)
        
        #Step 5: Add the sentence to the database
        users.update_one(
            {
                "Username" : username
            },
            {"$set":{
                "Sentence": sentence,
                "Tokens" : num_tokens-1
            }}
        )
        retJson = {
                "Message" : "Sentence Saved Successfully!"
            }
        return make_response(jsonify(retJson), 200)






        
