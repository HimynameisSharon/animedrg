from flask import Blueprint, jsonify
from models.db import supabase

measurements_bp = Blueprint("measurements", __name__)

@measurements_bp.route("/v1/measurements", methods=["GET"])
def get_all_measurements():
    try:
        result = supabase.table("measurements").select("*").execute()
        return jsonify({"status": "ok", "data": result.data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@measurements_bp.route("/v1/measurements/<id>", methods=["GET"])
def get_one_measurement(id):
    try:
        result = supabase.table("measurements").select("*").eq("id", id).execute()
        if not result.data:
            return jsonify({"error": "Measurement not found"}), 404
        return jsonify({"status": "ok", "data": result.data[0]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@measurements_bp.route("/v1/status", methods=["GET"])
def status():
    try:
        devices = supabase.table("devices").select("*").execute()
        measurements = supabase.table("measurements").select("*").execute()
        return jsonify({
            "status": "online",
            "total_devices": len(devices.data),
            "total_measurements": len(measurements.data)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500