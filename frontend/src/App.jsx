import { useState, useRef, useEffect } from "react"
import axios from "axios"

const SOURCE_LABELS = {
  "readme.md": "README",
  "api_spec.md": "API Reference",
  "explainer.md": "How It Works"
}

function SourceBadge({ source }) {
  const colors = {
    "readme.md": "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
    "api_spec.md": "bg-purple-500/10 text-purple-400 border-purple-500/20",
    "explainer.md": "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
  }
  return (
    <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border uppercase tracking-wider ${colors[source] || "bg-gray-500/10 text-gray-400 border-gray-500/20"}`}>
      {SOURCE_LABELS[source] || source}
    </span>
  )
}

function Message({ msg }) {
  if (msg.role === "user") {
    return (
      <div className="flex justify-end mb-6">
        <div className="bg-cyan-500/10 border border-cyan-500/20 rounded-xl px-4 py-3 max-w-lg">
          <p className="text-cyan-100 text-sm">{msg.content}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex justify-start mb-6">
      <div className="max-w-2xl w-full">
        <div className="bg-gray-900/80 border border-gray-700/50 rounded-xl px-5 py-4">
          {msg.loading ? (
            <div className="flex items-center gap-2">
              <div className="flex gap-1">
                <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
              <span className="text-gray-500 font-mono text-xs">Searching docs...</span>
            </div>
          ) : (
            <>
              <p className="text-gray-100 text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
              {msg.sources && msg.sources.length > 0 && (
                <div className="flex items-center gap-2 mt-3 pt-3 border-t border-gray-700/50 flex-wrap">
                  <span className="text-gray-500 font-mono text-[10px] uppercase tracking-wider">Sources:</span>
                  {msg.sources.map(s => <SourceBadge key={s} source={s} />)}
                  <span className="text-gray-600 font-mono text-[10px]">{msg.chunk_count} chunks</span>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

const SUGGESTED_QUESTIONS = [
  "What is a BREAKOUT signal?",
  "How do I open a position?",
  "What credit bundles are available?",
  "How is P&L calculated?",
  "What does the leaderboard endpoint return?",
  "How does the momentum acceleration work?"
]

export default function App() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Hey — I'm the UMExchange docs assistant. Ask me anything about how the platform works, the API endpoints, signals, investing mechanics, or the tech stack.",
      sources: [],
      chunk_count: 0
    }
  ])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const handleAsk = async (question) => {
    const q = question || input.trim()
    if (!q || loading) return

    setInput("")
    setMessages(prev => [
      ...prev,
      { role: "user", content: q },
      { role: "assistant", content: "", loading: true }
    ])
    setLoading(true)

    try {
      const res = await axios.post(`${import.meta.env.VITE_API_URL}/ask`, {
        question: q
      })
      setMessages(prev => [
        ...prev.slice(0, -1),
        {
          role: "assistant",
          content: res.data.answer,
          sources: res.data.sources,
          chunk_count: res.data.chunk_count
        }
      ])
    } catch {
      setMessages(prev => [
        ...prev.slice(0, -1),
        {
          role: "assistant",
          content: "Something went wrong. Make sure the API is running.",
          sources: [],
          chunk_count: 0
        }
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleAsk()
    }
  }

  const showSuggestions = messages.length === 1

  return (
    <div className="min-h-screen bg-gray-950 flex flex-col relative">
      {/* Grid background */}
      <div className="fixed inset-0 grid-bg pointer-events-none" />
      <div className="fixed inset-0 pointer-events-none" style={{
        background: "radial-gradient(ellipse 80% 50% at 50% 0%, rgba(76, 215, 246, 0.04) 0%, transparent 70%)"
      }} />

      {/* Header */}
      <header className="relative z-10 border-b border-gray-800/50 bg-gray-950/80 backdrop-blur-xl px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
            <span className="material-symbols-outlined text-cyan-400 text-[16px]">auto_awesome</span>
          </div>
          <div>
            <h1 className="text-white font-bold text-sm leading-none">UMExchange Assistant</h1>
            <p className="text-gray-500 font-mono text-[10px] mt-0.5 uppercase tracking-widest">Docs AI</p>
          </div>
        </div>
        <a
          href="https://music-stock-exchange.netlify.app"
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-1.5 text-gray-500 hover:text-cyan-400 font-mono text-xs transition-colors"
        >
          Open UMExchange
          <span className="material-symbols-outlined text-[14px]">open_in_new</span>
        </a>
      </header>

      {/* Messages */}
      <main className="relative z-10 flex-1 overflow-y-auto px-4 py-6 max-w-3xl mx-auto w-full">
        {messages.map((msg, i) => (
          <Message key={i} msg={msg} />
        ))}

        {/* Suggested questions */}
        {showSuggestions && (
          <div className="mt-4">
            <p className="text-gray-600 font-mono text-[11px] uppercase tracking-widest mb-3">Suggested questions</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {SUGGESTED_QUESTIONS.map(q => (
                <button
                  key={q}
                  onClick={() => handleAsk(q)}
                  className="text-left px-4 py-3 bg-gray-900/60 border border-gray-700/50 rounded-lg text-gray-400 text-xs font-mono hover:border-cyan-500/30 hover:text-cyan-300 transition-all"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </main>

      {/* Input */}
      <div className="relative z-10 border-t border-gray-800/50 bg-gray-950/80 backdrop-blur-xl px-4 py-4">
        <div className="max-w-3xl mx-auto flex gap-3">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything about UMExchange..."
            disabled={loading}
            className="flex-1 bg-gray-900 border border-gray-700/50 rounded-xl px-4 py-3 text-sm text-gray-100 font-mono focus:outline-none focus:ring-1 focus:ring-cyan-500/50 placeholder:text-gray-600 disabled:opacity-50"
          />
          <button
            onClick={() => handleAsk()}
            disabled={loading || !input.trim()}
            className="bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 px-4 py-3 rounded-xl hover:bg-cyan-500/20 transition-all disabled:opacity-30 disabled:cursor-not-allowed"
          >
            <span className="material-symbols-outlined text-[20px]">send</span>
          </button>
        </div>
        <p className="text-center text-gray-700 font-mono text-[10px] mt-2">
          Answers grounded in UMExchange documentation · Powered by GPT-4o-mini
        </p>
      </div>
    </div>
  )
}