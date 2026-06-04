const CATEGORY_COLORS = {
  Work: 'text-blue-400 bg-blue-900/30',
  Personal: 'text-green-400 bg-green-900/30',
  Finance: 'text-yellow-400 bg-yellow-900/30',
  Newsletter: 'text-purple-400 bg-purple-900/30',
  Promotions: 'text-orange-400 bg-orange-900/30',
  Social: 'text-pink-400 bg-pink-900/30',
  Spam: 'text-red-400 bg-red-900/30',
  Updates: 'text-dark-400 bg-dark-800',
  Support: 'text-cyan-400 bg-cyan-900/30',
  Travel: 'text-teal-400 bg-teal-900/30',
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  try {
    const d = new Date(dateStr)
    const now = new Date()
    const isToday = d.toDateString() === now.toDateString()
    if (isToday) return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    const diffDays = Math.floor((now - d) / 86400000)
    if (diffDays < 7) return d.toLocaleDateString([], { weekday: 'short' })
    return d.toLocaleDateString([], { month: 'short', day: 'numeric' })
  } catch { return '' }
}

function Avatar({ name, email }) {
  const letter = (name || email || '?').charAt(0).toUpperCase()
  const colors = [
    'from-blue-600 to-blue-800', 'from-purple-600 to-purple-800',
    'from-pink-600 to-pink-800', 'from-green-600 to-green-800',
    'from-orange-600 to-orange-800', 'from-cyan-600 to-cyan-800',
  ]
  const colorIndex = (name || email || '').charCodeAt(0) % colors.length
  return (
    <div className={`w-9 h-9 rounded-full bg-gradient-to-br ${colors[colorIndex]} flex items-center justify-center text-white font-semibold text-sm shrink-0`}>
      {letter}
    </div>
  )
}

export default function EmailCard({ email, onClick }) {
  const isUnread = !email.is_read

  return (
    <div
      id={`email-${email.id}`}
      onClick={onClick}
      className={`email-row animate-fade-in ${isUnread ? 'unread' : ''}`}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick()}
    >
      {/* Unread indicator */}
      <div className={`w-1.5 h-1.5 rounded-full mt-4 shrink-0 ${isUnread ? 'bg-primary-500' : 'bg-transparent'}`} />

      <Avatar name={email.sender_name} email={email.sender} />

      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2 mb-0.5">
          <span className={`text-sm truncate ${isUnread ? 'font-semibold text-dark-100' : 'font-normal text-dark-300'}`}>
            {email.sender_name || email.sender || 'Unknown'}
          </span>
          <span className="text-xs text-dark-600 shrink-0">{formatDate(email.date)}</span>
        </div>

        <div className="flex items-start gap-2">
          <div className="flex-1 min-w-0">
            <p className={`text-sm truncate mb-0.5 ${isUnread ? 'text-dark-200 font-medium' : 'text-dark-400'}`}>
              {email.subject || 'No Subject'}
            </p>
            <p className="text-xs text-dark-600 truncate leading-relaxed">
              {email.snippet || 'No preview available'}
            </p>
          </div>
          {email.ai_category && (
            <span className={`shrink-0 text-xs px-1.5 py-0.5 rounded-md font-medium ${CATEGORY_COLORS[email.ai_category] || CATEGORY_COLORS.Updates}`}>
              {email.ai_category}
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
