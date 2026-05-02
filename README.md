# GestureSync 🤚

Real-time hand gesture recognition system for touchless media control.
Built with Python, MediaPipe, TensorFlow LSTM, FastAPI, React, and Supabase.

## What it does
Controls media playback using hand gestures detected through a webcam.
No touch required.

## Gestures
| Gesture | Action |
|---|---|
| ✊ Fist | Play / Pause |
| 🖐 Open Palm | Mute |
| ☞ Index Point | Previous Track |
| ✌ Peace | Next Track |
| 👍 Thumbs Up | Fullscreen |

## Architecture
Webcam → MediaPipe (21 landmarks) → Normaliser → LSTM Model → FastAPI → React Dashboard

## Tech Stack
- Python, OpenCV, MediaPipe
- TensorFlow / Keras LSTM (99% accuracy)
- FastAPI + WebSocket
- React + Tailwind + Recharts
- Supabase (PostgreSQL)

## Run it
**Backend:**
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

**Frontend:**
cd frontend
npm install
npm run dev

## Model
- Input: 30 frames × 63 landmarks = (30, 63) sequence
- Architecture: LSTM(128) → LSTM(64) → Dense(64) → Dense(5)
- Accuracy: 99% on test set