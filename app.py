from flask import Flask, request, jsonify, render_template, send_file, abort
from flask_mail import Mail, Message
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta, timezone
from datetime import timedelta
import json

from flask_mail import Mail, Message

load_dotenv()
app = Flask(__name__)

# Load URI from .env
MONGO_URI = os.getenv("MONGODB_URI")

FIRMWARE_PATH = r"C:\Users\JBSS\Desktop\new_weather\GetChipID\build\esp32.esp32.esp32\GetChipID.ino.bin"

# Initialize MongoDB client
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client['air-monitoring'] if 'air-monitoring' not in MONGO_URI else client.get_default_database()
collection = db["AirMonitoring"]

@app.route("/ping-db", methods=["GET"])
def ping_db():
    try:
        client.admin.command('ping')
        return jsonify({"status": "success", "message": "MongoDB connected!"}), 200
    except ServerSelectionTimeoutError as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/insert", methods=["POST"])
def insert_data():
    data = request.get_json()
    print(data)
    if not data:
        return jsonify({"error": "No data received"}), 400
    try:
        # data["timestamp"] = datetime.now()
        data["timestamp"] = datetime.now(timezone.utc)
        collection.insert_one(data)
        return jsonify({"message": "Data inserted successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/get-latest", methods=["GET"])
def get_latest():
    try:
        data = collection.find_one(sort=[("timestamp", -1)], projection={"_id": 0})
        if data and "timestamp" in data:
            # If timestamp is a datetime object
            # Add 5 hours if needed
            adjusted_time = data["timestamp"] + timedelta(hours=5)
            # Format to "YYYY-MM-DD HH:MM:SS"
            data["timestamp"] = adjusted_time.strftime("%Y-%m-%d %H:%M:%S")
            return jsonify(data), 200
        return jsonify({"error": "No data found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get-firmware", methods=["GET"])
def get_firmware():
    try:
        if not os.path.exists(FIRMWARE_PATH):
            return jsonify({"error": "Firmware file not found."}), 404

        return send_file(FIRMWARE_PATH, mimetype="application/octet-stream", as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

from datetime import datetime, timedelta

@app.route("/get-history", methods=["GET"])
def get_history():
    try:
        # Get last 24 hours of data
        time_threshold = datetime.now() - timedelta(hours=24)
        data = list(collection.find(
            {"timestamp": {"$gte": time_threshold}},
            {"_id": 0}
        ).sort("timestamp", 1))
        
        # Format data for charts
        formatted = {
            "timestamps": [],
            "temperatures": [],
            "humidities": [],
            "air_qualities": []
        }

        for item in data:
            # Adjust for 5-hour difference (or whatever your timezone offset is)
            adjusted_time = item['timestamp'] + timedelta(hours=5)
            
            formatted["timestamps"].append(adjusted_time.strftime('%Y-%m-%d %H:%M:%S'))
            formatted["temperatures"].append(item['temperature'])
            formatted["humidities"].append(item['humidity'])
            formatted["air_qualities"].append(item['air_quality'])
        
        return jsonify(formatted), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'basit4502929@cloud.neduet.edu.pk'
app.config['MAIL_PASSWORD'] = 'fjvy cxsw gonq sxih'

mail = Mail(app)


def send_all():
    try:
        # Fetch latest document from MongoDB
        latest_data = collection.find_one(sort=[("timestamp", -1)])
        
        if latest_data:
            temperature = latest_data.get('temperature')
            humidity = latest_data.get('humidity')
            air_quality = latest_data.get('air_quality') 
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') # Changed from "pressure" to your real field

            msg = Message('🌤️ Latest Weather Station Report',
                          sender='khan4506342@cloud.neduet.edu.pk',
                          recipients=['ak123782651@gmail.com'])

            msg.body = f"""
            Here are the latest sensor readings:

            Temperature: {temperature} °C
            Humidity: {humidity} %
            Air Quality Index: {air_quality}
            Current Time: {current_time}

            Stay safe and have a nice day! 🌞
            """
            msg.content_type = "text/plain"

            mail.send(msg)
            return 'Weather Report Email Sent!'
        else:
            return 'No sensor data found in database!', 404
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

if __name__ == "__main__":
    with app.app_context():
        send_all()    
    app.run(host="0.0.0.0", port=5000, debug=True)