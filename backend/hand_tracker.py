import cv2
import mediapipe as mp

# Setup MediaPipe
mp_hands = mp.solutions.hands
mp_draw  = mp.solutions.drawing_utils
hands    = mp_hands.Hands()

# Setup webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)

    # Convert to RGB for MediaPipe
    rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    # Draw landmarks if hand detected
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            for i, lm in enumerate(hand_landmarks.landmark):
                print(f"Point {i}: x={lm.x:.3f}  y={lm.y:.3f}  z={lm.z:.3f}")
    cv2.imshow("H-X-H-2", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()