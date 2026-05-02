import cv2
import numpy as np
import mediapipe as mp
import tensorflow as tf
import json
from normaliser import normalise_landmarks
from media_controller import trigger_action
# Load model and classes
model   = tf.keras.models.load_model("gesture_model.h5")
classes = json.load(open("classes.json"))

# MediaPipe setup
mp_hands = mp.solutions.hands
mp_draw  = mp.solutions.drawing_utils
hands    = mp_hands.Hands()

# Webcam
cap         = cv2.VideoCapture(0)
buffer      = []
frame_count = 0
gesture     = "No hand"
confidence  = 0.0
action      = None

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)

    rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            lm_list    = [[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark]
            normalised = normalise_landmarks(lm_list)
            buffer.append(normalised)

            if len(buffer) > 30:
                buffer.pop(0)

            if len(buffer) == 30 and frame_count % 5 == 0:
                sequence   = np.array(buffer)[np.newaxis, ...]
                prediction = model.predict(sequence, verbose=0)
                idx        = np.argmax(prediction)
                confidence = prediction[0][idx]
                gesture    = classes[idx]
                action = trigger_action(gesture, confidence)
                if action:
                    print(action)
    # Display
    color = (0, 255, 0) if confidence > 0.6 else (0, 165, 255)
    cv2.putText(frame, f"Gesture: {gesture}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    cv2.putText(frame, f"Confidence: {confidence*100:.1f}%", (10, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    cv2.putText(frame, f"Action: {action if action else ''}", (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
    frame_count += 1
    cv2.imshow("H-X-H-2", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()