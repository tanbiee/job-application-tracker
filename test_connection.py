from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()

client = MongoClient(os.getenv("MONGO_URL"))

if not client:
    raise ValueError("Failed to connect to MongoDB. Please check your connection settings.")

try:
    client.admin.command("ping")
    print("mongoDB atlas connection Successful")

    db = client["job_tracker"]
    applications = db["applications"]

    print("Database: ", db.name)
    print("collection: ", applications.name)

except Exception as error:
    print("Connection failed: ", error)

finally:
    client.close()