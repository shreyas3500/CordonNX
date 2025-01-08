from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from pymongo import MongoClient
import pandas as pd
import sys

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB connection
client = MongoClient('mongodb+srv://doadmin:4T81NSqj572g3o9f@db-mongodb-blr1-27716-c2bd0cae.mongo.ondigitalocean.com/admin?tls=true&authSource=admin')
db = client['CordonEV']
customers_collection = db['customers_list']

@app.route('/')
def index():
    customers = list(customers_collection.find())
    return render_template('index.html', customers=customers)

@app.route('/manual_entry', methods=['POST'])
def manual_entry():
    customer = {
        'Company ID': request.form.get('CompanyID'),
        'Company Name': request.form.get('CompanyName'),
        'Contact Person': request.form.get('ContactPerson'),
        'Email Address': request.form.get('EmailAddress'),
        'Phone Number': request.form.get('PhoneNumber'),
        'Company Address': request.form.get('CompanyAddress'),
        'Number of GPS Devices': request.form.get('NumberOfGPSDevices'),
        'Number of Vehicles': request.form.get('NumberOfVehicles'),
        'Number of Drivers': request.form.get('NumberOfDrivers'),
        'Payment Status': request.form.get('PaymentStatus'),
        'Support Contact': request.form.get('SupportContact'),
        'Remarks': request.form.get('Remarks'),
    }
    customers_collection.insert_one(customer)
    flash('Customer added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/upload_customers', methods=['POST'])
def upload_customers():
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('index'))

    try:
        df = pd.read_excel(file)
        customers_collection.insert_many(df.to_dict('records'))
        flash('Customers uploaded successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('index'))

@app.route('/download_customer_template')
def download_template():
    path = r"/root/CordonNX/CordonNX/nayacomp/templates/Customer_upload_template.xlsx"
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8007
    app.run(host='64.227.137.175', port=8007, debug=True)
