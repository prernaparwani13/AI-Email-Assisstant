import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowLeft, Trash2, Reply, Forward, Star, MoreHorizontal,
  Sparkles, FileText, CheckCircle, Tag, Loader2, Copy, Check,
  Send, ChevronDown, SpellCheck,
} from 'lucide-react'
import { emailApi, aiApi } from '../lib/api'
import { useAuth } from '../contexts/AuthContext'
import UserMenu from '../components/UserMenu'

const TONES = ['professional', 'friendly', 'formal', 'concise', 'empathetic']

function CategoryBadge({ category }) {
  const map = {
    Work: 'badge-work', Personal: 'badge-personal', Finance: 'badge-finance',
    Newsletter: 'badge-newsletter', Promotions: 'badge-promotions',
    Social: 'badge-social', Spam: 'badge-spam', Updates: 'badge-updates',
    Support: 'badge-work', Travel: 'badge-personal',
  }
  return <span className={map[category] || 'badge-updates'}>{category}</span>
}

function AiButton({ label, icon: Icon, onClick, loading, active }) {
  return (
    <button
      onClick={onClick}
      disabled={loading}
      className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 
        ${active
          ? 'bg-primary-600/20 text-primary-300 border border-primary-600/30'
          : 'bg-dark-800 text-dark-300 border border-dark-700 hover:border-primary-700/40 hover:text-primary-300'
        } disabled:opacity-50`}
    >
      {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Icon className="w-3.5 h-3.5" />}
      {label}
    </button>
  )
}

export default function EmailDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  const [email, setEmail] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // AI states
  const [aiMode, setAiMode] = useState(null) // 'reply' | 'summary' | 'classify'
  const [aiResult, setAiResult] = useState('')
  const [aiLoading, setAiLoading] = useState(false)
  const [tone, setTone] = useState('professional')
  const [copied, setCopied] = useState(false)
  const [showToneMenu, setShowToneMenu] = useState(false)

  // Reply compose
  const [replyText, setReplyText] = useState('')
  const [sending, setSending] = useState(false)
  const [sent, setSent] = useState(false)
  const [grammarLoading, setGrammarLoading] = useState(false)
  const [grammarFixed, setGrammarFixed] = useState(false)

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await emailApi.getEmail(id)
        setEmail(res.data)
      } catch {
        setError('Failed to load email.')
      } finally {
        setLoading(false)
      }
    }
    fetch()
  }, [id])

  const runAI = async (mode) => {
    if (!email) return
    setAiMode(mode)
    setAiResult('')
    setAiLoading(true)
    try {
      let res
      if (mode === 'reply') {
        res = await aiApi.generateReply({ email_body: email.body || email.snippet, email_subject: email.subject, tone })
        setReplyText(res.data.result)
      } else if (mode === 'summary') {
        res = await aiApi.summarize({ email_body: email.body || email.snippet, email_subject: email.subject })
      } else if (mode === 'classify') {
        res = await aiApi.classify({ email_body: email.body || email.snippet, email_subject: email.subject, sender: email.sender })
      }
      setAiResult(res.data.result)
    } catch {
      setAiResult('AI request failed. Please try again.')
    } finally {
      setAiLoading(false)
    }
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(aiResult)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleSendReply = async () => {
    if (!replyText.trim() || !email) return
    setSending(true)
    try {
      await emailApi.sendEmail({
        to: email.sender,
        subject: `Re: ${email.subject}`,
        body: replyText,
      })
      setSent(true)
      setTimeout(() => setSent(false), 3000)
    } catch {
      alert('Failed to send reply.')
    } finally {
      setSending(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm('Move this email to trash?')) return
    await emailApi.deleteEmail(id)
    navigate('/dashboard')
  }

  const handleGrammarCheck = async () => {
    if (!replyText.trim()) return
    setGrammarLoading(true)
    try {
      const res = await aiApi.correctGrammar({ text: replyText })
      setReplyText(res.data.result)
      setGrammarFixed(true)
      setTimeout(() => setGrammarFixed(false), 2500)
    } catch {
      // silent fail — leave text as-is
    } finally {
      setGrammarLoading(false)
    }
  }

  if (loading) return (
    <div className="min-h-screen bg-dark-950 flex items-center justify-center">
      <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
    </div>
  )

  if (error || !email) return (
    <div className="min-h-screen bg-dark-950 flex items-center justify-center">
      <div className="text-center space-y-4">
        <p className="text-dark-400">{error || 'Email not found'}</p>
        <button onClick={() => navigate('/dashboard')} className="btn-primary">Back to inbox</button>
      </div>
    </div>
  )

  const initials = (email.sender_name || email.sender || '?').charAt(0).toUpperCase()

  return (
    <div className="min-h-screen bg-dark-950 bg-mesh">
      {/* Header */}
      <header className="sticky top-0 z-10 flex items-center gap-3 px-6 py-4 border-b border-dark-800 bg-dark-950/80 backdrop-blur">
        <button onClick={() => navigate('/dashboard')} className="btn-ghost p-2" id="back-btn">
          <ArrowLeft className="w-5 h-5" />
        </button>
        <h1 className="text-dark-200 font-medium text-sm truncate flex-1">{email.subject}</h1>
        <div className="flex items-center gap-2">
          <button onClick={handleDelete} className="btn-ghost p-2 text-red-400 hover:text-red-300" title="Delete">
            <Trash2 className="w-4 h-4" />
          </button>
          <UserMenu user={user} onLogout={logout} />
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 py-6 space-y-6">
        {/* Email card */}
        <div className="card space-y-5 animate-fade-in">
          {/* Subject + meta */}
          <div className="space-y-3">
            <h2 className="text-xl font-bold text-white">{email.subject || 'No Subject'}</h2>
            <div className="flex items-start justify-between gap-4 flex-wrap">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-600 to-purple-700 flex items-center justify-center text-white font-bold text-sm shrink-0">
                  {initials}
                </div>
                <div>
                  <p className="text-dark-100 font-medium text-sm">{email.sender_name || email.sender}</p>
                  <p className="text-dark-500 text-xs">{email.sender}</p>
                  {email.recipient && <p className="text-dark-600 text-xs">To: {email.recipient}</p>}
                </div>
              </div>
              <div className="text-right space-y-1">
                <p className="text-dark-500 text-xs">{email.date}</p>
                {email.ai_category && <CategoryBadge category={email.ai_category} />}
              </div>
            </div>
          </div>

          {/* AI toolbar */}
          <div className="flex flex-wrap items-center gap-2 p-3 bg-dark-800/40 rounded-xl border border-dark-700/50">
            <span className="text-dark-500 text-xs font-medium mr-1">AI Tools:</span>
            <AiButton label="Generate Reply" icon={Reply} onClick={() => runAI('reply')} loading={aiLoading && aiMode === 'reply'} active={aiMode === 'reply'} />
            <AiButton label="Summarize" icon={FileText} onClick={() => runAI('summary')} loading={aiLoading && aiMode === 'summary'} active={aiMode === 'summary'} />
            <AiButton label="Classify" icon={Tag} onClick={() => runAI('classify')} loading={aiLoading && aiMode === 'classify'} active={aiMode === 'classify'} />

            {/* Tone selector */}
            <div className="relative ml-auto">
              <button
                onClick={() => setShowToneMenu(!showToneMenu)}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-dark-800 text-dark-300 border border-dark-700 rounded-lg text-xs hover:border-dark-600 transition-colors"
              >
                Tone: <span className="text-dark-100 capitalize">{tone}</span>
                <ChevronDown className="w-3 h-3" />
              </button>
              {showToneMenu && (
                <div className="absolute right-0 top-full mt-1 bg-dark-800 border border-dark-700 rounded-lg overflow-hidden z-20 shadow-xl">
                  {TONES.map(t => (
                    <button key={t} onClick={() => { setTone(t); setShowToneMenu(false) }}
                      className={`block w-full text-left px-4 py-2 text-xs capitalize hover:bg-dark-700 transition-colors
                        ${tone === t ? 'text-primary-400' : 'text-dark-300'}`}>
                      {t}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* AI Result */}
          {(aiResult || (aiLoading && aiMode)) && (
            <div className="ai-response-box animate-slide-up space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-primary-400 text-xs font-semibold">
                  <Sparkles className="w-3.5 h-3.5" />
                  {aiMode === 'reply' ? 'AI-Generated Reply' : aiMode === 'summary' ? 'Email Summary' : 'Email Category'}
                </div>
                {aiResult && (
                  <button onClick={handleCopy} className="flex items-center gap-1 text-dark-400 hover:text-dark-200 text-xs transition-colors">
                    {copied ? <Check className="w-3.5 h-3.5 text-green-400" /> : <Copy className="w-3.5 h-3.5" />}
                    {copied ? 'Copied!' : 'Copy'}
                  </button>
                )}
              </div>
              {aiLoading ? (
                <div className="flex items-center gap-2 text-dark-400 text-sm py-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Generating with Gemini…
                </div>
              ) : (
                <pre className="text-dark-200 text-sm whitespace-pre-wrap font-sans leading-relaxed">{aiResult}</pre>
              )}
            </div>
          )}

          {/* Email body */}
          <div className="border-t border-dark-800 pt-5">
            <div className="text-dark-300 text-sm leading-relaxed whitespace-pre-wrap font-sans">
              {email.body || email.snippet || 'No content available.'}
            </div>
          </div>
        </div>

        {/* Reply compose box */}
        <div className="card space-y-4 animate-slide-up">
          <div className="flex items-center gap-2">
            <Reply className="w-4 h-4 text-primary-400" />
            <h3 className="text-dark-200 font-medium text-sm">Reply</h3>
            {aiMode === 'reply' && replyText && (
              <span className="text-xs text-primary-400 bg-primary-900/30 px-2 py-0.5 rounded-full">AI draft ready</span>
            )}
          </div>
          <textarea
            id="reply-textarea"
            value={replyText}
            onChange={(e) => setReplyText(e.target.value)}
            placeholder={`Reply to ${email.sender_name || email.sender}…`}
            rows={6}
            className="input-field resize-none text-sm font-sans"
          />
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <p className="text-dark-600 text-xs">To: {email.sender}</p>
              <button
                onClick={handleGrammarCheck}
                disabled={grammarLoading || !replyText.trim()}
                className="flex items-center gap-1.5 text-xs text-dark-400 hover:text-primary-300 transition-colors disabled:opacity-40"
              >
                {grammarLoading
                  ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  : <SpellCheck className="w-3.5 h-3.5" />}
                Fix Grammar
              </button>
              {grammarFixed && (
                <span className="flex items-center gap-1 text-green-400 text-xs animate-fade-in">
                  <CheckCircle className="w-3.5 h-3.5" /> Grammar fixed!
                </span>
              )}
            </div>
            <div className="flex items-center gap-2">
              {sent && (
                <span className="flex items-center gap-1 text-green-400 text-xs">
                  <CheckCircle className="w-3.5 h-3.5" /> Sent!
                </span>
              )}
              <button
                id="send-reply-btn"
                onClick={handleSendReply}
                disabled={sending || !replyText.trim()}
                className="btn-primary text-sm"
              >
                {sending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                {sending ? 'Sending…' : 'Send Reply'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
