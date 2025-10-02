# app.py

from flask import Flask, render_template
from aws_config import s3_client

app = Flask(__name__)

def list_buckets():
    """Récupère la liste des buckets S3"""
    response = s3_client.list_buckets()
    buckets = [bucket["Name"] for bucket in response.get("Buckets", [])]
    return buckets

@app.route("/")
def home():
    buckets = list_buckets()
    return render_template("index.html", buckets=buckets)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

