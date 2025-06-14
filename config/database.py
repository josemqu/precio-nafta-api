from pymongo import MongoClient

client = MongoClient(
    "mongodb+srv://josemqu:LmfXA2ZNj5rskBm4@codercluster.tgft5r9.mongodb.net/?retryWrites=true&w=majority&appName=CoderCluster"
)

db = client.prices

collection_name = db["stations2"]
