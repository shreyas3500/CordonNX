from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, send_file
from pymongo import MongoClient
import pandas as pd
import os
import sys

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Needed to use flash

# MongoDB connection
client = MongoClient("mongodb+srv://doadmin:4T81NSqj572g3o9f@db-mongodb-blr1-27716-c2bd0cae.mongo.ondigitalocean.com/admin?tls=true&authSource=admin")
db = client['CordonEV']
driver_collection = db['driver_inventory']

@app.route('/')
def index():
    drivers = list(driver_collection.find({}))
    return render_template('index.html', drivers=drivers)

@app.route('/manual_driver_entry', methods=['POST'])
def manual_driver_entry():
    # Retrieve data from the form
    data = request.form.to_dict()

    # Strip any leading/trailing whitespace from form data
    data = {key.strip(): value.strip() for key, value in data.items()}

    # Define the mapping between form field names and database field names
    field_mapping = {
        "DriverID": "Driver ID",
        "DriverName": "Driver Name",
        "LicenseNumber": "License Number",
        "PhoneNumber": "Phone Number",
        "Address": "Address",
        "DateOfHire": "Date of Hire",
        "DateOfBirth": "Date of Birth",
        "EmergencyContact": "Emergency Contact",
        "EmergencyPhone": "Emergency Phone",
        "LicensePlateNumber": "License Plate Number",  # Added License Plate Number
        "CurrentStatus": "Current Status"
    }

    # Create a record with mapped fields
    record = {db_field: data.get(form_field) for form_field, db_field in field_mapping.items()}

    # Validate required fields
    required_fields = ['Driver ID', 'Driver Name', 'License Number', 'License Plate Number']
    for field in required_fields:
        if not record.get(field):
            flash(f"{field} is required.", "danger")
            return redirect(url_for('index'))

    # Insert the record into MongoDB
    driver_collection.insert_one(record)
    flash("Driver added successfully!", "success")
    return redirect(url_for('index'))

@app.route('/upload_driver', methods=['POST'])
def upload_file_driver():
    if 'file' not in request.files:
        flash("No file part", "danger")
        return redirect(url_for('index'))

    file = request.files['file']
    
    if file.filename == '':
        flash("No selected file", "danger")
        return redirect(url_for('index'))

    try:
        # Read the Excel file
        df = pd.read_excel(file)

        # Define the field mapping for driver entries
        field_mapping = {
            "DriverID": "Driver ID",
            "DriverName": "Driver Name",
            "LicenseNumber": "License Number",
            "PhoneNumber": "Phone Number",
            "Address": "Address",
            "DateOfHire": "Date of Hire",
            "DateOfBirth": "Date of Birth",
            "EmergencyContact": "Emergency Contact",
            "EmergencyPhone": "Emergency Phone",
            "LicensePlateNumber": "License Plate Number",
            "CurrentStatus": "Current Status"
        }

        # Apply the mapping to each row in the DataFrame
        df.rename(columns=field_mapping, inplace=True)

        # Convert the DataFrame to a list of dictionaries
        data = df.to_dict(orient='records')

        # Insert the data into MongoDB
        driver_collection.insert_many(data)
        flash("File uploaded and drivers added successfully!", "success")
    except Exception as e:
        flash(f"An error occurred while processing the file: {str(e)}", "danger")
    
    return redirect(url_for('index'))


@app.route('/download_driver_template')
def download_driver_template():
    # Construct the absolute path to the template file
    filepath = os.path.join(os.path.dirname(__file__), 'templates', 'driver_upload_template.xlsx')
    
    # Check if the file exists
    if not os.path.exists(filepath):
        flash("Template file not found.", "danger")
        return redirect(url_for('index'))
    
    return send_file(filepath, as_attachment=True)



if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8009
    app.run(host='64.227.137.175', port=8009, debug=True)
# app.run(port=8009, debug=True)
