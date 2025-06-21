"""
database.py

Initializes the MongoDB connection and exposes database collections for use throughout the API.
Loads credentials from environment variables and verifies the connection.
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables from .env file
load_dotenv()

# Get database credentials from environment variables
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

# Create MongoDB connection string
MONGO_URI = (
    f"mongodb+srv://{DB_USER}:{DB_PASS}@{DB_HOST}/?retryWrites=true&w=majority&appName=CoderCluster"
)

# Initialize MongoDB client and expose collections
try:
    client = MongoClient(MONGO_URI)
    # Test the connection
    client.admin.command("ping")
    print("Pinged your deployment. You successfully connected to MongoDB!")

    db = client[DB_NAME]  # The main MongoDB database instance
    collection_name = db["stations2"]  # Collection for fuel stations
    users_collection = db["users"]      # Collection for user accounts

except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    raise
