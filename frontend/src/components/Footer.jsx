import React from 'react';
import { Bot, ShieldCheck, Heart, ExternalLink } from 'lucide-react';

export function Footer() {
  return (
    <footer className="glass-panel border-t border-gray-800 mt-16 px-6 py-10">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8">
        <div className="space-y-3 md:col-span-1">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg gradient-bg-primary flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <span className="font-extrabold text-lg gradient-text-primary">GovAssist AI</span>
          </div>
          <p className="text-xs text-gray-400 leading-relaxed">
            Commercial Multi-Agent RAG Framework for Intelligent Indian Government Scheme Recommendation & Document Grounding.
          </p>
          <div className="flex items-center gap-2 text-xs text-emerald-400 font-semibold bg-emerald-500/10 border border-emerald-500/20 px-3 py-1.5 rounded-xl w-fit">
            <ShieldCheck className="w-4 h-4" />
            <span>Document Grounded & Verified</span>
          </div>
        </div>

        <div>
          <h4 className="text-sm font-bold text-gray-200 mb-3 uppercase tracking-wider">Navigation</h4>
          <ul className="space-y-2 text-xs text-gray-400">
            <li><a href="/" className="hover:text-indigo-400 transition-colors">Home Landing</a></li>
            <li><a href="/assistant" className="hover:text-indigo-400 transition-colors">AI Scheme Assistant</a></li>
            <li><a href="/schemes" className="hover:text-indigo-400 transition-colors">Search & Filter Directory</a></li>
            <li><a href="/dashboard" className="hover:text-indigo-400 transition-colors">Citizen Dashboard</a></li>
          </ul>
        </div>

        <div>
          <h4 className="text-sm font-bold text-gray-200 mb-3 uppercase tracking-wider">Official Portals</h4>
          <ul className="space-y-2 text-xs text-gray-400">
            <li>
              <a href="https://www.myscheme.gov.in" target="_blank" rel="noreferrer" className="flex items-center gap-1 hover:text-indigo-400 transition-colors">
                myScheme Portal <ExternalLink className="w-3 h-3" />
              </a>
            </li>
            <li>
              <a href="https://scholarships.gov.in" target="_blank" rel="noreferrer" className="flex items-center gap-1 hover:text-indigo-400 transition-colors">
                National Scholarship Portal <ExternalLink className="w-3 h-3" />
              </a>
            </li>
            <li>
              <a href="https://pmkisan.gov.in" target="_blank" rel="noreferrer" className="flex items-center gap-1 hover:text-indigo-400 transition-colors">
                PM-KISAN Official Portal <ExternalLink className="w-3 h-3" />
              </a>
            </li>
          </ul>
        </div>

        <div>
          <h4 className="text-sm font-bold text-gray-200 mb-3 uppercase tracking-wider">Framework Tech Stack</h4>
          <p className="text-xs text-gray-400 leading-relaxed mb-3">
            FastAPI • PyMongo • FAISS IndexFlatIP • BAAI/bge-small-en-v1.5 • LangGraph StateGraph (9-Agents) • React Vite
          </p>
          <p className="text-[11px] text-gray-500">
            © 2026 GovAssist AI Framework. Built with <Heart className="w-3 h-3 inline text-red-500" /> for Indian Citizens.
          </p>
        </div>
      </div>
    </footer>
  );
}
