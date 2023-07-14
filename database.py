from pymongo import MongoClient

# Menghubungkan ke database MongoDB untuk top-up
topup_client = MongoClient("mongodb+srv://avel:tmp0@aveltmp.nqyqy6h.mongodb.net/aveltmp?retryWrites=true&w=majority:27017/")
topup_db = topup_client["topup_db"]
topup_collection = topup_db["topup"]

# Menghubungkan ke database MongoDB untuk my coin
coin_client = MongoClient("mongodb+srv://avel:tmp0@aveltmp.nqyqy6h.mongodb.net/aveltmp?retryWrites=true&w=majority:27017/")
coin_db = coin_client["coin_db"]
coin_collection = coin_db["coin"]

def add_topup(user_id, amount):
    data = {"user_id": user_id, "amount": amount}
    topup_collection.insert_one(data)

def get_topup(user_id):
    data = topup_collection.find_one({"user_id": user_id})
    return data["amount"] if data else 0

def add_coin(user_id, coins):
    data = {"user_id": user_id, "coins": coins}
    coin_collection.insert_one(data)

def get_coin(user_id):
    data = coin_collection.find_one({"user_id": user_id})
    return data["coins"] if data else 0
