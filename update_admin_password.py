import bcrypt
from pymongo import MongoClient

# MongoDB URI and database
client = MongoClient("mongodb+srv://doadmin:4T81NSqj572g3o9f@db-mongodb-blr1-27716-c2bd0cae.mongo.ondigitalocean.com/admin?tls=true&authSource=admin")
db = client['CordonEV']
collection = db['authentications']

# Function to generate hashed password
def generate_hashed_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode()

# Admin credentials
admin_username = "admin"
admin_password = "admin"  # Set your admin password here
admin_hashed_password = generate_hashed_password(admin_password)

# Super Admin credentials
super_admin_username = "superadmin"
super_admin_password = "super"  # Set your super admin password here
super_admin_hashed_password = generate_hashed_password(super_admin_password)

# Insert or update admin credentials
collection.update_one(
    { "username": admin_username },  # Query to find the admin user
    { 
        "$set": { 
            "password": admin_hashed_password, 
            "role": "admin"  # Set role to admin
        } 
    },
    upsert=True  # This will insert the record if it doesn't exist
)

# Insert or update super admin credentials
collection.update_one(
    { "username": super_admin_username },  # Query to find the super admin user
    { 
        "$set": { 
            "password": super_admin_hashed_password, 
            "role": "super_admin"  # Set role to super_admin
        } 
    },
    upsert=True  # This will insert the record if it doesn't exist
)

print("Admin and Super Admin credentials have been updated.")
