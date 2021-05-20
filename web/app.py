from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
api = Api(app)

client = MongoClient("mogodb://db:27017")
db = client.BankAPI
users = db["Users"]

def UserExist(username):
    if users.find({"Username": username}).count()==0:
        return False
    else:
        return True

class Register(Resource):
    def POST(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]

        if UserExist(username):
            retJson ={
                "status": 301,
                "msg": "Username already exist"
            }
            return jsonify(retJson)
        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        user.insert({
            "Username": username,
            "Password": password,
            "Own": 0,
            "Debt": 0
        })

        retJson = {
            "status": 200,
            "msg": "You successfully signed up for API"
        }
        return jsonify(retJson)

def verifyPw(username, password):
    if not UserExist(username):
        return False
    hashed_pw = users.find({
        "Username": username,
    })[0]["Password"]

    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False

def cashWithUser(username):
    cash = users.find({
        "Username": username
    })[0]["Deposit"]
    return cash

def debtWithUser(username):
    debt = users.find({
        "Username": username
    })[0]["Debt"]
    return debt

def generateReturnDictionary(status,msg):
    retJson={
        "status": statu,
        "msg": msg
    }
    return retJson

def verifiedCredential(username, password):
    if not UserExist(username):
        return generateReturnDictionary(301, "Username Exist"), True
    
    correct_pw = verifyPw(username,password)
    if not correct_pw:
        return generateReturnDictionary(302, "Incorrect Password"), True
    
    return None, False

def updateAccount(username, balance):
    users.update({
        "Username": username,
    },{
        "$set":{
            "Own": balance
        }
    }) 

def updateDebt(username, balance):
    users.update({
        "Username": username
    },{
        "$set":{
            "Debt": balance
        }
    })

class Deposit(Resource):
    def POST(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]
        money = postedData["amount"]
        retJson, error= verifiedCredential(username,password)

        if error:
            return jsonify(retJson)
        
        if money <= 0:
            return jsonify(generateReturnDictionary(304, "The amount must be > 0"))
        
        cash = cashWithUser(username)
        money -= 1
        bank_cash = cashWithUser("BANK")
        updateAccount("BANK", bank_cash+1)
        updateAccount(username, cash + money)
        return jsonify(generateReturnDictionary(200, "amount added successfully"))

class Transfer(Resource):
    def post(self):
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]
        to = postedData["to"]
        amount = postedData["amount"]

        retJson, error = verifiedCredential(username, password)
        
        if error:
            return jsonify(username)
        cash = cashWithUser(username)
        if cash <= amount:
            return jsonify(generateReturnDictionary(304, "The amount to be transfered is more than your account balance"))

        if not UserExist(to):
            return jsonify(generateReturnDictionary(301, "receiver username is invalid"))
        
        cash_from = cashWithUser(username)
        cash_to = cashWithUser(to)
        bank_cash = cashWithUser("BANK") 

        updateAccount("BANK", bank_cash+1)
        updateAccount(to, cash_to + amount-1)
        updateAccount(username, cash_from - amount)

        return jsonify(generateReturnDictionary(200,"amount transfered successfully"))

class Balance(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]

        retJson, error = verifiedCredential(username,password)

        if error:
            return jsonify(retJson)

        retJson = users.find({
            "Username" : username
        },{
            "Password": 0,
            "_id":0
        })[0]

        return jsonify(retJson)

class TakeLoan(Resource):
    def post(self):
        postedData= request.get_json()
        username = postedData["username"]
        password = postedData["password"]
        money = postedData["amount"]

        retJson, error = verifiedCredential(username, password)

        if error:
            return jsonify(retJson)

        cash =  cashWithUser(username)
        debt = debtWithUser(username)
        updateAccount(username, password)
        updateDebt(username, debt+money)

        return jsonify(generateReturnDictionary(200, "loan added to your account"))

class PayLoan(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]
        money = postedData["amont"]

        retJson, error = verifiedCredential(username, password)

        if error:
            return jsonify(retJson)
        
        cash =  cashWithUser(username)

        if cash < money:
            return jsonify(generateReturnDictionary(303, "not enough cash in account"))
        
        debt =  debtWithUser(username)
        updateAccount(username, cash-money)
        updateDebt(username, debt-money)

        return jsonify(generateReturnDictionary(200, "Loan is cleared"))

api.add_resource(Register, '/register')
api.add_resource(Deposit, '/deposit')
api.add_resource(Transfer, '/transfer')
api.add_resource(Balance, '/balance')
api.add_resource(TakeLoan, '/takeloan')
api.add_resource(PayLoan, '/payloan')

if __name__ == "__main__":
    app.run(host='0.0.0.0')