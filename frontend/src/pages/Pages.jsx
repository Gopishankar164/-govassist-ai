import { Link, Navigate, useLocation, useNavigate, useParams } from 'react-router-dom'
import { useEffect, useState, useRef } from 'react'
import { getUserProfile, login, recommend, chatStream, register, saveUserProfile } from '../api/client'
import ReactMarkdown from 'react-markdown'
import RecommendationCard from '../components/RecommendationCard'

export function Landing() { 
  const navigate = useNavigate();
  return (
    <section className="hero bg-govlight py-16 md:py-32 flex flex-col items-center text-center border-b-0 min-h-full">
      <div className="shell max-w-4xl">
        <h1 className="text-5xl md:text-7xl text-govnavy font-bold mt-4 leading-tight tracking-tight">GovAssist AI</h1>
        <p className="lead mt-8 text-2xl text-slate-700">
          Find government schemes based on your age, occupation, location, income and needs.
        </p>
        <div className="mt-12 mb-16">
          <Link className="button-primary text-xl px-12 py-4 shadow-lg hover:shadow-xl transition-shadow rounded-md" to="/assistant">Start Finding Schemes</Link>
        </div>
        
        <div className="mt-12 flex flex-col items-center">
          <p className="text-sm font-semibold text-slate-500 uppercase tracking-widest mb-6">Example Searches</p>
          <div className="grid gap-4 md:grid-cols-3 max-w-4xl w-full">
            <button onClick={() => { localStorage.setItem('govassist-draft-query', 'I am a farmer from Tamil Nadu.'); navigate('/assistant'); }} className="card hover:border-govgreen hover:shadow-md transition text-left cursor-pointer bg-white text-slate-700 text-lg border-2">
              "I am a farmer from Tamil Nadu."
            </button>
            <button onClick={() => { localStorage.setItem('govassist-draft-query', 'I am a student looking for scholarships.'); navigate('/assistant'); }} className="card hover:border-govgreen hover:shadow-md transition text-left cursor-pointer bg-white text-slate-700 text-lg border-2">
              "I am a student looking for scholarships."
            </button>
            <button onClick={() => { localStorage.setItem('govassist-draft-query', 'I need a government business loan.'); navigate('/assistant'); }} className="card hover:border-govgreen hover:shadow-md transition text-left cursor-pointer bg-white text-slate-700 text-lg border-2">
              "I need a government business loan."
            </button>
          </div>
        </div>
      </div>
    </section>
  )
}

export function Assistant() { 
  const [query, setQuery] = useState(''); 
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false); 
  const [error, setError] = useState(''); 
  const [conversationId, setConversationId] = useState(null);
  const bottomRef = useRef(null);
  
  useEffect(() => {
    if (bottomRef.current) {
        bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const abortControllerRef = useRef(null);

  const sendMessage = async (text) => {
    if(!text.trim()) return setError('Please describe what support you are looking for.');
    
    if (abortControllerRef.current) {
        abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();
    
    const userMessage = { role: 'user', content: text };
    const assistantMessagePlaceholder = { 
      role: 'assistant', 
      content: '', 
      recommendations: [], 
      data: null,
      isStreaming: true
    };
    
    setMessages(prev => [...prev, userMessage, assistantMessagePlaceholder]);
    setLoading(true);
    setError('');
    
    let accumulated = '';
    
    await chatStream(
        text, 
        conversationId, 
        (metadata) => {
            setLoading(false);
            setConversationId(metadata.conversation_id);
            setMessages(prev => {
                const newMessages = [...prev];
                const last = { ...newMessages[newMessages.length - 1] };
                if (last.role === 'assistant') {
                    last.recommendations = metadata.recommendations;
                    last.data = metadata;
                    newMessages[newMessages.length - 1] = last;
                }
                return newMessages;
            });
        },
        (chunk) => {
            accumulated += chunk;
            setMessages(prev => {
                const newMessages = [...prev];
                const last = { ...newMessages[newMessages.length - 1] };
                if (last.role === 'assistant') {
                    last.content = accumulated;
                    newMessages[newMessages.length - 1] = last;
                }
                return newMessages;
            });
        },
        () => {
            setMessages(prev => {
                const newMessages = [...prev];
                const last = { ...newMessages[newMessages.length - 1] };
                if (last.role === 'assistant') {
                    last.isStreaming = false;
                    newMessages[newMessages.length - 1] = last;
                }
                return newMessages;
            });
        },
        (err) => {
            if (err.name === 'AbortError') return;
            setLoading(false);
            setError(err.message || 'GovAssist service is currently unavailable.');
            setMessages(prev => {
                const last = prev[prev.length - 1];
                if (last.role === 'assistant' && !last.content) {
                    return prev.slice(0, -1);
                }
                return prev;
            });
            setQuery(text);
        },
        abortControllerRef.current.signal
    );
  };

  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  useEffect(() => {
    const draft = localStorage.getItem('govassist-draft-query');
    if (draft && messages.length === 0) {
      localStorage.removeItem('govassist-draft-query');
      sendMessage(draft);
    }
  }, []); // Run once on mount

  const startNewConversation = () => {
    setMessages([]);
    setConversationId(null);
    setQuery('');
    setError('');
  };
  
  const submit = async(e) => {
    e.preventDefault();
    const currentQuery = query;
    setQuery('');
    await sendMessage(currentQuery);
  }; 
  
  return (
    <section className="shell py-12">
      <div className="max-w-3xl mb-8 flex justify-between items-start">
        <div>
          <p className="eyebrow">AI Scheme Assistant</p>
          <h1 className="page-title text-4xl mb-4">Discover Government Support</h1>
          <p className="text-lg text-slate-700">
            You can describe your situation in everyday language. The assistant searches the live knowledge base to find relevant schemes.
          </p>
        </div>
        {messages.length > 0 && (
          <button onClick={startNewConversation} className="button-secondary shrink-0">
            New Conversation
          </button>
        )}
      </div>

      <div className="max-w-4xl bg-slate-50 border border-slate-200 rounded p-6 mb-8 max-h-[60vh] overflow-y-auto">
        {messages.length === 0 && (
          <div className="text-center py-16 text-slate-500">
            <h3 className="text-2xl text-govnavy mb-4">How can I help you find a government scheme?</h3>
            <p className="mb-8">Choose an example to get started:</p>
            <div className="flex flex-wrap justify-center gap-4">
               <button onClick={() => sendMessage("Find schemes for farmers")} className="button-secondary bg-white text-govnavy border-govnavy">Find schemes for farmers</button>
               <button onClick={() => sendMessage("Find scholarships for students")} className="button-secondary bg-white text-govnavy border-govnavy">Find scholarships for students</button>
               <button onClick={() => sendMessage("Find business loans")} className="button-secondary bg-white text-govnavy border-govnavy">Find business loans</button>
               <button onClick={() => sendMessage("Find housing assistance")} className="button-secondary bg-white text-govnavy border-govnavy">Find housing assistance</button>
            </div>
          </div>
        )}
        
        {messages.map((msg, idx) => (
          <div key={idx} className={`mb-8 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
            <div className={`inline-block max-w-[90%] text-left p-4 rounded-lg shadow-sm ${msg.role === 'user' ? 'bg-govnavy text-white' : 'bg-white border-l-4 border-govnavy'}`}>
              {msg.role === 'assistant' && (
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-8 h-8 rounded-full bg-govnavy flex items-center justify-center text-white text-xs font-bold">AI</div>
                  <strong className="text-govnavy">Assistant</strong>
                </div>
              )}
              {msg.role === 'assistant' ? (
                <div className="prose prose-slate prose-lg max-w-none">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                  {msg.isStreaming && <span className="inline-block w-2 h-4 ml-1 bg-govnavy animate-pulse"></span>}
                </div>
              ) : (
                <p className="whitespace-pre-line text-lg m-0">
                  {msg.content}
                </p>
              )}
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="text-left mb-8">
            <div className="inline-block p-4 rounded-lg shadow-sm bg-blue-50 border border-blue-200 text-blue-900">
               <div className="flex items-center gap-3">
                 <div className="w-6 h-6 border-4 border-blue-300 border-t-blue-700 rounded-full animate-spin"></div>
                 <span className="font-semibold">Retrieving and evaluating scheme records...</span>
               </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={submit} className="card bg-white max-w-4xl border-t-4 border-t-govgreen">
        <label htmlFor="query" className="text-lg font-bold text-slate-700 block mb-2">Send a message</label>
        <textarea 
          id="query" 
          value={query} 
          onChange={e => setQuery(e.target.value)} 
          placeholder="Ask a question or provide more profile information..." 
          rows="3"
          className="text-lg w-full border border-slate-300 p-3 rounded focus:ring-2 focus:ring-govnavy focus:border-govnavy outline-none transition"
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              submit(e);
            }
          }}
        />
        <div className="mt-4 flex justify-between items-center">
          <span className="text-sm text-slate-500">Press Enter to send, Shift+Enter for new line</span>
          <button className="button-primary px-8 text-lg" disabled={loading}>
            {loading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </form>
      
      {error && <div className="notice-error mt-6 max-w-4xl" role="alert"><strong>Error:</strong> {error}</div>}
    </section>
  )
}

export function Details() { 
  const {state} = useLocation(); 
  const {schemeId} = useParams(); 
  
  if(!state?.scheme) {
    return (
      <section className="shell py-16 max-w-3xl text-center">
        <h1 className="page-title text-3xl">Scheme Details Unavailable</h1>
        <p className="text-lg">Please open a scheme from a live recommendation to view its source-backed details.</p>
        <Link className="button-primary inline-block mt-8" to="/assistant">Return to Assistant</Link>
      </section>
    );
  }
  
  const s = state.scheme; 
  const unavailable = 'Official source information is not available in the current knowledge base.';
  
  return (
    <section className="shell py-12 max-w-4xl">
      <Link className="text-govnavy font-bold hover:underline inline-flex items-center" to="/assistant">
        <span className="mr-2">←</span> Back to Search Results
      </Link>
      
      <div className="mt-8 bg-white p-8 md:p-10 border-t-8 border-t-govnavy rounded shadow-sm">
        <div className="mb-8 border-b border-slate-200 pb-6">
          <p className="text-sm font-bold tracking-widest uppercase text-govgreen mb-3">
            {s.level || 'Unknown Level'} • {s.category || 'Uncategorized'}
          </p>
          <h1 className="text-3xl md:text-5xl font-bold text-govnavy leading-tight mt-0 mb-4">{s.scheme_name}</h1>
          
          <div className="flex flex-wrap items-center gap-4 mt-6">
            <span className={`badge badge-${s.eligibility_status} text-base px-3 py-1`}>Status: {s.eligibility_status.replace(/_/g, ' ')}</span>
            {s.source_url ? (
              <a className="button-primary" href={s.source_url} target="_blank" rel="noreferrer">Visit Official Source</a>
            ) : (
              <span className="text-sm text-slate-500 italic bg-slate-100 px-3 py-1 rounded">No official link available</span>
            )}
          </div>
        </div>
        
        <div className="space-y-10">
          <section>
            <h2 className="text-2xl mt-0">Overview & Benefits</h2>
            <div className="bg-slate-50 p-5 rounded border border-slate-200 mt-4">
              <h3 className="text-lg mt-0">Description</h3>
              <p className="whitespace-pre-line text-slate-700">{s.description || unavailable}</p>
              
              <h3 className="text-lg mt-6">Benefits</h3>
              <p className="whitespace-pre-line text-slate-700">{s.benefits || unavailable}</p>
            </div>
          </section>
          
          <section>
            <h2 className="text-2xl mt-0">Eligibility Requirements</h2>
            <div className="bg-slate-50 p-5 rounded border border-slate-200 mt-4">
              <p className="whitespace-pre-line text-slate-700">{s.eligibility || unavailable}</p>
            </div>
          </section>
          
          <section>
            <h2 className="text-2xl mt-0">Application Process & Documents</h2>
            <div className="bg-slate-50 p-5 rounded border border-slate-200 mt-4">
              <h3 className="text-lg mt-0">How to Apply</h3>
              <p className="whitespace-pre-line text-slate-700">{s.application || unavailable}</p>
              
              <h3 className="text-lg mt-6">Required Documents</h3>
              <p className="whitespace-pre-line text-slate-700">{s.documents || unavailable}</p>
            </div>
          </section>
        </div>
      </div>
    </section>
  )
}

export function Dashboard({user}) {
  const recent = localStorage.getItem('govassist-recent-query');
  return (
    <section className="shell py-12 max-w-5xl">
      <div className="mb-10">
        <p className="eyebrow">Citizen Portal</p>
        <h1 className="page-title text-4xl">Welcome, {user.name}</h1>
        <p className="lead">Manage your profile and explore government schemes tailored to your situation.</p>
      </div>
      
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Link className="card bg-govnavy text-white hover:bg-govgreen transition flex flex-col justify-between group no-underline" to="/assistant">
          <div>
            <h2 className="text-white border-0 mt-0 text-2xl group-hover:text-white">Find Schemes</h2>
            <p className="text-slate-300">Use the live assistant to explore the knowledge base.</p>
          </div>
          <span className="font-bold mt-4 block">Launch Assistant →</span>
        </Link>
        <Link className="card bg-white hover:border-govgreen transition flex flex-col justify-between group no-underline" to="/profile">
          <div>
            <h2 className="border-0 mt-0 text-2xl text-govnavy">Update Profile</h2>
            <p className="text-slate-600">Keep your details up to date for better eligibility checking.</p>
          </div>
          <span className="font-bold text-govgreen mt-4 block">Manage Profile →</span>
        </Link>
      </div>
      
      {recent && (
        <div className="mt-12 bg-slate-50 p-6 border border-slate-200 rounded">
          <h2 className="border-0 mt-0 text-xl">Recent Local Search</h2>
          <p className="font-medium text-lg italic text-slate-700">"{recent}"</p>
          <div className="mt-4 flex items-center justify-between">
            <span className="text-xs text-slate-500 uppercase font-bold tracking-wider">Stored locally on this device</span>
            <Link className="button-secondary text-sm py-1.5 px-4" to="/assistant">Search Again</Link>
          </div>
        </div>
      )}
    </section>
  )
}

export function Profile({user}) {
  const fields = [
    ['age','Age (Years)'],
    ['gender','Gender'],
    ['state','State / Union Territory'],
    ['education','Highest Education Level'],
    ['occupation','Current Occupation'],
    ['income','Annual Income (₹)'],
    ['caste_category','Category / Caste (e.g. SC/ST/OBC/General)']
  ];
  
  const [profile,setProfile] = useState({});
  const [status,setStatus] = useState('');
  const [loading,setLoading] = useState(true);
  
  useEffect(() => {
    getUserProfile()
      .then(({profile:data}) => setProfile(data || {}))
      .catch(() => setStatus('Error: Your profile could not be loaded.'))
      .finally(() => setLoading(false));
  }, []);
  
  const submit = async e => {
    e.preventDefault();
    setStatus('');
    setLoading(true);
    try {
      const result = await saveUserProfile(profile);
      setProfile(result.profile);
      setStatus('Success: Profile saved securely to your account.');
    } catch {
      setStatus('Error: Your profile could not be saved. Please sign in again.');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <section className="shell py-12 max-w-4xl">
      <div className="mb-10">
        <p className="eyebrow">Account Management</p>
        <h1 className="page-title text-4xl">Your Profile</h1>
        <p className="text-lg text-slate-600">Signed in securely as <strong>{user.email}</strong>. Providing accurate information helps GovAssist evaluate scheme eligibility more effectively.</p>
      </div>
      
      <form className="bg-white p-8 border-t-8 border-t-govnavy rounded shadow-sm" onSubmit={submit}>
        <div className="grid gap-6 md:grid-cols-2 mb-8">
          {fields.map(([key,label]) => (
            <div key={key} className="flex flex-col">
              <label htmlFor={key}>{label}</label>
              <input 
                id={key}
                name={key} 
                value={profile[key] || ''} 
                onChange={e => setProfile({...profile, [key]: e.target.value})}
                placeholder="Not provided"
                className="mt-1"
              />
            </div>
          ))}
        </div>
        
        <div className="border-t border-slate-200 pt-6 flex flex-wrap items-center justify-between gap-4">
          <button className="button-primary px-8" disabled={loading}>
            {loading ? 'Processing...' : 'Save Profile Details'}
          </button>
          
          {status && (
            <div className={`px-4 py-2 font-bold rounded ${status.startsWith('Success') ? 'bg-green-50 text-green-800 border border-green-200' : 'bg-red-50 text-red-800 border border-red-200'}`}>
              {status}
            </div>
          )}
        </div>
      </form>
    </section>
  )
}

export function Auth({register: isRegister=false, onAuthenticated}) {
  const nav = useNavigate();
  const [form, setForm] = useState({name:'', email:'', password:'', confirm_password:''});
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [loading, setLoading] = useState(false);
  
  const update = e => setForm({...form, [e.target.name]: e.target.value});
  
  const submit = async e => {
    e.preventDefault();
    setError('');
    setNotice('');
    if (isRegister && form.password !== form.confirm_password) return setError('Passwords do not match.');
    setLoading(true);
    try {
      const session = isRegister ? await register(form) : await login({email:form.email, password:form.password});
      onAuthenticated(session);
      setNotice(isRegister ? 'Registration successful.' : 'Login successful.');
      nav('/dashboard');
    } catch(err) {
      setError(err.response?.data?.detail || 'Unable to authenticate. Please check your network and try again.');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <section className="shell py-16 flex justify-center">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-govnavy mb-3">{isRegister ? 'Create an Account' : 'Secure Login'}</h1>
          <p className="text-slate-600">
            {isRegister ? 'Register for a secure portal account to manage your profile.' : 'Access your GovAssist profile and saved settings.'}
          </p>
        </div>
        
        <form className="bg-white p-8 border-t-8 border-t-govnavy rounded shadow-sm" onSubmit={submit}>
          <div className="space-y-5 mb-8">
            {isRegister && (
              <div>
                <label htmlFor="name">Full Name</label>
                <input id="name" name="name" value={form.name} onChange={update} required />
              </div>
            )}
            <div>
              <label htmlFor="email">Email Address</label>
              <input id="email" name="email" value={form.email} onChange={update} type="email" required />
            </div>
            <div>
              <label htmlFor="password">Password</label>
              <input id="password" name="password" value={form.password} onChange={update} type="password" required minLength="8" />
            </div>
            {isRegister && (
              <div>
                <label htmlFor="confirm_password">Confirm Password</label>
                <input id="confirm_password" name="confirm_password" value={form.confirm_password} onChange={update} type="password" required minLength="8" />
              </div>
            )}
          </div>
          
          <button className="button-primary w-full py-3 text-lg" disabled={loading}>
            {loading ? 'Processing...' : isRegister ? 'Register Account' : 'Sign In'}
          </button>
          
          {error && <div className="notice-error mt-4" role="alert"><strong>Error:</strong> {error}</div>}
          {notice && <div className="notice-info mt-4"><strong>Success:</strong> {notice}</div>}
        </form>
        
        <div className="text-center mt-6">
          {!isRegister ? (
            <p className="text-slate-600">New to GovAssist? <Link className="font-bold text-govgreen" to="/register">Create an account</Link></p>
          ) : (
            <p className="text-slate-600">Already registered? <Link className="font-bold text-govgreen" to="/login">Sign in securely</Link></p>
          )}
        </div>
      </div>
    </section>
  )
}

export function HowItWorks() {
  const steps = [
    ['User Query', 'You describe your needs in everyday language.'],
    ['Profile Extraction', 'Relevant profile information (e.g., state, occupation) is extracted from your query and saved profile.'],
    ['Semantic Retrieval', 'The BGE model represents your query semantically, and FAISS retrieves relevant schemes from the knowledge base.'],
    ['Eligibility Analysis', 'The retrieved schemes are checked against your profile to evaluate eligibility evidence.'],
    ['Ranking', 'The schemes are ranked to prioritize the most relevant and eligible options.'],
    ['Grounded Recommendation', 'The system generates a final summary based strictly on the retrieved canonical records.']
  ];
  
  return (
    <section className="shell py-16 max-w-4xl">
      <div className="mb-12">
        <p className="eyebrow">System Architecture</p>
        <h1 className="page-title text-4xl">How GovAssist Works</h1>
        <p className="text-lg text-slate-700">A fully traceable pipeline connects your question to the official knowledge base. We keep semantic relevance and eligibility analysis separate to ensure transparency.</p>
      </div>
      
      <ol className="timeline mt-10">
        {steps.map(([title, desc], i) => (
          <li key={title} className="bg-white p-6 border border-slate-200 rounded shadow-sm mb-6 ml-6">
            <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-govnavy font-bold text-white text-lg absolute -left-11 top-6">
              {i+1}
            </span>
            <div>
              <h2 className="border-0 mt-0 text-xl">{title}</h2>
              <p className="text-slate-600 m-0">{desc}</p>
            </div>
          </li>
        ))}
      </ol>
    </section>
  )
}

export function About() {
  return (
    <section className="shell py-16 max-w-4xl">
      <div className="mb-10">
        <p className="eyebrow">About the Platform</p>
        <h1 className="page-title text-4xl">GovAssist AI</h1>
        <p className="lead">Government scheme discovery powered by retrieval-augmented generation.</p>
      </div>
      
      <div className="bg-white p-8 border border-slate-200 rounded shadow-sm space-y-6 text-lg text-slate-700">
        <p>
          GovAssist connects a natural-language conversational interface to a verified retrieval pipeline. The system is designed to help citizens, workers, and businesses navigate complex government support programs.
        </p>
        <h2 className="text-2xl pt-4">Grounded Information</h2>
        <p>
          All scheme information is retrieved from a pre-processed knowledge base. The system does not hallucinate requirements or invent new schemes; it only presents data found in the canonical records.
        </p>
        <h2 className="text-2xl pt-4">Eligibility Transparency</h2>
        <p>
          We strictly separate <strong>Semantic Relevance</strong> (why a scheme matched your search) from <strong>Eligibility Evidence</strong> (whether your profile meets the stated rules). This ensures you know exactly why a recommendation was made.
        </p>
        
        <div className="notice-info mt-8 bg-slate-50 border-slate-300 text-slate-800 p-6">
          <strong className="block mb-2 text-govnavy">Disclaimer of Authority</strong>
          GovAssist is a discovery and assistance tool. It is <strong>not</strong> the final government eligibility authority. Final eligibility decisions are always made by the respective government department upon formal application.
        </div>
        
        <div className="pt-6">
          <Link className="button-primary px-8" to="/assistant">Launch Assistant</Link>
        </div>
      </div>
    </section>
  )
}

export function NotFound() {
  return (
    <section className="shell py-24 text-center max-w-2xl">
      <h1 className="text-6xl font-bold text-govnavy mb-6">404</h1>
      <h2 className="text-2xl border-0 mb-4 mt-0">Page Not Found</h2>
      <p className="text-lg text-slate-600 mb-8">The requested page does not exist or has been moved.</p>
      <Link className="button-primary px-8" to="/">Return to Homepage</Link>
    </section>
  )
}

export function Directory() {
  const [query, setQuery] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const submit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return setError('Please enter a search term.');
    setLoading(true);
    setError('');
    try {
      const result = await recommend(query);
      setData(result);
    } catch (err) {
      setError('Unable to fetch directory results.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="shell py-12">
      <div className="max-w-4xl mb-8">
        <p className="eyebrow">Scheme Directory</p>
        <h1 className="page-title text-4xl">Search Schemes</h1>
        <p className="text-lg text-slate-700">Search the knowledge base using semantic natural language. Filters are automatically applied based on your search intent.</p>
      </div>

      <form onSubmit={submit} className="mb-12 flex gap-4 max-w-3xl">
        <input 
          className="flex-1 text-lg"
          placeholder="e.g. MSME business loans in Karnataka"
          value={query}
          onChange={e => setQuery(e.target.value)}
        />
        <button className="button-primary" disabled={loading}>
          {loading ? 'Searching...' : 'Search Directory'}
        </button>
      </form>

      {error && <div className="notice-error mb-8">{error}</div>}

      {data && (
        <div className="grid gap-6">
          <p className="text-slate-600 font-bold mb-4">{data.recommendations.length} results found.</p>
          {data.recommendations.map(s => (
            <div key={s.scheme_id} className="bg-white p-6 rounded border border-slate-200 shadow-sm flex flex-col md:flex-row gap-6 justify-between items-start">
              <div className="flex-1">
                <span className="text-xs font-bold text-govgreen uppercase tracking-widest block mb-2">{s.level} • {s.category}</span>
                <h3 className="text-xl text-govnavy font-bold mt-0 mb-3">{s.scheme_name}</h3>
                <p className="text-slate-700 line-clamp-2">{s.description || 'No description available.'}</p>
                <div className="mt-4">
                  <span className={`badge badge-${s.eligibility_status}`}>{s.eligibility_status.replace(/_/g, ' ')}</span>
                </div>
              </div>
              <div className="md:w-48 shrink-0">
                <Link className="button-secondary w-full text-center" to={`/scheme/${s.scheme_id}`} state={{scheme: s}}>View Details</Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
