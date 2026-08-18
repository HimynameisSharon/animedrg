import os
import time
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, current_app

# Handle import resolution regardless of how script is invoked
try:
    from models.db import supabase
except ModuleNotFoundError:
    try:
        from db import supabase
    except ModuleNotFoundError:
        import sys
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        from models.db import supabase

ingest_bp = Blueprint("ingest", __name__)

@ingest_bp.route("/v1/ingest", methods=["POST"])
def ingest():
    start_time = time.time()
    
    print("\n==========================================", flush=True)
    print("🚨 POST REQUEST RECEIVED AT /v1/ingest", flush=True)
    
    try:
        data = request.get_json(force=True, silent=True) or {}
        
        print("📥 Incoming Raw Payload:", data, flush=True)
        print("==========================================\n", flush=True)

        # Extract raw payload
        raw_payload = data.get("payload", data)

        # Extract metric values with fallbacks
        bw = raw_payload.get("weight_kg") or raw_payload.get("bw") or raw_payload.get("weight") or 0.0
        temp = raw_payload.get("temp_c") or raw_payload.get("avg_temp") or raw_payload.get("temp") or 0.0
        confidence = raw_payload.get("confidence_score") if raw_payload.get("confidence_score") is not None else raw_payload.get("confidence", 0.95)
        animal_type = raw_payload.get("animal_type") or "chicken"

        # Clean payload mapping explicitly matching active Supabase columns
        mapped_data = {
            "device_id": str(data.get("device_info", {}).get("id") or data.get("device_id") or "Jetson-01"),
            "animal_type": str(animal_type),
            "weight_kg": float(bw),
            "temp_c": float(temp),
            "humidity_pct": raw_payload.get("humidity_pct") or raw_payload.get("humidity"),
            "confidence_score": float(confidence),
            
            
            # Dual-Camera Streaming Metrics (Top & Side Cameras + Chest Gap)
            "length1_cm": raw_payload.get("length1_cm"),
            "breadth1_cm": raw_payload.get("breadth1_cm"),
            "area1_cm2": raw_payload.get("area1_cm2"),
            "length2_cm": raw_payload.get("length2_cm"),
            "height1_cm": raw_payload.get("height1_cm"),
            "height2_cm": raw_payload.get("height2_cm"),
            "area2_cm2": raw_payload.get("area2_cm2"),
            "chest_gap_cm": raw_payload.get("chest_gap_cm"),
            
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        # Safely append optional fields only if provided in raw_payload to prevent PGRST204 schema errors
        if raw_payload.get("tag_no") or raw_payload.get("tag"):
            mapped_data["tag_no"] = str(raw_payload.get("tag_no") or raw_payload.get("tag"))

        print("⚙️ Mapped Payload for Supabase:", mapped_data, flush=True)

        # Insert into Supabase
        if supabase:
            response = supabase.table("measurements").insert(mapped_data).execute()
            
            elapsed = time.time() - start_time
            print(f"✅ Supabase Response ({elapsed:.2f}s):", response.data, flush=True)
            
            return jsonify({"status": "ok", "message": "Saved", "data": response.data}), 201
        else:
            print("⚠️ Supabase client not initialized!", flush=True)
            return jsonify({"status": "error", "message": "Database client uninitialized"}), 500

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Ingest Error after {elapsed:.2f}s:", str(e), flush=True)
        return jsonify({"status": "error", "message": str(e)}), 500