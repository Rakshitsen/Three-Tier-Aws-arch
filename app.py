from flask import Flask, render_template, request, redirect
import boto3
import pymysql
import uuid
import datetime

app = Flask(__name__)

# AWS Setup
s3 = boto3.client('s3',region_name='us-east-2')
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
dynamo_table = dynamodb.Table('image_metadata')

rds_host = "database-1.clqes8ciwtrf.us-east-2.rds.amazonaws.com"
rds_user = "admin"
rds_password = "Flower1rose"
rds_db = "initial"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    name = request.form['name']
    location = request.form['location']
    age = request.form['age']
    tech = request.form['technology']
    file = request.files['photo']
    
    if file:
        filename = str(uuid.uuid4()) + "_" + file.filename
        s3.upload_fileobj(file, "sirf-mera-aur-mera-tf-test-bucket", filename)
        upload_time = datetime.datetime.utcnow().isoformat()
        
        # DynamoDB
        dynamo_table.put_item(Item={
            'filename': filename,
            'upload_time': upload_time
        })
        
        # RDS
        connection = pymysql.connect(host=rds_host, user=rds_user,
                                     password=rds_password, db=rds_db)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO employees (name, location, age, technology) VALUES (%s, %s, %s, %s)",
                       (name, location, age, tech))
        connection.commit()
        cursor.close()
        connection.close()
    
    return redirect('/success')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/about')
def about():
    return redirect("http://sirf-mera-aur-mera-tf-test-bucket.s3-website.us-east-2.amazonaws.com")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)