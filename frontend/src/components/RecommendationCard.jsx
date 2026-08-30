import { Link } from 'react-router-dom'
import { useState } from 'react'

const labels = { 
  ELIGIBLE: 'Eligible', 
  POTENTIALLY_ELIGIBLE: 'Potentially Eligible', 
  INSUFFICIENT_INFORMATION: 'More Information Needed', 
  NOT_ELIGIBLE: 'Not Eligible',
  CONFLICT: 'Eligibility Conflict'
}

const unavailable = 'Official source information is not available in the current knowledge base.'

function CollapsibleSection({ title, content }) {
  const [open, setOpen] = useState(false);
  if (!content || content === unavailable) {
    return (
      <div className="mt-3">
        <h4 className="font-bold text-govnavy">{title}</h4>
        <p className="text-sm text-slate-500 mt-1">{unavailable}</p>
      </div>
    );
  }
  return (
    <div className="mt-3 border border-slate-200 rounded">
      <button 
        type="button" 
        onClick={() => setOpen(!open)}
        className="w-full text-left px-4 py-2 bg-slate-50 hover:bg-slate-100 font-bold text-govnavy flex justify-between items-center"
      >
        {title}
        <span className="text-xl leading-none">{open ? '−' : '+'}</span>
      </button>
      {open && <div className="p-4 text-sm text-slate-700 bg-white whitespace-pre-line leading-relaxed">{content}</div>}
    </div>
  )
}

export default function RecommendationCard({ scheme }) { 
  const status = scheme.eligibility_status; 
  
  return (
    <article className="card flex flex-col h-full border-t-4 border-t-govnavy" aria-label={scheme.scheme_name}>
      
      <div className="mb-4">
        <h3 className="text-xl font-bold text-govnavy leading-tight mt-0 mb-1">{scheme.scheme_name}</h3>
        <p className="text-sm text-slate-600 font-semibold uppercase tracking-wider">
          {scheme.level || 'Unknown Level'} • {scheme.category || 'Uncategorized'}
        </p>
      </div>
      
      <div className="grid md:grid-cols-2 gap-4 mb-5 p-4 bg-slate-50 border border-slate-200 rounded">
        <div>
          <span className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Match Relevance</span>
          <p className="text-sm text-slate-800">
            <strong>Why this scheme was retrieved:</strong><br/>
            This scheme is semantically relevant to your stated needs.
          </p>
        </div>
        <div className="md:border-l md:border-slate-300 md:pl-4">
          <span className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Eligibility Status</span>
          <span className={`badge badge-${status} inline-block mb-1`}>{labels[status] || status}</span>
          <p className="text-sm text-slate-800 mt-1">
            <strong>What your profile indicates:</strong><br/>
            {scheme.why_recommended || unavailable}
          </p>
        </div>
      </div>

      <div className="flex-1 space-y-1 mb-6">
        <CollapsibleSection title="Description & Benefits" content={scheme.description ? `${scheme.description}\n\nBenefits:\n${scheme.benefits || 'Not specified'}` : unavailable} />
        <CollapsibleSection title="Eligibility Requirements" content={scheme.eligibility} />
        <CollapsibleSection title="Application Process & Documents" content={scheme.application ? `${scheme.application}\n\nRequired Documents:\n${scheme.documents || 'Not specified'}` : unavailable} />
      </div>
      
      <div className="mt-auto pt-4 border-t border-slate-200 flex flex-wrap items-center justify-between gap-4">
        <Link className="button-secondary text-sm" to={`/scheme/${encodeURIComponent(scheme.scheme_id)}`} state={{ scheme }}>
          View Full Details
        </Link>
        {scheme.source_url ? (
          <a className="button-primary text-sm" href={scheme.source_url} target="_blank" rel="noreferrer">
            Official Source ↗
          </a>
        ) : (
          <span className="text-xs text-slate-500 max-w-[200px] text-right">Official source link not available</span>
        )}
      </div>
      
    </article>
  ) 
}
