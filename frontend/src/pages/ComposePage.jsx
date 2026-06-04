import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  ArrowLeft, Send, Sparkles, Loader2, CheckCircle,
  SpellCheck, ChevronDown, PenSquare,
} from 'lucide-react'
import { emailApi, aiApi } from '../lib/api'
import { useAuth } from '../contexts/AuthContext'
import UserMenu from '../components/UserMenu'

const TONES = ['professional', 'friendly', 'formal', 'concise', 'empathetic']

export default function ComposePage() {
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const [form, setForm] = useState({ to: '', subject: '', body: '', cc: '', bcc: '' })
  const [sending, setSending] = useState(false)
  const [sent, setSent] = useState(false)
  const [error, setError] = useState('')
  const [aiPrompt, setAiPrompt] = useState('')
  const [tone, setTone] = useState('professional')
  const [aiLoading, setAiLoading] = useState(false)
  const [grammarLoading, setGrammarLoading] = useState(false)
  const [grammarFixed, setGrammarFixed] = useState(false)
  const [showToneMenu, setShowToneMenu] = useState(false)
  const [showCc, setShowCc] = useState(false)

  const update = (field) => (e) => setForm(prev => ({ ...prev, [field]: e.target.value }))

  const handleSend = async () => {
    if (!form.to || !form.subject || !form.body) { setError('To, Subject, and Body are required.'); return }
    setSending(true); setError('')
    try {
      await emailApi.sendEmail(form)
      setSent(true)
      setTimeout(() => navigate('/dashboard'), 2000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to send email.')
    } finally { setSending(false) }
  }

  const handleAiCompose = async () => {
    if (!aiPrompt.trim()) return
    setAiLoading(true)
    try {
      const res = await aiApi.compose(aiPrompt, tone)
      let text = res.data.result
      // Safety-net: replace any residual [Your Name] placeholders with the real user name
      if (user?.name) {
        text = text.replace(/\[Your Name\]/g, user.name)
      }
      const subjectMatch = text.match(/^Subject:\s*(.+)$/m)
      if (subjectMatch) {
        setForm(prev => ({ ...prev, subject: subjectMatch[1].trim(), body: text.replace(/^Subject:.*\n?/m, '').trim() }))
      } else {
        setForm(prev => ({ ...prev, body: text }))
      }
    } catch { setError('AI compose failed.') }
    finally { setAiLoading(false) }
  }

  const handleGrammarCheck = async () => {
    if (!form.body.trim()) return
    setGrammarLoading(true)
    try {
      const res = await aiApi.correctGrammar({ text: form.body })
      setForm(prev => ({ ...prev, body: res.data.result }))
      setGrammarFixed(true)
      setTimeout(() => setGrammarFixed(false), 2500)
    } catch { setError('Grammar correction failed.') }
    finally { setGrammarLoading(false) }
  }

  return (
    <div className="min-h-screen bg-dark-950 bg-mesh">
      <header className="sticky top-0 z-10 flex items-center gap-3 px-6 py-4 border-b border-dark-800 bg-dark-950/80 backdrop-blur">
        <button onClick={() => navigate('/dashboard')} className="btn-ghost p-2"><ArrowLeft className="w-5 h-5" /></button>
        <div className="flex items-center gap-2">
          <PenSquare className="w-5 h-5 text-primary-400" />
          <h1 className="text-white font-semibold">New Message</h1>
        </div>
        <div className="ml-auto flex items-center gap-2">
          {sent && <span className="flex items-center gap-1 text-green-400 text-sm"><CheckCircle className="w-4 h-4" /> Sent!</span>}
          <button id="send-email-btn" onClick={handleSend} disabled={sending || sent} className="btn-primary">
            {sending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            {sending ? 'Sending…' : sent ? 'Sent!' : 'Send'}
          </button>
          <UserMenu user={user} onLogout={logout} />
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 py-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <div className="card space-y-0 p-0 overflow-hidden">
            <div className="flex items-center border-b border-dark-800">
              <label className="text-dark-500 text-sm px-4 py-3 w-16 shrink-0">To</label>
              <input id="compose-to" type="email" value={form.to} onChange={update('to')} placeholder="recipient@example.com"
                className="flex-1 bg-transparent px-2 py-3 text-sm text-dark-100 placeholder-dark-600 focus:outline-none" />
              <button onClick={() => setShowCc(!showCc)} className="px-4 text-dark-500 hover:text-dark-300 text-xs">{showCc ? 'Hide' : 'Cc/Bcc'}</button>
            </div>
            {showCc && <>
              <div className="flex items-center border-b border-dark-800">
                <label className="text-dark-500 text-sm px-4 py-3 w-16 shrink-0">Cc</label>
                <input id="compose-cc" type="text" value={form.cc} onChange={update('cc')} placeholder="cc@example.com"
                  className="flex-1 bg-transparent px-2 py-3 text-sm text-dark-100 placeholder-dark-600 focus:outline-none" />
              </div>
              <div className="flex items-center border-b border-dark-800">
                <label className="text-dark-500 text-sm px-4 py-3 w-16 shrink-0">Bcc</label>
                <input id="compose-bcc" type="text" value={form.bcc} onChange={update('bcc')} placeholder="bcc@example.com"
                  className="flex-1 bg-transparent px-2 py-3 text-sm text-dark-100 placeholder-dark-600 focus:outline-none" />
              </div>
            </>}
            <div className="flex items-center border-b border-dark-800">
              <label className="text-dark-500 text-sm px-4 py-3 w-16 shrink-0">Subject</label>
              <input id="compose-subject" type="text" value={form.subject} onChange={update('subject')} placeholder="Email subject"
                className="flex-1 bg-transparent px-2 py-3 text-sm text-dark-100 placeholder-dark-600 focus:outline-none font-medium" />
            </div>
            <textarea id="compose-body" value={form.body} onChange={update('body')}
              placeholder="Write your message here…" rows={16}
              className="w-full bg-transparent px-4 py-4 text-sm text-dark-200 placeholder-dark-600 focus:outline-none resize-none font-sans leading-relaxed" />
            <div className="flex items-center gap-3 px-4 py-3 border-t border-dark-800 bg-dark-900/30">
              <button id="grammar-check-btn" onClick={handleGrammarCheck} disabled={grammarLoading || !form.body}
                className="flex items-center gap-1.5 text-xs text-dark-400 hover:text-primary-300 transition-colors disabled:opacity-40">
                {grammarLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <SpellCheck className="w-3.5 h-3.5" />}
                Fix Grammar
              </button>
              {grammarFixed && (
                <span className="flex items-center gap-1 text-green-400 text-xs animate-fade-in">
                  <CheckCircle className="w-3.5 h-3.5" /> Grammar fixed!
                </span>
              )}
              <span className="text-dark-600 text-xs ml-auto">{form.body.length} chars</span>
            </div>
          </div>
          {error && <p className="text-red-400 text-sm bg-red-900/20 border border-red-800/30 rounded-lg px-4 py-2">{error}</p>}
        </div>

        <div className="space-y-4">
          <div className="card space-y-4">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-primary-400" />
              <h3 className="text-dark-200 font-semibold text-sm">AI Compose</h3>
            </div>
            <p className="text-dark-500 text-xs">Describe your email and Gemini will draft it.</p>
            <textarea id="ai-prompt-input" value={aiPrompt} onChange={(e) => setAiPrompt(e.target.value)}
              placeholder="e.g. Write a follow-up about the project deadline…" rows={4}
              className="input-field resize-none text-sm font-sans" />
            <div className="relative">
              <button onClick={() => setShowToneMenu(!showToneMenu)}
                className="w-full flex items-center justify-between px-3 py-2 bg-dark-800 border border-dark-700 rounded-lg text-sm text-dark-300 hover:border-dark-600 transition-colors">
                <span>Tone: <span className="text-dark-100 capitalize">{tone}</span></span>
                <ChevronDown className="w-4 h-4" />
              </button>
              {showToneMenu && (
                <div className="absolute left-0 right-0 top-full mt-1 bg-dark-800 border border-dark-700 rounded-lg overflow-hidden z-20 shadow-xl">
                  {TONES.map(t => (
                    <button key={t} onClick={() => { setTone(t); setShowToneMenu(false) }}
                      className={`block w-full text-left px-4 py-2.5 text-sm capitalize hover:bg-dark-700 transition-colors ${tone === t ? 'text-primary-400 bg-primary-900/20' : 'text-dark-300'}`}>
                      {t}
                    </button>
                  ))}
                </div>
              )}
            </div>
            <button id="ai-compose-btn" onClick={handleAiCompose} disabled={aiLoading || !aiPrompt.trim()} className="btn-primary w-full text-sm">
              {aiLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
              {aiLoading ? 'Generating…' : 'Generate with AI'}
            </button>
          </div>
          <div className="glass rounded-xl p-4 space-y-2">
            <p className="text-dark-400 text-xs font-medium">💡 Tips</p>
            <ul className="text-dark-600 text-xs space-y-1">
              <li>• Use AI Compose to draft from scratch</li>
              <li>• Fix Grammar corrects typos & tone</li>
              <li>• Cc/Bcc available for group emails</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
