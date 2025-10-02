from flask import Flask, render_template, request, jsonify
import boto3

app = Flask(__name__)

# Clients AWS
ec2 = boto3.client("ec2")
s3 = boto3.client("s3")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ec2")
def list_ec2():
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

@app.route("/s3")
def list_buckets():
    buckets = [bucket["Name"] for bucket in s3.list_buckets()["Buckets"]]
    return jsonify(buckets)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
