# backend/services/comparator.py
import numpy as np

def compute_path_points(segments):
    """
    Compute 3D points from shaft lengths and Euler angles (yaw, pitch).
    """
    points = [(0, 0, 0)]
    x, y, z = 0, 0, 0

    for seg in segments:
        l = seg['shaft_length']
        yaw_deg = seg['euler'][0]
        pitch_deg = seg['euler'][1]

        yaw_rad = np.radians(yaw_deg)
        pitch_rad = np.radians(pitch_deg)

        dx = l * np.cos(pitch_rad) * np.cos(yaw_rad)
        dy = l * np.cos(pitch_rad) * np.sin(yaw_rad)
        dz = l * np.sin(pitch_rad)

        x += dx
        y += dy
        z += dz
        points.append((x, y, z))

    return points

def compare_paths(segments1, segments2):
    """
    Compare two paths represented as segments.
    Returns dict with average and max deviation, plus 3D points for both paths.
    """
    points1 = compute_path_points(segments1)
    points2 = compute_path_points(segments2)

    length = min(len(points1), len(points2))
    points1 = points1[:length]
    points2 = points2[:length]

    deltas = [np.linalg.norm(np.subtract(points1[i], points2[i])) for i in range(length)]

    avg_deviation = float(np.mean(deltas)) if deltas else 0.0
    max_deviation = float(np.max(deltas)) if deltas else 0.0

    return {
        'points1': points1,
        'points2': points2,
        'avg_deviation': avg_deviation,
        'max_deviation': max_deviation,
        'deltas': deltas
    }

def extract_path_points(segments):
    """
    Converts a list of segment dictionaries into a list of 3D points (x, y, z).
    """
    return [(seg["x"], seg["y"], seg["z"]) for seg in segments]
            
         