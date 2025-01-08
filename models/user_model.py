from pymongo import MongoClient

client = MongoClient("mongodb+srv://doadmin:4T81NSqj572g3o9f@db-mongodb-blr1-27716-c2bd0cae.mongo.ondigitalocean.com/admin?tls=true&authSource=admin")
db = client['CordonEV']

# Users collection
users_collection = db['authentications']
