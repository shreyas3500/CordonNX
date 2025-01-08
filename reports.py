from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import traceback
from bson import ObjectId

app = Flask(__name__)

# MongoDB Connection
client = MongoClient("mongodb+srv://doadmin:4T81NSqj572g3o9f@db-mongodb-blr1-27716-c2bd0cae.mongo.ondigitalocean.com/admin?tls=true&authSource=admin")
db = client["CordonEV"]
collection = db["data"]

# Utility function to convert ObjectId to string
def convert_objectid(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {key: convert_objectid(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid(item) for item in obj]
    return obj

# Function to convert date string to datetime object
def convert_to_datetime(date_str):
    try:
        return datetime.strptime(date_str, "%d%m%y")
    except ValueError:
        return None

@app.route("/")
def index():
    return render_template("reports.html")

@app.route("/search", methods=["POST"])
def search():
    try:
        # Extract the last 4 digits of the vehicle registration from the request
        vehicle_reg_last_4 = request.json.get("vehicleReg")
        start_date_str = request.json.get("startDate")
        end_date_str = request.json.get("endDate")
        date_str = request.json.get("date")

        # Ensure the vehicle registration is provided
        if not vehicle_reg_last_4:
            return jsonify({"error": "Vehicle registration number (last 4 digits) is required"}), 400

        print(f"Searching for vehicle with last 4 digits of registration: {vehicle_reg_last_4}")

        # Query the database for the 'License Plate Number' using last 4 digits
        vehicle_data = collection.find_one({"Vehicle Data.License Plate Number": {"$regex": f".*{vehicle_reg_last_4}$"}})

        if vehicle_data is None:
            print(f"No vehicle data found for {vehicle_reg_last_4}")
            return jsonify({"error": "Vehicle not found"}), 404

        print(f"Vehicle data found for {vehicle_reg_last_4}: {vehicle_data}")

        # Extract Atlanta Data from the database
        atlanta_data = vehicle_data.get("Atlanta Data", [])
        if not atlanta_data:
            print(f"No Atlanta data found for {vehicle_reg_last_4}")
            return jsonify({"error": "No Atlanta data found for this vehicle"}), 404

        print(f"Atlanta Data for {vehicle_reg_last_4}: {atlanta_data}")

        # Convert ObjectId fields to string before returning
        atlanta_data = convert_objectid(atlanta_data)

        # Filter based on date if provided
        filtered_data = []

        if start_date_str and end_date_str:
            # Convert start and end dates to datetime objects
            start_date = convert_to_datetime(start_date_str)
            end_date = convert_to_datetime(end_date_str)

            if not start_date or not end_date:
                return jsonify({"error": "Invalid date format. Use DDMMYY."}), 400

            # Filter the data by date range
            for entry in atlanta_data:
                entry_date = datetime.strptime(entry['date'], "%d%m%y")
                if start_date <= entry_date <= end_date:
                    filtered_data.append(entry)

        elif date_str:
            # Convert the single date to datetime object
            date = convert_to_datetime(date_str)

            if not date:
                return jsonify({"error": "Invalid date format. Use DDMMYY."}), 400

            # Filter the data by single date
            for entry in atlanta_data:
                entry_date = datetime.strptime(entry['date'], "%d%m%y")
                if entry_date == date:
                    filtered_data.append(entry)

        else:
            # If no date filter is provided, return all data
            filtered_data = atlanta_data

        if filtered_data:
            return jsonify({"atlanta_data": filtered_data})
        else:
            return jsonify({"error": "No data found for the given date range"}), 404

    except Exception as e:
        # Log the full traceback for debugging
        error_message = traceback.format_exc()
        print(f"Error occurred: {error_message}")
        return jsonify({"error": "An internal server error occurred", "details": error_message}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)











# # MongoDB Connection
# client = MongoClient("mongodb+srv://doadmin:4T81NSqj572g3o9f@db-mongodb-blr1-27716-c2bd0cae.mongo.ondigitalocean.com/admin?tls=true&authSource=admin")  # Update with your IP/Port if different
# db = client["CordonEV"]  # Replace with your database name
# collection = db["data"]  # Replace with your collection name