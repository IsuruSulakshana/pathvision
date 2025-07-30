# backend/services/file_handler.py
import os
import sys
import json

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

def get_input_dir():
    input_dir = os.path.join(get_base_path(), "data", "input")
    os.makedirs(input_dir, exist_ok=True)
    return input_dir

def list_vehicle_paths():
    input_dir = get_input_dir()
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
    return paths

def load_path_data(filename):
    filepath = os.path.join(get_input_dir(), filename)
    with open(filepath, "r") as f:
        return json.load(f)

def save_path_data(filename, data):
    filepath = os.path.join(get_input_dir(), filename)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)
