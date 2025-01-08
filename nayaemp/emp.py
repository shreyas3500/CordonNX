from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from pymongo import MongoClient
import re
import pandas as pd
from datetime import datetime
import sys

app = Flask(__name__)
app.secret_key = "your_secret_key"

# MongoDB connection
client = MongoClient("mongodb+srv://doadmin:4T81NSqj572g3o9f@db-mongodb-blr1-27716-c2bd0cae.mongo.ondigitalocean.com/admin?tls=true&authSource=admin")
db = client["CordonEV"]
collection = db["employees_db"]

# Route to render the main employee management page
@app.route('/')
def index():
    employees = list(collection.find())
    for employee in employees:
        if 'DateOfBirth' in employee:
            employee['DateOfBirth'] = employee['DateOfBirth'].split(" ")[0]
        if 'DateOfJoining' in employee:
            employee['DateOfJoining'] = employee['DateOfJoining'].split(" ")[0]
    return render_template('index.html', employees=employees)

# Route to handle manual entry of employee data
@app.route('/manual_entry', methods=['POST'])
def manual_entry():
    data = request.form.to_dict()

    # Strip any leading/trailing whitespace
    for key in data:
        data[key] = data[key].strip()

    # Format the dates to remove time and seconds
    try:
        data['DateOfBirth'] = datetime.strptime(data['DateOfBirth'], "%Y-%m-%d").strftime("%Y-%m-%d")
        data['DateOfJoining'] = datetime.strptime(data['DateOfJoining'], "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError as e:
        flash(f"Date format error: {e}", "danger")
        return redirect(url_for('index'))

    # Validate phone number and email
    if len(data['PhoneNumber']) != 10 or not data['PhoneNumber'].isdigit():
        flash("Phone Number must be 10 digits long.", "danger")
        return redirect(url_for('index'))

    if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', data['Email']):
        flash("Invalid Email format.", "danger")
        return redirect(url_for('index'))

    # Check if Employee ID is unique
    if collection.find_one({"EmployeeID": data['EmployeeID']}):
        flash("Employee ID already exists.", "danger")
        return redirect(url_for('index'))

    # Insert into MongoDB
    collection.insert_one(data)
    flash("Employee added successfully!", "success")
    return redirect(url_for('index'))

# Route to handle file upload for bulk employee data entry
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash("No file part.", "danger")
        return redirect(url_for('index'))

    file = request.files['file']

    if file.filename == '':
        flash("No selected file.", "danger")
        return redirect(url_for('index'))

    if file and file.filename.endswith('.xlsx'):
        df = pd.read_excel(file)

        for _, row in df.iterrows():
            employee_data = {
                "EmployeeID": str(row['EmployeeID']).strip(),
                "FirstName": str(row['FirstName']).strip(),
                "LastName": str(row['LastName']).strip(),
                "Email": str(row['Email']).strip(),
                "PhoneNumber": str(row['PhoneNumber']).strip(),
                "DateOfBirth": pd.to_datetime(row['DateOfBirth']).strftime("%Y-%m-%d"),
                "DateOfJoining": pd.to_datetime(row['DateOfJoining']).strftime("%Y-%m-%d"),
                "Position": str(row['Position']).strip(),
                "Department": str(row['Department']).strip(),
                "Address": str(row['Address']).strip()
            }

            # Validate phone number and email
            if len(employee_data['PhoneNumber']) != 10 or not employee_data['PhoneNumber'].isdigit():
                flash(f"Invalid phone number for {employee_data['EmployeeID']}. Skipping this entry.", "danger")
                continue

            if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', employee_data['Email']):
                flash(f"Invalid email format for {employee_data['EmployeeID']}. Skipping this entry.", "danger")
                continue

            # Check if Employee ID is unique
            if collection.find_one({"EmployeeID": employee_data['EmployeeID']}):
                flash(f"Employee ID {employee_data['EmployeeID']} already exists. Skipping this entry.", "danger")
                continue

            # Insert into MongoDB
            collection.insert_one(employee_data)

        flash("File uploaded and processed successfully!", "success")
    else:
        flash("Invalid file format. Please upload an .xlsx file.", "danger")

    return redirect(url_for('index'))

# Route to download the employee template
@app.route('/download_template')
def download_template():
    path = r"/root/CordonNX/CordonNX/nayaemp/templates/Employee_upload_template.xlsx"
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8005
    app.run(host='64.227.137.175', port=8005, debug=True)
