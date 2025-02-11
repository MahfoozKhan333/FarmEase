from pymongo import MongoClient

def connect_to_mongodb():
    try:
        # Connect to MongoDB server
        client = MongoClient("mongodb://localhost:27017/")
        
        # Create the database
        db = client["cattle_farm"]  
        print("Successfully connected to database.")

        # Initialize collections with optional schema validation (if necessary)
        if "animals" not in db.list_collection_names():
            db.create_collection("animals")
            print("Collection 'animals' initialized.")

        if "users" not in db.list_collection_names():
            db.create_collection("users")
            print("Collection 'users' initialized.")

        return client

    except Exception as e:
        print("Error connecting to MongoDB or intialising data:", e)
        raise e

# Connect to MongoDB and initialize the schema
if __name__ == "__main__":
    connect_to_mongodb()
