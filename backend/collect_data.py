import cv2
import numpy as np
import os
import mediapipe as mp
from normaliser import normalise_landmarks

SEQUENCE_LEN = 30        # frames per sample
DATA_DIR     = "data"    # where samples get saved

gesture_name = input("Enter gesture name: ")

# Create folder for this gesture if it doesn't exist
save_path = os.path.join(DATA_DIR, gesture_name)
os.makedirs(save_path, exist_ok=True)

print(f"Saving samples to: {save_path}")
# MediaPipe setup
mp_hands = mp.solutions.hands
mp_draw  = mp.solutions.drawing_utils
hands    = mp_hands.Hands()

# Webcam setup
cap     = cv2.VideoCapture(0)
buffer  = []       # holds last 30 frames of landmarks
samples = 0        # how many samples saved so far

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)

    rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get landmarks as list of [x, y, z]
            lm_list = [[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark]

            # Normalise and add to buffer
            normalised = normalise_landmarks(lm_list)
            buffer.append(normalised)

            # Keep only last 30 frames
            if len(buffer) > SEQUENCE_LEN:
                buffer.pop(0)

    # Show status on screen
    cv2.putText(frame, f"Gesture: {gesture_name}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"Samples: {samples}", (10, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"Buffer: {len(buffer)}/30", (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
    cv2.putText(frame, "SPACE=record  Q=quit", (10, 160),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)

    cv2.imshow("H-X-H-2 Collector", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    elif key == ord(" ") and len(buffer) == SEQUENCE_LEN:
        # Save buffer as one .npy file
        sequence = np.stack(buffer)   # shape (30, 63)
        filename = os.path.join(save_path, f"{samples:04d}.npy")
        np.save(filename, sequence)
        samples += 1
        print(f"Saved sample {samples}")

cap.release()
cv2.destroyAllWindows()
print(f"Done. Total samples: {samples}")