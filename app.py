from flask import Flask, render_template, request, jsonify
import boto3
import botocore
import os

app = Flask(__name__)

# Clients AWS
ec2 = boto3.client("ec2")
s3 = boto3.client("s3")

@app.route("/")
def home():
    return render_template("index.html")

# --------- EC2 ----------
@app.route("/ec2", methods=["GET"])
def list_ec2():
    """Lister les instances EC2"""
    instances = ec2.describe_instances()
    result = []
    for reservation in instances["Reservations"]:
        for instance in reservation["Instances"]:
            result.append({
                "InstanceId": instance["InstanceId"],
                "State": instance["State"]["Name"],
                "Type": instance["InstanceType"],
                "Zone": instance["Placement"]["AvailabilityZone"]
            })
    return jsonify(result)

# --------- S3 ----------
@app.route("/s3", methods=["GET"])
def list_buckets():
    """Lister les buckets S3"""
    buckets = [bucket["Name"] for bucket in s3.list_buckets()["Buckets"]]
    return jsonify(buckets)

@app.route("/s3/create", methods=["POST"])
def create_bucket():
    """Créer un bucket"""
    bucket_name = request.form.get("bucket_name")
    if not bucket_name:
        return jsonify({"error": "Le nom du bucket est requis"}), 400

    try:
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={
                "LocationConstraint": boto3.session.Session().region_name
            }
        )
        return jsonify({"message": f"Bucket {bucket_name} créé avec succès"})
    except botocore.exceptions.ClientError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/s3/upload", methods=["POST"])
def upload_file():
    """Uploader un fichier dans un bucket"""
    bucket_name = request.form.get("bucket_name")
    if "file" not in request.files:
        return jsonify({"error": "Aucun fichier reçu"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Nom de fichier invalide"}), 400

    try:
        s3.upload_fileobj(file, bucket_name, file.filename)
        return jsonify({"message": f"Fichier {file.filename} uploadé dans {bucket_name}"})
    except botocore.exceptions.ClientError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/s3/delete", methods=["POST"])
def delete_bucket():
    """Supprimer un bucket"""
    bucket_name = request.form.get("bucket_name")
    if not bucket_name:
        return jsonify({"error": "Le nom du bucket est requis"}), 400
    
    try:
        # Vérifier si le bucket est vide avant suppression
        objects = s3.list_objects_v2(Bucket=bucket_name)
        if "Contents" in objects:
            return jsonify({"error": "Le bucket n'est pas vide, impossible de supprimer"}), 400

        s3.delete_bucket(Bucket=bucket_name)
        return jsonify({"message": f"Bucket {bucket_name} supprimé avec succès"})
    except botocore.exceptions.ClientError as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
