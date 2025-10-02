from flask import Flask, render_template, request, redirect, url_for, flash
import boto3
import botocore

app = Flask(__name__)
app.secret_key = "une_clef_secrete_pour_flask"

# Clients AWS
ec2 = boto3.client("ec2")
s3 = boto3.client("s3")

# --------- HOME ----------
@app.route("/")
def home():
    return render_template("index.html")

# --------- EC2 ----------
@app.route("/ec2")
def ec2_page():
    """Page HTML qui liste les instances EC2"""
    instances_data = []
    instances = ec2.describe_instances()
    for reservation in instances["Reservations"]:
        for instance in reservation["Instances"]:
            instances_data.append({
                "InstanceId": instance["InstanceId"],
                "State": instance["State"]["Name"],
                "Type": instance["InstanceType"],
                "Zone": instance["Placement"]["AvailabilityZone"]
            })
    return render_template("ec2.html", instances=instances_data)

# --------- S3 ----------
@app.route("/s3")
def s3_page():
    """Page HTML pour gérer les buckets S3"""
    buckets = [bucket["Name"] for bucket in s3.list_buckets()["Buckets"]]
    return render_template("s3.html", buckets=buckets)

@app.route("/s3/create", methods=["POST"])
def create_bucket():
    bucket_name = request.form.get("bucket_name")
    if not bucket_name:
        flash("Le nom du bucket est requis", "error")
        return redirect(url_for("s3_page"))

    try:
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={
                "LocationConstraint": boto3.session.Session().region_name
            }
        )
        flash(f"Bucket {bucket_name} créé avec succès", "success")
    except botocore.exceptions.ClientError as e:
        flash(f"Erreur: {e}", "error")
    return redirect(url_for("s3_page"))

@app.route("/s3/upload", methods=["POST"])
def upload_file():
    bucket_name = request.form.get("bucket_name")
    if "file" not in request.files or request.files["file"].filename == "":
        flash("Aucun fichier sélectionné", "error")
        return redirect(url_for("s3_page"))

    file = request.files["file"]
    try:
        s3.upload_fileobj(file, bucket_name, file.filename)
        flash(f"Fichier {file.filename} uploadé dans {bucket_name}", "success")
    except botocore.exceptions.ClientError as e:
        flash(f"Erreur: {e}", "error")
    return redirect(url_for("s3_page"))

@app.route("/s3/delete", methods=["POST"])
def delete_bucket():
    bucket_name = request.form.get("bucket_name")
    if not bucket_name:
        flash("Le nom du bucket est requis", "error")
        return redirect(url_for("s3_page"))

    try:
        objects = s3.list_objects_v2(Bucket=bucket_name)
        if "Contents" in objects:
            flash("Le bucket n'est pas vide, impossible de supprimer", "error")
            return redirect(url_for("s3_page"))

        s3.delete_bucket(Bucket=bucket_name)
        flash(f"Bucket {bucket_name} supprimé avec succès", "success")
    except botocore.exceptions.ClientError as e:
        flash(f"Erreur: {e}", "error")
    return redirect(url_for("s3_page"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
