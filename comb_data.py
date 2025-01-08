# from flask import Flask, render_template
# from pymongo import MongoClient
# import re
# import threading

# app = Flask(__name__)

# # Connect to the MongoDB database
# client = MongoClient("mongodb+srv://doadmin:4T81NSqj572g3o9f@db-mongodb-blr1-27716-c2bd0cae.mongo.ondigitalocean.com/admin?tls=true&authSource=admin")
# db = client.CordonEV

# def sanitize_imei(imei):
#     """Remove non-printable characters and prefixes like 'ATL' from IMEI"""
#     if isinstance(imei, str):
#         return re.sub(r'[^\d]', '', imei).lstrip("ATL")
#     return imei

# def merge_data(imei=None):
#     data_collection = db.data

#     if imei is not None:
#         imei_sanitized = str(imei).strip()
#         print(f"Original IMEI: {imei}")
#         print(f"Sanitized IMEI: {imei_sanitized}")

#         try:
#             imei_as_int = int(imei_sanitized)
#         except ValueError:
#             print(f"Error converting IMEI to integer: {imei_sanitized}")
#             return

#         vehicle = db.vehicle_inventory.find_one({"IMEI Number": imei_as_int})

#         if vehicle:
#             print(f"Vehicle found: {vehicle}")
#         else:
#             print(f"No vehicle found for sanitized IMEI: {imei_sanitized}")
#             return

#         company_name = vehicle.get('Company Name')
#         driver_name = vehicle.get('Driver Name')

#         if company_name:
#             print(f"Fetching details for company: {company_name}")
#             company_details = db.customers_list.find_one({"Company Name": re.compile(f"^{company_name}$", re.IGNORECASE)})
#             if company_details:
#                 print(f"Company details: {company_details}")
#             else:
#                 print(f"No details found for company: {company_name}")
#         else:
#             print("No company name found in vehicle data")
#             company_details = None

#         # Fetch related data
#         atlanta_data = list(db.atlanta.find({"imei": {"$regex": re.escape("ATL" + imei_sanitized)}}))
#         device_data = db.device_inventory.find_one({"IMEI": imei_sanitized})

#         if driver_name:
#             driver_data = db.driver_inventory.find_one({"Driver Name": driver_name.strip()})
#         else:
#             driver_data = None

#         print(f"Atlanta Data: {atlanta_data}")
#         print(f"Device Data: {device_data}")
#         print(f"Driver Data: {driver_data}")

#         # Consolidate data with additional checks
#         combined_data = {
#             "IMEI Number": imei_sanitized,
#             "Company Name": company_name,
#             "Driver Name": driver_name,
#             "Vehicle Data": vehicle,
#             "Atlanta Data": atlanta_data if atlanta_data else None,
#             "Device Data": device_data if device_data else None,
#             "Driver Data": driver_data if driver_data else None,
#             "Company Details": company_details if company_details else None  # Add company details to the combined data
#         }

#         print(f"Combined Data to be inserted: {combined_data}")

#         # Ensure all necessary fields are present before inserting
#         try:
#             data_collection.update_one(
#                 {"IMEI Number": imei_sanitized},  # Match record by IMEI
#                 {"$set": combined_data},  # Set new data
#                 upsert=True  # Insert if no record matches
#             )
#             print(f"Data successfully merged for IMEI: {imei}")
#         except Exception as e:
#             print(f"Error inserting data into MongoDB: {str(e)}")



# def initial_merge():
#     # Perform an initial merge of all data in the vehicle_inventory collection
#     print("Performing initial data merge...")
#     for vehicle in db.vehicle_inventory.find():
#         imei = vehicle.get('IMEI Number')
#         if imei:
#             merge_data(imei)
#     print("Initial data merge completed!")

# def listen_to_changes():
#     # Set up change streams to watch collections
#     vehicle_inventory_stream = db.vehicle_inventory.watch()
#     atlanta_stream = db.atlanta.watch()
#     device_inventory_stream = db.device_inventory.watch()
#     driver_inventory_stream = db.driver_inventory.watch()

#     # Watch for changes and update the 'data' collection accordingly
#     while True:
#         # Check for changes in any stream
#         for change in vehicle_inventory_stream:
#             imei = change['fullDocument'].get('IMEI Number')
#             merge_data(imei)

#         for change in atlanta_stream:
#             imei = change['fullDocument'].get('imei')
#             imei_str = imei.replace("ATL", "")  # Strip out "ATL" to get the correct IMEI
#             merge_data(imei_str)

#         for change in device_inventory_stream:
#             imei = change['fullDocument'].get('IMEI')
#             merge_data(imei)

#         for change in driver_inventory_stream:
#             driver_name = change['fullDocument'].get('Driver Name')
#             # Trigger update for all vehicles related to this driver
#             for vehicle in db.vehicle_inventory.find({"Driver Name": driver_name.strip()}):
#                 imei = vehicle.get('IMEI Number')
#                 merge_data(imei)

# # Perform the initial merge when the app starts
# initial_merge()

# # Start the background thread for monitoring changes
# threading.Thread(target=listen_to_changes, daemon=True).start()

# # Commenting out the HTML rendering part
# # @app.route('/')
# # def show_data():
# #     # Fetch the merged data from the 'data' collection, sorted by IMEI Number
# #     merged_data = list(db.data.find().sort("IMEI Number"))

# #     # Debug: Print merged data to verify it's being fetched
# #     print(f"Fetched {len(merged_data)} records from 'data' collection:")
# #     for item in merged_data:
# #         print(item)

# #     # Render the template with the merged data
# #     return render_template('all_data.html', merged_data=merged_data)

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8008)





from flask import Flask, render_template
from pymongo import MongoClient
import re
import threading

app = Flask(__name__)

# Connect to the MongoDB database
client = MongoClient("mongodb+srv://doadmin:4T81NSqj572g3o9f@db-mongodb-blr1-27716-c2bd0cae.mongo.ondigitalocean.com/admin?tls=true&authSource=admin")
db = client.CordonEV

def sanitize_imei(imei):
    """Remove non-printable characters and prefixes like 'ATL' from IMEI"""
    if isinstance(imei, str):
        return re.sub(r'[^\d]', '', imei).lstrip("ATL")
    return imei

def merge_data(imei=None):
    data_collection = db.data

    if imei is not None:
        imei_sanitized = sanitize_imei(imei)
        print(f"Processing IMEI: {imei_sanitized}")

        # Ensure imei_sanitized is treated as a string
        imei_sanitized_str = str(imei_sanitized)

        # Check if the vehicle exists in the vehicle_inventory
        vehicle = db.vehicle_inventory.find_one({"IMEI Number": imei_sanitized_str})

        if vehicle:
            print(f"Vehicle found: {vehicle}")
        else:
            print(f"No vehicle found for sanitized IMEI: {imei_sanitized_str}")
            return

        company_name = vehicle.get('Company Name')
        driver_name = vehicle.get('Driver Name')

        if company_name:
            print(f"Fetching details for company: {company_name}")
            company_details = db.customers_list.find_one({"Company Name": re.compile(f"^{company_name}$", re.IGNORECASE)})
            if company_details:
                print(f"Company details: {company_details}")
            else:
                print(f"No details found for company: {company_name}")
        else:
            print("No company name found in vehicle data")
            company_details = None

        # Fetch atlanta_data
        atlanta_data = list(db.atlanta.find({"imei": {"$regex": re.escape("ATL" + imei_sanitized_str)}}))
        device_data = db.device_inventory.find_one({"IMEI": imei_sanitized_str})

        if driver_name:
            driver_data = db.driver_inventory.find_one({"Driver Name": driver_name.strip()})
        else:
            driver_data = None

        # Consolidate data with additional checks
        combined_data = {
            "IMEI Number": imei_sanitized_str,
            "Company Name": company_name,
            "Driver Name": driver_name,
            "Vehicle Data": vehicle,
            "Atlanta Data": atlanta_data if atlanta_data else None,
            "Device Data": device_data if device_data else None,
            "Driver Data": driver_data if driver_data else None,
            "Company Details": company_details if company_details else None
        }

        print(f"Combined Data to be inserted: {combined_data}")

        # Ensure all necessary fields are present before inserting
        try:
            result = data_collection.update_one(
                {"IMEI Number": imei_sanitized_str},  # Match record by IMEI
                {"$set": combined_data},  # Set new data
                upsert=True  # Insert if no record matches
            )
            if result.upserted_id:
                print(f"New data inserted for IMEI: {imei_sanitized_str}")
            else:
                print(f"Data updated for IMEI: {imei_sanitized_str}")
        except Exception as e:
            print(f"Error inserting data into MongoDB for IMEI {imei_sanitized_str}: {str(e)}")

def initial_merge():
    # Perform an initial merge of all data in the vehicle_inventory collection
    print("Performing initial data merge...")
    vehicles = list(db.vehicle_inventory.find())
    print(f"Found {len(vehicles)} vehicles in the inventory.")

    for vehicle in vehicles:
        imei = vehicle.get('IMEI Number')
        if imei:
            print(f"Processing vehicle with IMEI: {imei}")
            merge_data(imei)
    print("Initial data merge completed!")

def listen_to_changes():
    # Set up change streams to watch collections
    vehicle_inventory_stream = db.vehicle_inventory.watch()
    atlanta_stream = db.atlanta.watch()
    device_inventory_stream = db.device_inventory.watch()
    driver_inventory_stream = db.driver_inventory.watch()

    # Watch for changes and update the 'data' collection accordingly
    while True:
        # Check for changes in any stream
        for change in vehicle_inventory_stream:
            imei = change['fullDocument'].get('IMEI Number')
            print(f"Change detected in vehicle_inventory for IMEI: {imei}")
            merge_data(imei)

        for change in atlanta_stream:
            imei = change['fullDocument'].get('imei')
            imei_str = imei.replace("ATL", "")  # Strip out "ATL" to get the correct IMEI
            print(f"Change detected in atlanta for IMEI: {imei_str}")
            merge_data(imei_str)

        for change in device_inventory_stream:
            imei = change['fullDocument'].get('IMEI')
            print(f"Change detected in device_inventory for IMEI: {imei}")
            merge_data(imei)

        for change in driver_inventory_stream:
            driver_name = change['fullDocument'].get('Driver Name')
            print(f"Change detected in driver_inventory for Driver: {driver_name}")
            # Trigger update for all vehicles related to this driver
            for vehicle in db.vehicle_inventory.find({"Driver Name": driver_name.strip()}):
                imei = vehicle.get('IMEI Number')
                merge_data(imei)

# Perform the initial merge when the app starts
initial_merge()

# Start the background thread for monitoring changes
threading.Thread(target=listen_to_changes, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8008)
