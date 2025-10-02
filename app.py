from flask import Flask, render_template, request, redirect, url_for
import boto3
import os

app = Flask(__name__)

# -----------------------
# Demander les infos AWS à l'utilisateur
# -----------------------
AWS_ACCESS_KEY_ID = input("Entrez votre AWS Access Key ID : ")
AWS_SECRET_ACCESS_KEY = input("Entrez votre AWS Secret Access Key : ")
AWS_REGION = input("Entrez la région AWS (ex: eu-west-3) : ")

# Création des clients boto3
session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)
s3 = session.client('s3')
ec2 = session.client('ec2')

# -----------------------
# Routes Flask
# -----------------------

@app.route('/')
def index():
    # Lister les instances EC2
    instances = []
    resp = ec2.describe_instances()
    for reservation in resp['Reservations']:
        for i in reservation['Instances']:
            instances.append({
                'InstanceId': i['InstanceId'],
                'State': i['State']['Name']
            })

    # Lister les buckets S3
    buckets = [b['Name'] for b in s3.list_buckets()['Buckets']]

    return render_template('index.html', instances=instances, buckets=buckets)


@app.route('/create_bucket', methods=['POST'])
def create_bucket():
    bucket_name = request.form['bucket_name']
    try:
        s3.create_bucket(Bucket=bucket_name,
                         CreateBucketConfiguration={'LocationConstraint': AWS_REGION})
    except Exception as e:
        return f"Erreur: {e}"
    return redirect(url_for('index'))


@app.route('/upload_file', methods=['POST'])
def upload_file():
    bucket_name = request.form['bucket_name']
    file = request.files['file']
    if file:
        s3.upload_fileobj(file, bucket_name, file.filename)
    return redirect(url_for('index'))


@app.route('/delete_bucket', methods=['POST'])
def delete_bucket():
    bucket_name = request.form['bucket_name']
    try:
        # Supprime tous les objets avant le bucket
        objects = s3.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in objects:
            for obj in objects['Contents']:
                s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
        s3.delete_bucket(Bucket=bucket_name)
    except Exception as e:
        return f"Erreur: {e}"
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
