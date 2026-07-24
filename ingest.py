from flask import Blueprint, request, jsonify
from models.db import supabase
import os
from datetime import datetime, timezone

ingest_bp = Blueprint("ingest", __name__)

@ingest_bp.route("/v1/ingest", methods=["POST"])
def ingest():
    try:
        data = request.get_json() or {}

        # 1. Check auth token
        token = data.get("auth_token")
        if token != os.getenv("HARDWARE_SECRET_TOKEN"):
            return jsonify({"error": "Unauthorized"}), 401

        # 2. Get device info
        device_info = data.get("device_info", {})
        device_id = device_info.get("id")
        if not device_id:
            return jsonify({"error": "device_id is required"}), 400

        # 3. Check device exists
        device = supabase.table("devices").select("*").eq("device_id", device_id).execute()
        if not device.data:
            return jsonify({"error": "Device not found"}), 404

        # 4. Get payload & construct measurement
        payload = data.get("payload", {})

        measurement = {
            "device_id": device.data[0]["id"],
            "weight_kg": payload.get("weight_kg"),
            "temp_c": payload.get("temp_c"),
            "humidity_pct": payload.get("humidity"),
            "angle": payload.get("angle"),
            "confidence_score": payload.get("confidence"),
            
            # --- Added Missing Fields ---
            "animal_type": payload.get("animal_type"),
            "length_cm": payload.get("length_cm"),
            "breadth_cm": payload.get("breadth_cm"),
            "light_pct": payload.get("light_pct", payload.get("light")), # Handles 'light_pct' or 'light'
            
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        # 5. Insert into Supabase
        result = supabase.table("measurements").insert(measurement).execute()
        return jsonify({"status": "ok", "message": "Saved", "data": result.data}), 201

    except Exception as e:
        # Detailed error log in console for debugging
        print(f"Sync Error Details: {repr(e)}")
        return jsonify({"status": "error", "message": "Database sync failed", "details": str(e)}), 500