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
collection = db['sim_inventory']

@app.route('/')
def index():
    sims = list(collection.find({}))
    return render_template('index.html', sims=sims)

@app.route('/manual_entry', methods=['POST'])
def manual_entry():
    data = request.form.to_dict()

    # Strip any leading/trailing whitespace
    data['MobileNumber'] = data['MobileNumber'].strip()
    data['SimNumber'] = data['SimNumber'].strip()

    # Validate alphanumeric and length
    if len(data['MobileNumber']) != 10 or len(data['SimNumber']) != 20:
        flash("Invalid Mobile Number or SIM Number length", "danger")
        return redirect(url_for('index'))

    # Check if Mobile Number or SIM Number is unique
    if collection.find_one({"MobileNumber": data['MobileNumber']}) or collection.find_one({"SimNumber": data['SimNumber']}):
        flash("Mobile Number or SIM Number already exists", "danger")
        return redirect(url_for('index'))

    # Insert into MongoDB
    collection.insert_one(data)
    flash("SIM added successfully!", "success")
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
            mobile_number = str(row['MobileNumber']).strip()
            sim_number = str(row['SimNumber']).strip()
            date_in = str(row['DateIn']).split(' ')[0].strip()
            date_out = str(row['DateOut']).split(' ')[0].strip() if not pd.isnull(row['DateOut']) else ""
            vendor = str(row['Vendor']).strip()

            # Perform necessary validations
            if len(mobile_number) != 10:
                flash(f"Invalid Mobile Number length at row {index + 2}, column 'MobileNumber' (Length: {len(mobile_number)})", "danger")
                return redirect(url_for('index'))
            if len(sim_number) != 20:
                flash(f"Invalid SIM Number length at row {index + 2}, column 'SimNumber' (Length: {len(sim_number)})", "danger")
                return redirect(url_for('index'))
            if collection.find_one({"MobileNumber": mobile_number}) or collection.find_one({"SimNumber": sim_number}):
                flash(f"Duplicate Mobile Number or SIM Number at row {index + 2}", "danger")
                return redirect(url_for('index'))

            # Create record to insert
            record = {
                "MobileNumber": mobile_number,
                "SimNumber": sim_number,
                "Date In": date_in,
                "Date Out": date_out,
                "Vendor": vendor,
            }
            records.append(record)

        # Insert records into MongoDB
        if records:
            collection.insert_many(records)
            flash("File uploaded and SIMs added successfully!", "success")

        return redirect(url_for('index'))
    else:
        flash("Unsupported file format", "danger")
        return redirect(url_for('index'))

@app.route('/download_template')
def download_template():
    filepath = r"/root/CordonNX/CordonNX/nayasim/templates/sim_inventory_template.xlsx"
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8004
    app.run(host='0.0.0.0', port=8004, debug=True)