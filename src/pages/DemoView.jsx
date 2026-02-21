import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

const CHAT_API_URL = 'http://localhost:8000/api/chat'

export default function DemoView() {
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()
  const url = location.state?.url

  async function handleSend(e) {
    e.preventDefault()
    const userText = message.trim()
    if (!userText) return

    setMessages((prev) => [...prev, { role: 'user', text: userText }])
    setMessage('')
    setLoading(true)

    try {
      const res = await fetch(CHAT_API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userText }),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) {
        throw new Error(data.message ?? data.error ?? `Request failed (${res.status})`)
      }
      const reply = data.reply ?? data.message ?? data.content ?? ''
      setMessages((prev) => [...prev, { role: 'assistant', text: reply }])
    } catch (err) {
      const errorText = err instanceof Error ? err.message : 'Failed to get a response from the AI agent. Please try again.'
      setMessages((prev) => [...prev, { role: 'error', text: errorText }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="demo">
      <header className="demo__header">
        <button
          type="button"
          className="demo__back"
          onClick={() => navigate('/')}
          aria-label="Back to homepage"
        >
          ← Back
        </button>
        <span className="demo__title">Demo</span>
        <span className="demo__status-badge">
          <span className="demo__status-dot" aria-hidden />
          Agent Status: Online
        </span>
        {url && <span className="demo__url">{url}</span>}
      </header>

      <div className="demo__body">
        <main className="demo__main">
          <div className="demo__screen-area">
            <span className="demo__screen-placeholder">
              Screen sharing will appear here
            </span>
          </div>
        </main>

        <div className="demo__roi-widget" aria-label="Economic value">
          <strong>Economic Value</strong>
          <div className="demo__roi-human">Estimated Human Cost: $150/hr</div>
          <div className="demo__roi-agent">Current Agent Cost: $0.05</div>
        </div>

        <aside className="demo__chat">
          <div className="demo__chat-messages">
            {messages.length === 0 && !loading && (
              <p className="demo__chat-empty">
                Type a message to the AI agent below.
              </p>
            )}
            {messages.map((m, i) => (
              <div key={i} className={`demo__chat-msg demo__chat-msg--${m.role}`}>
                {m.text}
              </div>
            ))}
            {loading && (
              <p className="demo__chat-typing">AI agent is typing...</p>
            )}
          </div>
          <form className="demo__chat-form" onSubmit={handleSend}>
            <input
              type="text"
              className="demo__chat-input"
              placeholder="Type a message to the AI agent…"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
            />
            <button type="submit" className="demo__chat-send">
              Send
            </button>
          </form>
        </aside>
      </div>
    </div>
  )
}
