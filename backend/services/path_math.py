# backend/services/path_math.py
import numpy as np

def rotation_matrix_local(yaw_deg, pitch_deg):
    """
    Build a rotation matrix for a shaft segment in its local frame.
    Yaw: rotation about local Z-axis
    Pitch: rotation about local Y-axis
    """
    yaw = np.radians(yaw_deg)
    pitch = np.radians(pitch_deg)

    # Local Z (yaw)
    Rz = np.array([
        [np.cos(yaw), -np.sin(yaw), 0],
        [np.sin(yaw),  np.cos(yaw), 0],
        [0, 0, 1]
    ])

    # Local Y (pitch)
    Ry = np.array([
        [np.cos(pitch), 0, np.sin(pitch)],
        [0, 1, 0],
        [-np.sin(pitch), 0, np.cos(pitch)]
    ])

    # Apply pitch first, then yaw in local frame
    return Ry @ Rz


def compute_path(shaft_lengths, x_angles, y_angles):
    """
    Compute 3D points of a steering path using local rotations.
    x_angles → yaw-like (local Z rotation)
    y_angles → pitch-like (local Y rotation)
    Returns a list of (x, y, z) coordinates.
    """
    if not (len(shaft_lengths) == len(x_angles) == len(y_angles)):
        raise ValueError("All input lists must have the same length")

    points = [np.array([0.0, 0.0, 0.0])]
    orientation = np.eye(3)  # global reference frame

    for l, x_deg, y_deg in zip(shaft_lengths, x_angles, y_angles):
        R_local = rotation_matrix_local(x_deg, y_deg)
        orientation = orientation @ R_local           # update global orientation
        shaft_dir = orientation @ np.array([0, 0, 1]) # local Z-axis in global frame
        new_point = points[-1] + l * shaft_dir
        points.append(new_point)

    return [tuple(p) for p in points]


def compute_path_from_segments(segments):
    """
    Compute 3D points from segments list (dict with 'shaft_length' and 'xyz' [x, y, z]).
    Uses x as yaw-like and y as pitch-like for rotation computation.
    """
    shaft_lengths = [seg['shaft_length'] for seg in segments]
    x_angles = [seg['xyz'][0] for seg in segments]
    y_angles = [seg['xyz'][1] for seg in segments]
    return compute_path(shaft_lengths, x_angles, y_angles)
