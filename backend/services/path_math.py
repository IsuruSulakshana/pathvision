import numpy as np

def compute_path(shaft_lengths, yaw_angles, pitch_angles):
    pitch_rad = np.radians(pitch_angles)
    yaw_rad = np.radians(yaw_angles)
    points = [(0.0, 0.0, 0.0)]
    for i in range(len(shaft_lengths)):
        L = shaft_lengths[i]
        pitch = pitch_rad[i]
        yaw = yaw_rad[i]
        dx = L * np.cos(pitch) * np.cos(yaw)
        dy = L * np.cos(pitch) * np.sin(yaw)
        dz = L * np.sin(pitch)
        last_point = points[-1]
        new_point = (last_point[0] + dx, last_point[1] + dy, last_point[2] + dz)
        points.append(new_point)
    return points
