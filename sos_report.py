from flask import Flask, jsonify, render_template
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb+srv://doadmin:4T81NSqj572g3o9f@db-mongodb-blr1-27716-c2bd0cae.mongo.ondigitalocean.com/admin?tls=true&authSource=admin")
db = client["CordonEV"]
sos_logs_collection = db["sos_logs"]

# Convert latitude and longitude to decimal degrees
def convert_coordinates(lat, lon):
    try:
        lat_deg = int(lat[:2])
        lat_min = float(lat[2:])
        lon_deg = int(lon[:3])
        lon_min = float(lon[3:])
        latitude = lat_deg + (lat_min / 60)
        longitude = lon_deg + (lon_min / 60)
        return latitude, longitude
    except Exception as e:
        print(f"Error converting coordinates: {e}")
        return 0.0, 0.0

@app.route('/')
def index():
    return render_template('sos_report.html')

@app.route('/api/sos-logs')
def get_sos_logs():
    logs = []
    for log in sos_logs_collection.find():
        lat, lon = convert_coordinates(log["latitude"], log["longitude"])
        logs.append({
            "imei": log["imei"],
            "latitude": lat,
            "longitude": lon,
            "location": log["location"],
            "timestamp": log["timestamp"]
        })
    return jsonify(logs)

if __name__ == "__main__":
    app.run(debug=True)

