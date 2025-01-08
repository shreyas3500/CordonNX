# import threading
# import socketserver
# import json
# from pymongo import MongoClient
# from flask import Flask, render_template, jsonify, request
# import asyncio
# import signal
# import sys
# from datetime import datetime
# import threading
# import os
# from flask import Flask, render_template, redirect, url_for


# app = Flask(__name__ ,template_folder='templates')

# # MongoDB connection
# client = MongoClient(
#     'mongodb+srv://doadmin:4T81NSqj572g3o9f@db-mongodb-blr1-27716-c2bd0cae.mongo.ondigitalocean.com/admin?tls=true&authSource=admin',
#     serverSelectionTimeoutMS=5000
# )
# db = client['CordonEV']
# collection = db['atlanta']

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
#     lock = threading.Lock()  # Lock for thread safety

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

#             with MyTCPHandler.lock:
#                 if sos_state == '1':
#                     if not MyTCPHandler.sos_active:
#                         MyTCPHandler.sos_active = True
#                         if not MyTCPHandler.sos_alert_triggered:
#                             MyTCPHandler.sos_alert_triggered = True
#                             # SOS alert triggered for the first time
#                             print("SOS alert triggered!")
#                             # Add code to handle the SOS alert (e.g., send notification)

#                 elif sos_state == '0' and MyTCPHandler.sos_active:
#                     # SOS alert has stopped
#                     MyTCPHandler.sos_active = False
#                     MyTCPHandler.sos_alert_triggered = False
#                     print("SOS alert reset.")

#                 # Store the last SOS state
#                 MyTCPHandler.last_sos_state = sos_state

#                 # Check if GPS value is 'A' before storing data
#                 if json_data.get('gps') == 'A':
#                     self.store_data_in_mongodb(json_data)

#                 if 'latitude' in json_data and 'longitude' in json_data:
#                     latitude = json_data['latitude']
#                     longitude = json_data['longitude']
#                     print(f"Vehicle location - Latitude: {latitude}, Longitude: {longitude}")

#                 else:
#                     print("Invalid JSON format")

#         except Exception as e:
#             print("Error handling request:", e)

#     def parse_json_data(self, data):
#         """
#         Attempt to parse received data as JSON.
#         Modify this method according to your data format.
#         """
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
#                     # Extracting values from binary string
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
#                     # Handle case where binary string is not long enough
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
#         """
#         Store vehicle location data in MongoDB.
#         """
#         try:
#             collection.update_one(
#                 {'imei': json_data['imei']},
#                 {'$set': json_data},
#                 upsert=True
#             )
#             print("Data stored/updated in MongoDB.")
#         except Exception as e:
#             print("Error storing data in MongoDB:", e)

# @app.route('/')
# def home():
#     # Redirect to the display_table route
#     return redirect(url_for('display_table'))

# @app.route('/display', methods=['GET'])
# def display_table():
#     # Render the DisplayTable.html template
#     return render_template('DisplayTable.html')

# # Define the logout route if needed
# @app.route('/logout')
# def logout():
#     # Implement your logout logic here (e.g., clearing session data)
#     return redirect(url_for('home'))  # Redirect to home after logout

# @app.route('/admin/users', methods=['GET'])
# def admin_users():
#     # Render the Users.html template
#     return render_template('Users.html')

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

#             cursor = collection.find(query)
#             data = list(cursor)
#             for document in data:
#                 document['_id'] = str(document['_id'])  # Convert ObjectId to string

#             return jsonify(data)
#         except Exception as e:
#             return jsonify({'error': str(e)}), 500
#     else:
#         return jsonify({'error': 'Method not allowed'}), 405

# async def start_flask_server():
#     await asyncio.sleep(0.1)  # Allow time for event loop to start
#     app.run(host='64.227.137.175', port=8001, debug=True, use_reloader=False)

# def run_servers():
#     # Start TCP server
#     HOST = "64.227.137.175"
#     PORT = 8080
#     server = ThreadedTCPServer((HOST, PORT), MyTCPHandler)
#     ip, port = server.server_address
#     print(f"Starting TCP Server @ IP: {ip}, port: {port}")

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
from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request, redirect, url_for
import asyncio
import signal
import sys
from datetime import datetime
import re

app = Flask(__name__, template_folder='templates')

# MongoDB connection
client = MongoClient(
    'mongodb+srv://doadmin:4T81NSqj572g3o9f@db-mongodb-blr1-27716-c2bd0cae.mongo.ondigitalocean.com/admin?tls=true&authSource=admin',
    serverSelectionTimeoutMS=5000
)
db = client['CordonEV']
collection = db['atlanta']

# Function to clean IMEI by removing non-numeric characters
def clean_imei(imei):
    # Remove any non-numeric characters from the IMEI
    return re.sub(r'\D', '', imei)  # Keep only digits

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
    
    # Class variables to track SOS state
    last_sos_state = '0'
    sos_active = False
    sos_alert_triggered = False
    lock = threading.Lock()  # Lock for thread safety

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

                with MyTCPHandler.lock:
                    if sos_state == '1':
                        if not MyTCPHandler.sos_active:
                            MyTCPHandler.sos_active = True
                            if not MyTCPHandler.sos_alert_triggered:
                                MyTCPHandler.sos_alert_triggered = True
                                # SOS alert triggered for the first time
                                print("SOS alert triggered!")
                                # Add code to handle the SOS alert (e.g., send notification)

                    elif sos_state == '0' and MyTCPHandler.sos_active:
                        # SOS alert has stopped
                        MyTCPHandler.sos_active = False
                        MyTCPHandler.sos_alert_triggered = False
                        print("SOS alert reset.")

                # Store the last SOS state
                MyTCPHandler.last_sos_state = sos_state

                # Check if GPS value is 'A' before storing data
                if json_data.get('gps') == 'A':
                    self.store_data_in_mongodb(json_data)

                if 'latitude' in json_data and 'longitude' in json_data:
                    latitude = json_data['latitude']
                    longitude = json_data['longitude']
                    print(f"Vehicle location - Latitude: {latitude}, Longitude: {longitude}")

        except Exception as e:
            print("Error handling request:", e)

    def parse_json_data(self, data):
        """
        Attempt to parse received data as JSON.
        Modify this method according to your data format.
        """
        try:
            parts = data.split(',')
            print(f"Parsed data parts: {parts}")
            expected_fields_count = 35

            if len(parts) >= expected_fields_count:
                # Parsing binary string from 'accelerometer' field (index 14)
                binary_string = parts[14].strip('#')
                print(f"Binary string: {binary_string}")

                # Ensure the binary string is long enough
                if len(binary_string) >= 11:
                    # Extracting values from binary string
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
                    # Handle case where binary string is not long enough
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
        """
        Store vehicle location data in MongoDB.
        """
        try:
            collection.update_one(
                {'imei': json_data['imei']},
                {'$set': json_data},
                upsert=True
            )
            print("Data stored/updated in MongoDB.")
        except Exception as e:
            print("Error storing data in MongoDB:", e)

@app.route('/')
def home():
    # Redirect to the display_table route
    return redirect(url_for('display_table'))

@app.route('/display', methods=['GET'])
def display_table():
    # Render the DisplayTable.html template
    return render_template('DisplayTable.html')

@app.route('/logout')
def logout():
    # Implement your logout logic here (e.g., clearing session data)
    return redirect(url_for('home'))  # Redirect to home after logout

@app.route('/admin/users', methods=['GET'])
def admin_users():
    # Render the Users.html template
    return render_template('Users.html')

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

            cursor = collection.find(query)
            data = list(cursor)
            for document in data:
                document['_id'] = str(document['_id'])  # Convert ObjectId to string
                document['imei_clean'] = clean_imei(document['imei'])  # Add cleaned IMEI
                
                # Sort data by the cleaned IMEI
            data.sort(key=lambda x: int(x['imei_clean']))

            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Method not allowed'}), 405

async def start_flask_server():
    await asyncio.sleep(0.1)  # Allow time for event loop to start
    app.run(host='64.227.137.175', port=8001, debug=True, use_reloader=False)

def run_servers():
    # Start TCP server
    HOST = "64.227.137.175"
    PORT = 8080
    server = ThreadedTCPServer((HOST, PORT), MyTCPHandler)
    ip, port = server.server_address
    print(f"Starting TCP Server @ IP: {ip}, port: {port}")

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    # Start Flask server
    asyncio.run(start_flask_server())

    def shutdown_servers(signal, frame):
        print("Shutting down servers...")
        server.shutdown()
        server.server_close()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_servers)
    signal.signal(signal.SIGTERM, shutdown_servers)

if __name__ == "__main__":
    run_servers()
