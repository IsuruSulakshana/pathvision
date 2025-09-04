# backend/services/file_handler.py

import os
import sys
import json

def get_config_path():
    """Return the path to config.json, depending on whether running as PyInstaller bundle or source."""
    if getattr(sys, 'frozen', False):
        # Running from PyInstaller bundle
        exe_dir = os.path.dirname(sys.executable)
    else:
        # Running from source
        exe_dir = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(exe_dir, "config.json")


def create_default_config(config_file):
    """Create a default config.json with a default shared input path."""
    default_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(config_file))), "data", "input")
    os.makedirs(default_path, exist_ok=True)
    config = {"shared_input_path": default_path}
    with open(config_file, "w") as f:
        json.dump(config, f, indent=4)
    print(f"[INFO] Created default config.json at {config_file} with path: {default_path}")
    return default_path


def get_shared_input_path():
    """Return the shared input path from config.json, creating it if missing."""
    config_file = get_config_path()
    if not os.path.exists(config_file):
        return create_default_config(config_file)

    try:
        with open(config_file, "r") as f:
            config = json.load(f)
            path = config.get("shared_input_path")
            if path:
                os.makedirs(path, exist_ok=True)
                return path
            else:
                print(f"[WARN] 'shared_input_path' missing in config.json. Recreating config.")
                return create_default_config(config_file)
    except Exception as e:
        print(f"[ERROR] Failed to read config.json: {e}. Recreating config.")
        return create_default_config(config_file)


def get_input_dir():
    """Return the input directory path; raise exception if not found."""
    path = get_shared_input_path()
    if path:
        return path
    raise Exception("Shared input path not found in config.json")


def list_vehicle_paths():
    """Return a list of tuples (filename, vehicle) for all JSON vehicle path files."""
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
    """Load JSON data of a given path file."""
    filepath = os.path.join(get_input_dir(), filename)
    with open(filepath, "r") as f:
        return json.load(f)


def save_path_data(filename, data):
    """Save JSON data to a path file."""
    filepath = os.path.join(get_input_dir(), filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)
