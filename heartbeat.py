from flask import Blueprint, request, jsonify
from models.db import supabase
import os

heartbeat_bp = Blueprint("heartbeat", __name__)

@heartbeat_bp.route("/v1/heartbeat", methods=["POST"])
def heartbeat():
    data = request.get_json()

    # Check auth token
    token = data.get("auth_token")
    if token != os.getenv("HARDWARE_SECRET_TOKEN"):
        return jsonify({"error": "Unauthorized"}), 401

    device_id = data.get("device_id")
    if not device_id:
        return jsonify({"error": "device_id is required"}), 400

    # Check if device exists
    result = supabase.table("devices").select("*").eq("device_id", device_id).execute()
    if not result.data:
        return jsonify({"error": "Device not found"}), 404

    return jsonify({"status": "ok", "device_id": device_id}), 200