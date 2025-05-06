from app import app
from flask_ngrok import run_with_ngrok

# run_with_ngrok(app)  # Start ngrok when app is run
if __name__ == "__main__":
    app.run(debug=True, port=8000)  # Run the Flask app
    