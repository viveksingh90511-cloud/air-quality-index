import React, { useState, useRef, useEffect } from 'react'
import { apiClient, endpoints } from '../api/client'

// Responses now come from the backend API

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([
    { role: 'assistant', content: '👋 Hi! I\'m your AI Health Assistant. Ask me about air quality, masks, or health precautions!' }
  ])
  const [input, setInput] = useState('')
  const messagesEnd = useRef(null)

  useEffect(() => { messagesEnd.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const [isLoading, setIsLoading] = useState(false)

  const send = async () => {
    if (!input.trim() || isLoading) return
    const userMsg = input.trim()
    setMessages(prev => [...prev, { role: 'user', content: userMsg }])
    setInput('')
    setIsLoading(true)

    try {
      const res = await apiClient.post(endpoints.chat, { message: userMsg })
      if (res && res.response) {
        setMessages(prev => [...prev, { role: 'assistant', content: res.response }])
      }
    } catch (err) {
      console.error('Chat error:', err)
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I am having trouble connecting to the server.' }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="chat-widget">
      {isOpen && (
        <div className="chat-panel">
          <div style={{ padding: '14px 16px', borderBottom: '1px solid var(--border-glass)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ fontSize: '1.2rem' }}>🤖</span>
              <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>AI Health Assistant</span>
            </div>
            <button onClick={() => setIsOpen(false)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '1.2rem' }}>✕</button>
          </div>
          <div className="chat-messages">
            {messages.map((msg, i) => (
              <div key={i} className={`chat-message ${msg.role}`}>
                {msg.content.split('\n').map((line, j) => (
                  <React.Fragment key={j}>{line}<br /></React.Fragment>
                ))}
              </div>
            ))}
            <div ref={messagesEnd} />
          </div>
          <div className="chat-input-area">
            <input className="chat-input" value={input} onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && send()}
              placeholder="Ask about air quality..." id="chat-input"
            />
            <button className="btn btn-primary" onClick={send} style={{ padding: '8px 14px' }} id="chat-send-btn">Send</button>
          </div>
        </div>
      )}
      <button className="chat-toggle" onClick={() => setIsOpen(!isOpen)} id="chat-toggle-btn" aria-label="Open AI Assistant">
        {isOpen ? '✕' : '🤖'}
      </button>
    </div>
  )
}
