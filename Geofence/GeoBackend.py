from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from bson import ObjectId
import logging

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb+srv://doadmin:4T81NSqj572g3o9f@db-mongodb-blr1-27716-c2bd0cae.mongo.ondigitalocean.com/admin?tls=true&authSource=admin"
mongo = PyMongo(app)

logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    return render_template('Geofence.html')

@app.route('/save_geofence', methods=['POST'])
def save_geofence():
    app.logger.debug('save_geofence endpoint was hit')
    try:
        data = request.json
        app.logger.debug('Received data: %s', data)
        
        geofence_id = mongo.db.Geofence.insert_one(data).inserted_id
        app.logger.debug('Geofence saved with ID: %s', geofence_id)
        
        return jsonify({'geofence_id': str(geofence_id)})
    except Exception as e:
        app.logger.error('Error saving geofence: %s', str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/get_vehicles', methods=['GET'])
def get_vehicles():
    app.logger.debug('get_vehicles endpoint was hit')
    try:
        vehicles = list(mongo.db['geo-vehicles'].find())
        for vehicle in vehicles:
            vehicle['_id'] = str(vehicle['_id'])
        return jsonify({'vehicles': vehicles})
    except Exception as e:
        app.logger.error('Error fetching vehicles: %s', str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/get_geofences', methods=['GET'])
def get_geofences():
    app.logger.debug('get_geofences endpoint was hit')
    try:
        geofences = list(mongo.db.Geofence.find())
        app.logger.debug('Number of geofences fetched: %d', len(geofences))
        for geofence in geofences:
            geofence['_id'] = str(geofence['_id'])
        return jsonify({'geofences': geofences})
    except Exception as e:
        app.logger.error('Error fetching geofences: %s', str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/add_vehicle', methods=['POST'])
def add_vehicle():
    app.logger.debug('add_vehicle endpoint was hit')
    try:
        data = request.json
        vehicle_id = mongo.db['geo-vehicles'].insert_one(data).inserted_id
        app.logger.debug('Vehicle added with ID: %s', vehicle_id)
        return jsonify({'vehicle_id': str(vehicle_id)})
    except Exception as e:
        app.logger.error('Error adding vehicle: %s', str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/delete_geofence/<geofence_id>', methods=['DELETE'])
def delete_geofence(geofence_id):
    app.logger.debug('delete_geofence endpoint was hit')
    try:
        result = mongo.db.Geofence.delete_one({'_id': ObjectId(geofence_id)})
        if result.deleted_count == 1:
            result = mongo.db['geo-vehicles'].delete_many({'geofence_id': geofence_id})
            app.logger.debug('Deleted %d vehicles associated with geofence ID: %s', result.deleted_count, geofence_id)
            return jsonify({'message': 'Geofence and associated vehicles deleted successfully.'})
        else:
            return jsonify({'error': 'Geofence not found.'}), 404
    except Exception as e:
        app.logger.error('Error deleting geofence: %s', str(e))
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='64.227.137.175', port=5000,debug=True)
