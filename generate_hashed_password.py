import bcrypt

# Function to generate hashed password
def generate_hashed_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode()

# Admin password
admin_password = "admin_password"  # Set your admin password here
admin_hashed_password = generate_hashed_password(admin_password)
print("Admin Hashed password:", admin_hashed_password)

# Super Admin password
super_admin_password = "superadmin_password"  # Set your super admin password here
super_admin_hashed_password = generate_hashed_password(super_admin_password)
print("Super Admin Hashed password:", super_admin_hashed_password)
