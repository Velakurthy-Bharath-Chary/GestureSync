from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import base64
import cv2
import numpy as np
import tensorflow as tf
import mediapipe as mp
import json
from normaliser import normalise_landmarks
from database import SessionLocal, GestureLog

# ── Load model + classes once ─────────────────────────
model   = tf.keras.models.load_model("gesture_model.h5")
classes = json.load(open("classes.json"))

# ── MediaPipe setup once ──────────────────────────────
mp_hands = mp.solutions.hands
hands    = mp_hands.Hands()

buffer = []

# ── FastAPI app ───────────────────────────────────────
app = FastAPI(title="H-X-H-2 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "H-X-H-2 running"}

@app.get("/gestures")
def get_gestures():
    return {"gestures": classes}

@app.get("/analytics")
def get_analytics():
    db   = SessionLocal()
    logs = db.query(GestureLog).order_by(GestureLog.created_at.desc()).limit(100).all()
    db.close()
    return {
        "total": len(logs),
        "logs": [
            {
                "gesture":    l.gesture,
                "confidence": l.confidence,
                "created_at": str(l.created_at)
            }
            for l in logs
        ]
    }

# ── WebSocket endpoint ────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    global buffer
    buffer = []

    try:
        while True:
            # Receive frame from frontend
            data      = await websocket.receive_json()
            img_bytes = base64.b64decode(data["frame"])
            img_arr   = np.frombuffer(img_bytes, dtype=np.uint8)
            frame     = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)

            # Run MediaPipe
            rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb)

            gesture    = "No hand"
            confidence = 0.0

            if result.multi_hand_landmarks:
                lm_list    = [[lm.x, lm.y, lm.z]
                              for lm in result.multi_hand_landmarks[0].landmark]
                normalised = normalise_landmarks(lm_list)
                buffer.append(normalised)

                if len(buffer) > 30:
                    buffer.pop(0)

                if len(buffer) == 30:
                    sequence   = np.array(buffer)[np.newaxis, ...]
                    prediction = model.predict(sequence, verbose=0)
                    idx        = np.argmax(prediction)
                    confidence = float(prediction[0][idx])
                    gesture    = classes[idx]

            # Log to Supabase
            if gesture != "No hand":
                db = SessionLocal()
                log = GestureLog(
                    gesture    = gesture,
                    confidence = confidence,
                    action     = None
                )
                db.add(log)
                db.commit()
                db.close()

            # Send result back to frontend
            await websocket.send_json({
                "gesture":    gesture,
                "confidence": round(confidence, 3),
            })

    except WebSocketDisconnect:
        pass