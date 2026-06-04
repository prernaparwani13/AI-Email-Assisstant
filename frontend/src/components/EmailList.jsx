import EmailCard from './EmailCard'
import { Inbox, RefreshCw } from 'lucide-react'

function SkeletonRow() {
  return (
    <div className="flex items-start gap-3 px-4 py-3 border-b border-dark-800/50">
      <div className="w-9 h-9 rounded-full shimmer-bg shrink-0 mt-0.5" />
      <div className="flex-1 space-y-2">
        <div className="flex items-center gap-2">
          <div className="h-3.5 w-32 shimmer-bg rounded" />
          <div className="h-3 w-20 shimmer-bg rounded ml-auto" />
        </div>
        <div className="h-3.5 w-56 shimmer-bg rounded" />
        <div className="h-3 w-full shimmer-bg rounded" />
      </div>
    </div>
  )
}

export default function EmailList({ emails, loading, error, onEmailClick, onRefresh }) {
  if (loading) {
    return (
      <div className="divide-y divide-dark-800/30">
        {Array.from({ length: 8 }).map((_, i) => <SkeletonRow key={i} />)}
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-24 gap-4">
        <div className="w-12 h-12 rounded-full bg-red-900/20 flex items-center justify-center">
          <RefreshCw className="w-5 h-5 text-red-400" />
        </div>
        <p className="text-dark-400 text-sm">{error}</p>
        <button onClick={onRefresh} className="btn-secondary text-sm">Try Again</button>
      </div>
    )
  }

  if (!emails || emails.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-24 gap-4">
        <div className="w-16 h-16 rounded-full bg-dark-800/50 flex items-center justify-center">
          <Inbox className="w-7 h-7 text-dark-600" />
        </div>
        <div className="text-center">
          <p className="text-dark-300 font-medium">No emails found</p>
          <p className="text-dark-600 text-sm mt-1">Your inbox is empty or no results match.</p>
        </div>
        <button onClick={onRefresh} className="btn-ghost text-sm">
          <RefreshCw className="w-4 h-4" /> Refresh
        </button>
      </div>
    )
  }

  return (
    <div className="divide-y divide-dark-800/30">
      {emails.map(email => (
        <EmailCard key={email.id} email={email} onClick={() => onEmailClick(email.id)} />
      ))}
    </div>
  )
}
