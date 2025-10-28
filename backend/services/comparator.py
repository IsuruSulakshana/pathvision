# backend/services/comparator.py
import numpy as np
from backend.services.path_math import compute_path  # central computation function


def compare_paths(segments1, segments2):
    """
    Compare two paths represented as segments.
    Returns dict with average and max deviation, plus 3D points for both paths.
    """
    # Compute 3D points using the central compute_path function
    shaft_lengths1 = [seg['shaft_length'] for seg in segments1]
    yaw_angles1 = [seg['euler'][0] for seg in segments1]
    pitch_angles1 = [seg['euler'][1] for seg in segments1]

    shaft_lengths2 = [seg['shaft_length'] for seg in segments2]
    yaw_angles2 = [seg['euler'][0] for seg in segments2]
    pitch_angles2 = [seg['euler'][1] for seg in segments2]

    points1 = compute_path(shaft_lengths1, yaw_angles1, pitch_angles1)
    points2 = compute_path(shaft_lengths2, yaw_angles2, pitch_angles2)

    # Align lengths
    length = min(len(points1), len(points2))
    points1 = points1[:length]
    points2 = points2[:length]

    # Compute deviations
    deltas = [float(np.linalg.norm(np.subtract(points1[i], points2[i]))) for i in range(length)]
    avg_deviation = float(np.mean(deltas)) if deltas else 0.0
    max_deviation = float(np.max(deltas)) if deltas else 0.0

    return {
        'points1': points1,
        'points2': points2,
        'avg_deviation': avg_deviation,
        'max_deviation': max_deviation,
        'deltas': deltas
    }
