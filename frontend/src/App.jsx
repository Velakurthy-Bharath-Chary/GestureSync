import { useState, useEffect, useRef } from "react"

const WS_URL  = "ws://localhost:8000/ws"
const API_URL = "http://localhost:8000"

export default function App() {
  const [connected,   setConnected]   = useState(false)
  const [gesture,     setGesture]     = useState("No hand")
  const [confidence,  setConfidence]  = useState(0)
  const [history,     setHistory]     = useState([])
  const [analytics,   setAnalytics]   = useState(null)
  const videoRef  = useRef(null)
  const wsRef     = useRef(null)
  const canvasRef = useRef(null)

  // Connect WebSocket
  useEffect(() => {
    const ws = new WebSocket(WS_URL)
    wsRef.current = ws

    ws.onopen  = () => setConnected(true)
    ws.onclose = () => setConnected(false)

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setGesture(data.gesture)
      setConfidence(data.confidence)
      if (data.gesture !== "No hand") {
        setHistory(prev => [data, ...prev].slice(0, 10))
      }
    }

    return () => ws.close()
  }, [])

  // Start webcam
  useEffect(() => {
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream
        }
      })
  }, [])

  // Send frames to backend
  useEffect(() => {
    if (!connected) return

    const interval = setInterval(() => {
      const video  = videoRef.current
      const canvas = canvasRef.current
      if (!video || !canvas) return

      const ctx = canvas.getContext("2d")
      ctx.drawImage(video, 0, 0, 320, 240)
      const b64 = canvas.toDataURL("image/jpeg", 0.7).split(",")[1]
      wsRef.current?.send(JSON.stringify({ frame: b64 }))
    }, 100)

    return () => clearInterval(interval)
  }, [connected])

  // Fetch analytics every 5 seconds
  useEffect(() => {
    const fetch_analytics = () => {
      fetch(`${API_URL}/analytics`)
        .then(r => r.json())
        .then(setAnalytics)
    }
    fetch_analytics()
    const t = setInterval(fetch_analytics, 5000)
    return () => clearInterval(t)
  }, [])

  const color = confidence > 0.6 ? "text-green-400" : "text-yellow-400"

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6">
      <h1 className="text-3xl font-black mb-6">
        H-X-H-2 <span className="text-blue-400">Dashboard</span>
      </h1>

      <div className="grid grid-cols-2 gap-6">

        {/* Left — webcam */}
        <div className="bg-gray-800 rounded-2xl p-4">
          <div className="flex items-center justify-between mb-3">
            <span className="font-semibold">Live Feed</span>
            <span className={`text-xs px-2 py-1 rounded-full ${connected ? "bg-green-900 text-green-400" : "bg-red-900 text-red-400"}`}>
              {connected ? "● Connected" : "● Disconnected"}
            </span>
          </div>
          <video ref={videoRef} autoPlay muted playsInline
            className="w-full rounded-xl" style={{ transform: "scaleX(-1)" }} />
          <canvas ref={canvasRef} width={320} height={240} className="hidden" />

          {/* Gesture badge */}
          <div className="mt-4 text-center">
            <p className={`text-4xl font-black ${color}`}>{gesture}</p>
            <p className="text-gray-400 text-sm mt-1">
              Confidence: {(confidence * 100).toFixed(1)}%
            </p>
            <div className="w-full bg-gray-700 rounded-full h-2 mt-2">
              <div className="h-2 rounded-full bg-blue-500 transition-all duration-200"
                style={{ width: `${confidence * 100}%` }} />
            </div>
          </div>
        </div>

        {/* Right — stats */}
        <div className="space-y-4">

          {/* Analytics summary */}
          <div className="bg-gray-800 rounded-2xl p-4">
            <h2 className="font-semibold mb-3">Analytics</h2>
            {analytics ? (
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-gray-700 rounded-xl p-3 text-center">
                  <p className="text-2xl font-bold text-blue-400">{analytics.total}</p>
                  <p className="text-gray-400 text-xs">Total Gestures</p>
                </div>
                <div className="bg-gray-700 rounded-xl p-3 text-center">
                  <p className="text-2xl font-bold text-green-400">
                    {analytics.logs[0]?.gesture ?? "—"}
                  </p>
                  <p className="text-gray-400 text-xs">Last Gesture</p>
                </div>
              </div>
            ) : (
              <p className="text-gray-500 text-sm">Loading...</p>
            )}
          </div>

          {/* Recent history */}
          <div className="bg-gray-800 rounded-2xl p-4">
            <h2 className="font-semibold mb-3">Recent Gestures</h2>
            {history.length === 0 ? (
              <p className="text-gray-500 text-sm">Show a gesture to see it here</p>
            ) : (
              <div className="space-y-2">
                {history.map((h, i) => (
                  <div key={i} className="flex justify-between items-center bg-gray-700 rounded-lg px-3 py-2">
                    <span className="text-sm font-medium">{h.gesture}</span>
                    <span className="text-xs text-gray-400">
                      {(h.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  )
}