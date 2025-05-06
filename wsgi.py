from app import app

if __name__ == "__main__":
    with app.app_context():
        app.send_all()    
    app.run(host="0.0.0.0", port=5000, debug=True)