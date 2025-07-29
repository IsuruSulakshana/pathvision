# backend/services/angle_diff.py

def compute_cumulative_angle_differences(segments1, segments2):
    """
    Compute cumulative relative angle differences segment-wise.
    Each difference is corrected by the sum of previous differences.
    Returns list of dicts: [{'yaw_diff': val, 'pitch_diff': val, 'roll_diff': val}, ...]
    """
    length = min(len(segments1), len(segments2))
    diffs = []
    correction = [0.0, 0.0, 0.0]  # yaw, pitch, roll

    for i in range(length):
        seg1 = segments1[i]['euler']
        seg2 = segments2[i]['euler']

        # Apply correction to second path segment angles
        corrected_seg2 = [
            seg2[0] - correction[0],
            seg2[1] - correction[1],
            seg2[2] - correction[2],
        ]

        # Calculate signed difference
        yaw_diff = corrected_seg2[0] - seg1[0]
        pitch_diff = corrected_seg2[1] - seg1[1]
        roll_diff = corrected_seg2[2] - seg1[2]

        diffs.append({
            'yaw_diff': yaw_diff,
            'pitch_diff': pitch_diff,
            'roll_diff': roll_diff,
        })

        # Update correction vector cumulatively
        correction[0] += yaw_diff
        correction[1] += pitch_diff
        correction[2] += roll_diff

    return diffs
