import numpy as np

def normalise_landmarks(landmarks):
    pts = np.array(landmarks, dtype=np.float32)  # shape (21, 3)

    # Step 1: subtract wrist (point 0) from every point
    pts = pts - pts[0]

    # Step 2: calculate scale — distance from wrist to point 9
    scale = np.linalg.norm(pts[9])

    # Step 3: divide everything by scale
    pts = pts / scale

    # Step 4: flatten (21, 3) → (63,) and return
    return pts.flatten()
# Quick test
# Better test — wrist at bottom, fingers spread upward
