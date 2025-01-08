# import threading
# import socketserver
# import json
# from pymongo import MongoClient
# from flask import Flask, render_template, jsonify, request
# import asyncio
# import signal
# import sys
# from datetime import datetime
# from math import radians, sin, cos, sqrt, atan2

# # Flask app setup
# app = Flask(__name__, template_folder='templates')

# # MongoDB connection
# client = MongoClient(
#     'mongodb+srv://doadmin:4T81NSqj572g3o9f@db-mongodb-blr1-27716-c2bd0cae.mongo.ondigitalocean.com/admin?tls=true&authSource=admin',
#     serverSelectionTimeoutMS=5000
# )
# db = client['CordonEV']
# collection = db['atlanta']

# # Haversine function to calculate the distance between two points on Earth
# def calculate_distance(lat1, lon1, lat2, lon2):
#     R = 6371.0  # Radius of the Earth in km
#     dlat = radians(lat2 - lat1)
#     dlon = radians(lon2 - lon1)

#     a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
#     c = 2 * atan2(sqrt(a), sqrt(1 - a))

#     distance = R * c
#     return distance

# class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
#     """
#     Threaded TCP Server Class - handles multiple requests asynchronously
#     """
#     allow_reuse_address = True

#     def __init__(self, server_address, handler_cls):
#         super().__init__(server_address, handler_cls)
#         self.shutdown_event = threading.Event()

#     def server_close(self):
#         super().server_close()

# class MyTCPHandler(socketserver.BaseRequestHandler):
#     """
#     The request handler class for our TCP server.
#     It is instantiated once per connection to the server.
#     """
    
#     # Class variables to track SOS state
#     last_sos_state = '0'
#     sos_active = False
#     sos_alert_triggered = False

#     def handle(self):
#         try:
#             data = self.request.recv(4096).decode('utf-8').strip()
#             print("Received raw data:", data)

#             json_data = self.parse_json_data(data)
#             if json_data:
#                 print("Valid JSON data:", json_data)

#                 # Check and handle SOS alert
#                 sos_state = json_data.get('sos', '0')
#                 print(f"SOS state received: {sos_state}")

#                 if sos_state == '1':
#                     if not MyTCPHandler.sos_active:
#                         MyTCPHandler.sos_active = True
#                         if not MyTCPHandler.sos_alert_triggered:
#                             MyTCPHandler.sos_alert_triggered = True
#                             print("SOS alert triggered!")
#                             # Add code to handle the SOS alert (e.g., send notification)

#                 elif sos_state == '0' and MyTCPHandler.sos_active:
#                     MyTCPHandler.sos_active = False
#                     MyTCPHandler.sos_alert_triggered = False
#                     print("SOS alert reset.")

#                 MyTCPHandler.last_sos_state = sos_state

#                 # Check if GPS value is 'A' before storing data
#                 if json_data.get('gps') == 'A':
#                     self.store_data_in_mongodb(json_data)

#                 if 'latitude' in json_data and 'longitude' in json_data:
#                     latitude = json_data['latitude']
#                     longitude = json_data['longitude']
#                     print(f"Vehicle location - Latitude: {latitude}, Longitude: {longitude}")

#             else:
#                 print("Invalid JSON format")

#         except Exception as e:
#             print("Error handling request:", e)

#     def parse_json_data(self, data):
#         try:
#             parts = data.split(',')
#             print(f"Parsed data parts: {parts}")
#             expected_fields_count = 35

#             if len(parts) >= expected_fields_count:
#                 # Parsing binary string from 'accelerometer' field (index 14)
#                 binary_string = parts[14].strip('#')
#                 print(f"Binary string: {binary_string}")

#                 # Ensure the binary string is long enough
#                 if len(binary_string) >= 11:
#                     ignition = binary_string[0]
#                     door = binary_string[1]
#                     sos = binary_string[2]
#                     r1 = binary_string[3]
#                     r2 = binary_string[4]
#                     ac = binary_string[5]
#                     r3 = binary_string[6]
#                     main_power = binary_string[7]
#                     harsh_speed = binary_string[8]
#                     arm = binary_string[9]
#                     sleep = binary_string[10]
#                 else:
#                     ignition = door = sos = r1 = r2 = ac = r3 = main_power = harsh_speed = arm = sleep = '0'

#                 # Handle missing latitude/longitude
#                 latitude = parts[4] if parts[4] != '-' else ''
#                 longitude = parts[6] if parts[6] != '-' else ''

#                 json_data = {
#                     'imei': parts[0],
#                     'header': parts[1],
#                     'time': parts[2],
#                     'gps': parts[3],
#                     'latitude': latitude,
#                     'dir1': parts[5],
#                     'longitude': longitude,
#                     'dir2': parts[7],
#                     'speed': parts[8],
#                     'course': parts[9],
#                     'date': parts[10],
#                     'checksum': parts[13] if len(parts) > 13 else '0',
#                     'ignition': ignition,
#                     'door': door,
#                     'sos': sos,
#                     'r1': r1,
#                     'r2': r2,
#                     'ac': ac,
#                     'r3': r3,
#                     'main_power': main_power,
#                     'harsh_speed': harsh_speed,
#                     'arm': arm,
#                     'sleep': sleep,
#                     'accelerometer': parts[12],
#                     'adc': parts[15],
#                     'one_wire': parts[16],
#                     'i_btn': parts[17],
#                     'odometer': parts[18],
#                     'temp': parts[19],
#                     'internal_bat': parts[20],
#                     'gsm_sig': parts[21],
#                     'mcc': parts[22],
#                     'mnc': parts[23],
#                     'cellid': parts[24],
#                 }
#                 return json_data
#             else:
#                 print(f"Received data does not contain at least {expected_fields_count} fields.")
#                 return None

#         except Exception as e:
#             print("Error parsing JSON data:", e)
#             return None

#     def store_data_in_mongodb(self, json_data):
#         try:
#             collection.update_one(
#                 {'imei': json_data['imei'], 'date': json_data['date']},
#                 {'$set': json_data},
#                 upsert=True
#             )
#             print("Data stored/updated in MongoDB.")
#         except Exception as e:
#             print("Error storing data in MongoDB:", e)

# # Flask routes
# @app.route('/')
# def index():
#     return render_template('alldevice.html')

# @app.route('/api/data', methods=['GET', 'POST'])
# def receive_data():
#     if request.method == 'POST':
#         try:
#             data = request.get_json()
#             if data:
#                 collection.insert_one(data)
#                 print("Data received from TCP server and stored in MongoDB:", data)
#                 return jsonify({'message': 'Data received successfully'}), 200
#             else:
#                 return jsonify({'error': 'No JSON data received'}), 400
#         except Exception as e:
#             return jsonify({'error': str(e)}), 500
#     elif request.method == 'GET':
#         try:
#             imei = request.args.get('imei')
#             today = datetime.now().strftime('%d%m%y')

#             query = {'date': today}
#             if imei:
#                 query['imei'] = imei

#             # Fetch vehicles from MongoDB
#             cursor = collection.find(query)
#             vehicles = list(cursor)

#             # Fetch landmarks from MongoDB
#             landmarks_cursor = db.landmarks.find({})
#             landmarks = list(landmarks_cursor)

#             # Calculate distance for each vehicle to the nearest landmark
#             for vehicle in vehicles:
#                 vehicle_lat = float(vehicle.get('latitude', 0))
#                 vehicle_lon = float(vehicle.get('longitude', 0))

#                 nearest_landmark = None
#                 min_distance = float('inf')

#                 for landmark in landmarks:
#                     landmark_lat = float(landmark['latitude'])
#                     landmark_lon = float(landmark['longitude'])

#                     distance = calculate_distance(vehicle_lat, vehicle_lon, landmark_lat, landmark_lon)
#                     if distance < min_distance:
#                         min_distance = distance
#                         nearest_landmark = landmark

#                 vehicle['nearest_landmark'] = nearest_landmark['name'] if nearest_landmark else None
#                 vehicle['distance_to_landmark'] = min_distance if nearest_landmark else None
#                 vehicle['_id'] = str(vehicle['_id'])

#             return jsonify(vehicles)
#         except Exception as e:
#             return jsonify({'error': str(e)}), 500
#     else:
#         return jsonify({'error': 'Method not allowed'}), 405

# # @app.route('/map')
# # def map_view():
# #     return render_template('map.html')

# # Flask and TCP server control
# async def start_flask_server():
#     await asyncio.sleep(0.1)
#     app.run(host='64.227.137.175', port=8002, debug=True, use_reloader=False)

# def run_servers():
#     HOST = "64.227.137.175"
#     PORT = 8000
#     server = ThreadedTCPServer((HOST, PORT), MyTCPHandler)
#     print(f"Starting TCP Server @ IP: {HOST}, port: {PORT}")

#     server_thread = threading.Thread(target=server.serve_forever)
#     server_thread.daemon = True
#     server_thread.start()

#     # Start Flask server
#     asyncio.run(start_flask_server())

#     def shutdown_servers(signal, frame):
#         print("Shutting down servers...")
#         server.shutdown()
#         server.server_close()
#         sys.exit(0)

#     signal.signal(signal.SIGINT, shutdown_servers)
#     signal.signal(signal.SIGTERM, shutdown_servers)

# if __name__ == "__main__":
#     run_servers()











import threading
import socketserver
import json
import os
from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request
import signal
import sys
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2

# Flask app setup
app = Flask(__name__, template_folder='templates')

# MongoDB connection using environment variables
MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://doadmin:4T81NSqj572g3o9f@db-mongodb-blr1-27716-c2bd0cae.mongo.ondigitalocean.com/admin?tls=true&authSource=admin')
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client['CordonEV']
collection = db['atlanta']

# Haversine function to calculate the distance between two points on Earth
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Radius of the Earth in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """
    Threaded TCP Server Class - handles multiple requests asynchronously
    """
    allow_reuse_address = True

    def __init__(self, server_address, handler_cls):
        super().__init__(server_address, handler_cls)
        self.shutdown_event = threading.Event()

    def server_close(self):
        super().server_close()

class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our TCP server.
    It is instantiated once per connection to the server.
    """
    
    # Class variables to track SOS state (with thread-safe lock)
    lock = threading.Lock()
    sos_active = False
    sos_alert_triggered = False

    def handle(self):
        try:
            data = self.request.recv(4096).decode('utf-8').strip()
            print("Received raw data:", data)

            json_data = self.parse_json_data(data)
            if json_data:
                print("Valid JSON data:", json_data)

                # Check and handle SOS alert
                sos_state = json_data.get('sos', '0')
                print(f"SOS state received: {sos_state}")

                # Thread-safe SOS handling
                with MyTCPHandler.lock:
                    if sos_state == '1' and not MyTCPHandler.sos_alert_triggered:
                        MyTCPHandler.sos_active = True
                        MyTCPHandler.sos_alert_triggered = True
                        print("SOS alert triggered!")
                        # Add SOS alert notification handling here
                    elif sos_state == '0' and MyTCPHandler.sos_active:
                        MyTCPHandler.sos_active = False
                        MyTCPHandler.sos_alert_triggered = False
                        print("SOS alert reset.")

                # Check if GPS value is 'A' before storing data
                if json_data.get('gps') == 'A':
                    self.store_data_in_mongodb(json_data)

                if 'latitude' in json_data and 'longitude' in json_data:
                    latitude = json_data['latitude']
                    longitude = json_data['longitude']
                    print(f"Vehicle location - Latitude: {latitude}, Longitude: {longitude}")

            else:
                print("Invalid JSON format")

        except Exception as e:
            print("Error handling request:", e)

    def parse_json_data(self, data):
        try:
            parts = data.split(',')
            print(f"Parsed data parts: {parts}")
            expected_fields_count = 35

            if len(parts) >= expected_fields_count:
                # Parsing binary string from 'accelerometer' field (index 14)
                binary_string = parts[14].strip('#')
                print(f"Binary string: {binary_string}")
                
                # Default values if binary string is too short
                ignition, door, sos = '0', '0', '0'

                # Ensure the binary string is long enough
                if len(binary_string) >= 11:
                    ignition = binary_string[0]
                    door = binary_string[1]
                    sos = binary_string[2]
                    r1 = binary_string[3]
                    r2 = binary_string[4]
                    ac = binary_string[5]
                    r3 = binary_string[6]
                    main_power = binary_string[7]
                    harsh_speed = binary_string[8]
                    arm = binary_string[9]
                    sleep = binary_string[10]
                else:
                    ignition = door = sos = r1 = r2 = ac = r3 = main_power = harsh_speed = arm = sleep = '0'

                # Handle missing latitude/longitude
                latitude = parts[4] if parts[4] != '-' else ''
                longitude = parts[6] if parts[6] != '-' else ''

                json_data = {
                    'imei': parts[0],
                    'header': parts[1],
                    'time': parts[2],
                    'gps': parts[3],
                    'latitude': latitude,
                    'dir1': parts[5],
                    'longitude': longitude,
                    'dir2': parts[7],
                    'speed': parts[8],
                    'course': parts[9],
                    'date': parts[10],
                    'checksum': parts[13] if len(parts) > 13 else '0',
                    'ignition': ignition,
                    'door': door,
                    'sos': sos,
                    'r1': r1,
                    'r2': r2,
                    'ac': ac,
                    'r3': r3,
                    'main_power': main_power,
                    'harsh_speed': harsh_speed,
                    'arm': arm,
                    'sleep': sleep,
                    'accelerometer': parts[12],
                    'adc': parts[15],
                    'one_wire': parts[16],
                    'i_btn': parts[17],
                    'odometer': parts[18],
                    'temp': parts[19],
                    'internal_bat': parts[20],
                    'gsm_sig': parts[21],
                    'mcc': parts[22],
                    'mnc': parts[23],
                    'cellid': parts[24],
                }
                return json_data
            else:
                print(f"Received data does not contain at least {expected_fields_count} fields.")
                return None

        except Exception as e:
            print("Error parsing JSON data:", e)
            return None

    def store_data_in_mongodb(self, json_data):
        try:
            collection.update_one(
                {'imei': json_data['imei'], 'date': json_data['date']},
                {'$set': json_data},
                upsert=True
            )
            print("Data stored/updated in MongoDB.")
        except Exception as e:
            print("Error storing data in MongoDB:", e)

# Flask routes
@app.route('/')
def index():
    return render_template('alldevice.html')

@app.route('/api/data', methods=['GET', 'POST'])
def receive_data():
    if request.method == 'POST':
        try:
            data = request.get_json()
            if data:
                collection.insert_one(data)
                print("Data received from TCP server and stored in MongoDB:", data)
                return jsonify({'message': 'Data received successfully'}), 200
            else:
                return jsonify({'error': 'No JSON data received'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    elif request.method == 'GET':
        try:
            imei = request.args.get('imei')
            today = datetime.now().strftime('%d%m%y')

            query = {'date': today}
            if imei:
                query['imei'] = imei

            # Fetch vehicles from MongoDB
            cursor = collection.find(query)
            vehicles = list(cursor)

            # Fetch landmarks from MongoDB
            landmarks_cursor = db.landmarks.find({})
            landmarks = list(landmarks_cursor)

            # Calculate distance for each vehicle to the nearest landmark
            for vehicle in vehicles:
                vehicle_lat = float(vehicle.get('latitude', 0))
                vehicle_lon = float(vehicle.get('longitude', 0))

                nearest_landmark = None
                min_distance = float('inf')

                for landmark in landmarks:
                    landmark_lat = float(landmark['latitude'])
                    landmark_lon = float(landmark['longitude'])

                    distance = calculate_distance(vehicle_lat, vehicle_lon, landmark_lat, landmark_lon)
                    if distance < min_distance:
                        min_distance = distance
                        nearest_landmark = landmark

                vehicle['nearest_landmark'] = nearest_landmark['name'] if nearest_landmark else None
                vehicle['distance_to_landmark'] = min_distance if nearest_landmark else None
                vehicle['_id'] = str(vehicle['_id'])

            return jsonify(vehicles)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Method not allowed'}), 405

# Flask and TCP server control
def start_flask_server():
    app.run(host='0.0.0.0', port=8002, debug=True, use_reloader=False)

def run_servers():
    HOST = "0.0.0.0"
    PORT = 8000
    server = ThreadedTCPServer((HOST, PORT), MyTCPHandler)
    print(f"Starting TCP Server @ IP: {HOST}, port: {PORT}")

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    # Start Flask server in a separate thread
    flask_thread = threading.Thread(target=start_flask_server)
    flask_thread.daemon = True
    flask_thread.start()

    def shutdown_servers(signal, frame):
        print("Shutting down servers...")
        server.shutdown()
        server.server_close()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_servers)
    signal.signal(signal.SIGTERM, shutdown_servers)

    server_thread.join()
    flask_thread.join()

if __name__ == "__main__":
    run_servers()


