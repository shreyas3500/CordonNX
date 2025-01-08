from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, send_file
from pymongo import MongoClient
from bson.objectid import ObjectId
import pandas as pd
import os
import sys

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Needed to use flash

# MongoDB connection
client = MongoClient("mongodb+srv://doadmin:4T81NSqj572g3o9f@db-mongodb-blr1-27716-c2bd0cae.mongo.ondigitalocean.com/admin?tls=true&authSource=admin")
db = client['CordonEV']
collection = db['device_inventory']

@app.route('/')
def index():
    devices = list(collection.find({}))
    return render_template('index.html', devices=devices)

@app.route('/manual_entry', methods=['POST'])
def manual_entry():
    data = request.form.to_dict()

    # Strip any leading/trailing whitespace
    data['IMEI'] = data['IMEI'].strip()
    data['GLNumber'] = data['GLNumber'].strip()

    # Validate alphanumeric and length
    if len(data['IMEI']) != 15 or len(data['GLNumber']) != 13:
        flash("Invalid IMEI or GL Number length", "danger")
        return redirect(url_for('index'))

    # Check if IMEI or GL Number is unique
    if collection.find_one({"IMEI": data['IMEI']}) or collection.find_one({"GLNumber": data['GLNumber']}):
        flash("IMEI or GL Number already exists", "danger")
        return redirect(url_for('index'))

    # Set status to Active if 'Outward To' is filled
    if data.get('OutwardTo'):
        data['Status'] = 'Active'

    # Insert into MongoDB
    collection.insert_one(data)
    flash("Device added successfully!", "success")
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash("No file part", "danger")
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        flash("No selected file", "danger")
        return redirect(url_for('index'))

    if file and (file.filename.endswith('.xls') or file.filename.endswith('.xlsx')):
        df = pd.read_excel(file)

        # Validate data and prepare for MongoDB insertion
        records = []
        for index, row in df.iterrows():
            imei = str(row['IMEI']).strip()
            gl_number = str(row['GLNumber']).strip()
            device_model = str(row['Device Model']).strip()
            device_make = str(row['Device Make']).strip()
            date_in = str(row['Date In']).split(' ')[0].strip()  # Extract only the date part
            warranty = str(row['Warranty']).split(' ')[0].strip()
            sent_by = str(row['Sent By']).strip()
            outward_to = str(row['Outward to']).strip()
            status = str(row['Status']).strip()

            # Perform necessary validations
            if len(imei) != 15:
                flash(f"Invalid IMEI length at row {index + 2}, column 'IMEI' (Length: {len(imei)})", "danger")
                return redirect(url_for('index'))
            if len(gl_number) != 13:
                flash(f"Invalid GL Number length at row {index + 2}, column 'GLNumber' (Length: {len(gl_number)})", "danger")
                return redirect(url_for('index'))
            if collection.find_one({"IMEI": imei}) or collection.find_one({"GLNumber": gl_number}):
                flash(f"Duplicate IMEI or GL Number at row {index + 2}", "danger")
                return redirect(url_for('index'))

            # Create record to insert
            record = {
                "IMEI": imei,
                "GLNumber": gl_number,
                "Device Model": device_model,
                "Device Make": device_make,
                "Date In": date_in,
                "Warranty": warranty,
                "Sent By": sent_by,
                "Outward to": outward_to,
                "Status": status if status else "Inactive"  # Default to Inactive if status is not provided
            }
            records.append(record)

        # Insert records into MongoDB
        if records:
            collection.insert_many(records)
            flash("File uploaded and devices added successfully!", "success")

        return redirect(url_for('index'))
    else:
        flash("Unsupported file format", "danger")
        return redirect(url_for('index'))

@app.route('/download_template')
def download_template():
    path = r"/root/CordonNX/CordonNX/naya/templates/device_inventory_template.xlsx"
    return send_file(path, as_attachment=True)

@app.route('/edit_device/<device_id>', methods=['POST'])
def edit_device(device_id):
    updated_data = request.json
    result = device_inventory.update_one({'_id': device_id}, {'$set': updated_data})
    return jsonify({'success': result.modified_count > 0})

@app.route('/delete_device/<device_id>', methods=['DELETE'])
def delete_device(device_id):
    result = device_inventory.delete_one({'_id': device_id})
    return jsonify({'success': result.deleted_count > 0})
    

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8003
    app.run(host='64.227.137.175', port=8003)
    # app.run(port=8003, debug=True)
