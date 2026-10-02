import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';

export default function ChatPage() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I am GovAssist AI. How can I help you find government schemes today?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(Math.random().toString(36).substring(7));
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleNewChat = () => {
    setSessionId(Math.random().toString(36).substring(7));
    setMessages([
      { role: 'assistant', content: 'Hello! I am GovAssist AI. How can I help you find government schemes today?' }
    ]);
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // In production, fetch profile from context or backend
      const response = await fetch('/api/v1/agent/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          session_id: sessionId,
          query: userMessage.content,
          user_profile: {} // To be wired to global state
        })
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      setMessages(prev => [...prev, { role: 'assistant', content: '' }]);
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.slice(6);
            if (dataStr === '[DONE]') break;
            
            try {
              const data = JSON.parse(dataStr);
              setMessages(prev => {
                const newMessages = [...prev];
                const lastIdx = newMessages.length - 1;
                newMessages[lastIdx] = {
                  ...newMessages[lastIdx],
                  content: newMessages[lastIdx].content + (data.content || '')
                };
                return newMessages;
              });
            } catch (err) {
              console.error('Error parsing SSE json:', err);
            }
          }
        }
      }
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: '**Error:** Failed to connect to the agent framework.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto w-full">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Chat with GovAssist</h2>
        <button 
          onClick={handleNewChat}
          className="px-4 py-2 bg-slate-800 text-sm rounded-lg hover:bg-slate-700 transition"
        >
          New Conversation
        </button>
      </div>
      <div className="flex-1 overflow-y-auto space-y-6 pb-4">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex gap-4 ${msg.role === 'assistant' ? '' : 'flex-row-reverse'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
              msg.role === 'assistant' ? 'bg-primary text-white' : 'bg-surface border border-slate-700 text-slate-300'
            }`}>
              {msg.role === 'assistant' ? <Bot size={18} /> : <User size={18} />}
            </div>
            <div className={`max-w-[80%] rounded-2xl p-4 ${
              msg.role === 'assistant' 
                ? 'bg-surface border border-slate-700/50 text-slate-200' 
                : 'bg-primary text-white'
            }`}>
              <ReactMarkdown className="prose prose-invert max-w-none text-sm">
                {msg.content}
              </ReactMarkdown>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex gap-4">
            <div className="w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center shrink-0">
              <Bot size={18} />
            </div>
            <div className="bg-surface border border-slate-700/50 rounded-2xl p-4 flex items-center gap-2 text-slate-400 text-sm">
              <Loader2 size={16} className="animate-spin" /> Analyzing profile and schemes...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="mt-4 pt-4 border-t border-slate-700/50">
        <form onSubmit={handleSend} className="relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            placeholder="Ask about government schemes..."
            className="w-full bg-surface border border-slate-700 rounded-xl pl-4 pr-12 py-4 text-white focus:outline-none focus:border-primary transition-colors disabled:opacity-50"
          />
          <button 
            type="submit" 
            disabled={loading || !input.trim()}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-primary text-white rounded-lg hover:bg-primary/90 disabled:opacity-50 transition-colors"
          >
            <Send size={18} />
          </button>
        </form>
        <p className="text-center text-xs text-muted mt-2">
          GovAssist AI uses advanced RAG technology. Responses are grounded in official documents.
        </p>
      </div>
    </div>
  );
}
