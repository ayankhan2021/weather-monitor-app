from flask import Flask, request, jsonify, render_template, send_file, send_from_directory
from dotenv import load_dotenv
load_dotenv()
from pymongo import MongoClient
import os
import json
import requests
from pymongo.errors import ServerSelectionTimeoutError
from datetime import datetime, timedelta, timezone
from flask_mail import Mail, Message

# Load environment variables

app = Flask(__name__)   

# MongoDB config
MONGO_URI = "mongodb+srv://ayan12345:ayan12345@cluster-1.kh6okyv.mongodb.net/air-monitoring"
client = None
db = None
collection = None

def connect_to_mongo():
    global client, db, collection   
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')  # Trigger connection
        db = client["air-monitoring"]
        collection = db["AirMonitoring"]
        print("✅ MongoDB connected successfully.")
    except Exception as e:
        print("❌ MongoDB connection failed:", str(e))
        client, db, collection = None, None, None

# Connect at runtime (non-blocking)
connect_to_mongo()

# Flask config
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FIRMWARE_DIR = os.path.join(BASE_DIR, 'static', 'firmware')
FIRMWARE_PATH = os.path.join(FIRMWARE_DIR, 'GetChipID.ino.bin')

# Mail config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'basit4502929@cloud.neduet.edu.pk'
app.config['MAIL_PASSWORD'] = 'fjvy cxsw gonq sxih'

mail = Mail(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ping-db")
def ping_db():
    if not collection:
        return jsonify({"status": "error", "message": "MongoDB not connected"}), 500
    return jsonify({"status": "success", "message": "MongoDB connected"}), 200

@app.route("/insert", methods=["POST"])
def insert_data():
    if not collection:
        return jsonify({"error": "Database not connected"}), 500
    try:
        raw_data = request.get_data(as_text=True)
        print("📩 Raw body:", raw_data)

        data = request.get_json(force=True)  # ⚠️ Force parsing without content-type check
        print("✅ Parsed JSON:", data)

        if not data:
            return jsonify({"error": "No data received"}), 400

        data["timestamp"] = datetime.now(timezone.utc)
        collection.insert_one(data)
        return jsonify({"message": "Data inserted successfully"}), 201
    except Exception as e:
        print("❌ Insert error:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route("/get-latest")
def get_latest():
    if not collection:
        return jsonify({"error": "Database not connected"}), 500
    try:
        data = collection.find_one(sort=[("timestamp", -1)], projection={"_id": 0})
        if not data:
            return jsonify({"error": "No data found"}), 404
        data["timestamp"] = (data["timestamp"] + timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get-history")
def get_history():
    if not collection:
        return jsonify({"error": "Database not connected"}), 500
    try:
        time_threshold = datetime.now() - timedelta(hours=24)
        data = list(collection.find({"timestamp": {"$gte": time_threshold}}, {"_id": 0}).sort("timestamp", 1))
        formatted = {
            "timestamps": [(d["timestamp"] + timedelta(hours=5)).strftime('%Y-%m-%d %H:%M:%S') for d in data],
            "temperatures": [d["temperature"] for d in data],
            "humidities": [d["humidity"] for d in data],
            "air_qualities": [d["air_quality"] for d in data]
        }
        return jsonify(formatted), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get-firmware")
def get_firmware():
    if not os.path.exists(FIRMWARE_PATH):
        return jsonify({"error": "Firmware file not found"}), 404
    return send_file(FIRMWARE_PATH, mimetype="application/octet-stream", as_attachment=True)

@app.route("/firmware/latest")
def serve_firmware():
    return send_from_directory(FIRMWARE_DIR, "GetChipID.ino.bin", as_attachment=True)

@app.route("/firmware/upload", methods=["POST"])
def upload_firmware():
    token = request.headers.get('Authorization')
    if token != f"Bearer {os.getenv('UPLOAD_SECRET')}":
        return jsonify({"error": "Unauthorized"}), 401
    file = request.files.get('firmware')
    if not file or file.filename == '':
        return jsonify({"error": "No firmware file provided"}), 400
    try:
        os.makedirs(FIRMWARE_DIR, exist_ok=True)
        file.save(FIRMWARE_PATH)
        return jsonify({"message": "Firmware uploaded successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/upload-firmware")
def upload_firmware_form():
    return render_template("upload.html")

@app.route("/send-report")
def send_report():
    return send_all()

def send_all():
    if not collection:
        return "MongoDB not connected", 500
    try:
        data = collection.find_one(sort=[("timestamp", -1)])
        if not data:
            return 'No sensor data found in database!', 404

        msg = Message(
            subject='🌤️ Latest Weather Station Report',
            sender='khan4506342@cloud.neduet.edu.pk',
            recipients=['ak123782651@gmail.com']
        )
        msg.body = f"""
        Here are the latest sensor readings:

        Temperature: {data.get('temperature')} °C
        Humidity: {data.get('humidity')} %
        Air Quality Index: {data.get('air_quality')}
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

        Stay safe and have a nice day! 🌞
        """
        mail.send(msg)
        return 'Weather Report Email Sent!'
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
