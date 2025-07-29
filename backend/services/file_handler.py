# backend/services/file_handler.py
import os
import json

def list_vehicle_paths():
    input_dir = "data/input"
    paths = []
    for filename in os.listdir(input_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(input_dir, filename)
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                    if "vehicle" in data:
                        paths.append((filename, data["vehicle"]))
            except Exception:
                continue
    return paths  # List of (filename, vehicle_name)

def load_path_data(filename):
    filepath = os.path.join("data/input", filename)
    with open(filepath, "r") as f:
        data = json.load(f)
    return data  # Full dictionary with 'vehicle' and 'segments'
