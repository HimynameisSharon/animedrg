<<<<<<< HEAD
from flask import Flask
from flask_cors import CORS
from models.db import supabase
from routes.heartbeat import heartbeat_bp
from routes.ingest import ingest_bp
from routes.measurements import measurements_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(heartbeat_bp)
app.register_blueprint(ingest_bp)
app.register_blueprint(measurements_bp)

@app.route("/")
def index():
    return {"message": "ANiMeDRig backend is running"}, 200

@app.route("/test-db")
def test_db():
    try:
        result = supabase.table("devices").select("*").execute()
        return {"status": "Supabase connected", "data": result.data}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

if __name__ == "__main__":
=======
from flask import Flask
from flask_cors import CORS
from models.db import supabase
from routes.heartbeat import heartbeat_bp
from routes.ingest import ingest_bp
from routes.measurements import measurements_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(heartbeat_bp)
app.register_blueprint(ingest_bp)
app.register_blueprint(measurements_bp)

@app.route("/")
def index():
    return {"message": "ANiMeDRig backend is running"}, 200

@app.route("/test-db")
def test_db():
    try:
        result = supabase.table("devices").select("*").execute()
        return {"status": "Supabase connected", "data": result.data}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

if __name__ == "__main__":
>>>>>>> f4bb7e7d089993ef621558cac8ad3475bccef42b
    app.run(debug=True)