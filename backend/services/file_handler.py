# backend/services/file_handler.py

import os
import sys
import json

def get_config_path():
    if getattr(sys, 'frozen', False):
        # Running from PyInstaller bundle
        exe_dir = os.path.dirname(sys.executable)
    else:
        # Running from source
        exe_dir = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(exe_dir, "config.json")


def get_shared_input_path():
    config_file = get_config_path()
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
                return config.get("shared_input_path")
        except Exception as e:
            print(f"[ERROR] Failed to read config.json: {e}")
            return None
    else:
        print(f"[ERROR] config.json not found at {config_file}")
    return None


def get_input_dir():
    path = get_shared_input_path()
    if path:
        os.makedirs(path, exist_ok=True)
        return path
    raise Exception("Shared input path not found in config.json")


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
