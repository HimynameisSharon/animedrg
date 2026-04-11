from flask import Blueprint, request, jsonify
from models.db import supabase
import os
from datetime import datetime, timezone

ingest_bp = Blueprint("ingest", __name__)

@ingest_bp.route("/v1/ingest", methods=["POST"])
def ingest():
    data = request.get_json()

    # Check auth token
    token = data.get("auth_token")
    if token != os.getenv("HARDWARE_SECRET_TOKEN"):
        return jsonify({"error": "Unauthorized"}), 401

    # Get device info
    device_info = data.get("device_info", {})
    device_id = device_info.get("id")
    if not device_id:
        return jsonify({"error": "device_id is required"}), 400

    # Check device exists
    device = supabase.table("devices").select("*").eq("device_id", device_id).execute()
    if not device.data:
        return jsonify({"error": "Device not found"}), 404

    # Get payload
    payload = data.get("payload", {})

    # Save measurement
    measurement = {
        "device_id": device.data[0]["id"],
        "weight_kg": payload.get("weight_kg"),
        "temp_c": payload.get("temp_c"),
        "humidity_pct": payload.get("humidity"),
        "angle": payload.get("angle"),
        "confidence_score": payload.get("confidence"),
        "status": "active",
        "created_at": payload.get("timestamp", datetime.now(timezone.utc).isoformat())
    }

    result = supabase.table("measurements").insert(measurement).execute()

    return jsonify({
        "status": "ok",
        "message": "Measurement saved",
        "data": result.data
    }), 201