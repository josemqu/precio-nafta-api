import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database credentials from environment variables
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')

# Create MongoDB connection string
MONGO_URI = f"mongodb+srv://{DB_USER}:{DB_PASS}@{DB_HOST}/?retryWrites=true&w=majority&appName=CoderCluster"

# Initialize MongoDB client
try:
    client = MongoClient(MONGO_URI)
    # Test the connection
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    
    db = client[DB_NAME]
    collection_name = db["stations2"]
    
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    raise
