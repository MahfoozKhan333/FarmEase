from pymongo import MongoClient

def connect_to_mongodb():
    try:
        # Connect to MongoDB server
        client = MongoClient("mongodb://localhost:27017/")
        
        # Create the database
        db = client["cattle_farm"]  

        # Users Collection Schema
        users = db['users']
        users.insert_one({
            # "_id": None,  # MongoDB ObjectId (or use custom ID)
            "username": None,
            "password": None,  # Password stored as a hashed value
            "email": None,
            "first_name": None,
            "last_name": None,
            "mobile_number":None
        })

        # Animals Collection Schema
        animals = db['animals']
        animals.insert_one({
            # "_id": None,  # MongoDB ObjectId (or use custom ID)
            "animal_id": None,
            "user_id": None,  # Reference to the user's ID
            "breed": None,
            "food": None,
            "weight": None,
            "growth": None,
            "milk_production": None,
            "date_of_birth": None,
            "last_updated": None
        })

        # Records Collection Schema
        records = db['records']
        records.insert_one({
            # "_id": None,  # MongoDB ObjectId (or use custom ID)
            "animal_id": None,  # Reference to the animal's ID
            "record_date": None,
            "weight": None,
            "milk_production": None
        })

        print("Database and collections initialized with empty schema.")
        return client

    except Exception as e:
        print("Error connecting to MongoDB or inserting data:", e)
        raise e

# Connect to MongoDB and initialize the schema
if __name__ == "__main__":
    connect_to_mongodb()
