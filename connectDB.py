from pymongo import MongoClient


def connect_to_mongodb():

    try:
        
        client = MongoClient("mongodb://localhost:27017/")
        db = client["cattle_farm"]  
        collection = db['animals']
        collection.insert_one({"name": "Cow", "breed": "Holstein", "age": 5})

        return client
    
    except ConnectionError as e:
        print("Error connecting to MongoDB:", e)
        raise e
