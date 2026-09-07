from pymongo import MongoClient
from pymongo.read_preferences import SecondaryPreferred
from django.conf import settings

client = MongoClient(
    settings.MONGO_URI,
    read_preference=SecondaryPreferred(),
    maxPoolSize=50,
    serverSelectionTimeoutMS=5000
)

db = client[settings.MONGO_DATABASE]