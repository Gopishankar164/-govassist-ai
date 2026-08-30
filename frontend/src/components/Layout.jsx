import { Link, NavLink } from 'react-router-dom'
import { useState } from 'react'

export default function Layout({ children, user, onLogout }) { 
  const [open, setOpen] = useState(false); 
  
  const unauthLinks = [
    ['/', 'Home'],
    ['/assistant', 'Assistant']
  ];
  
  const authLinks = [
    ['/assistant', 'Assistant'],
    ['/profile', 'Profile']
  ];

  const links = user ? authLinks : unauthLinks;
  
  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b-4 border-govgreen bg-white sticky top-0 z-30 shadow-sm">
        <nav className="shell flex min-h-[4rem] items-center justify-between gap-4 py-3">
          <Link to={user ? "/assistant" : "/"} className="font-bold text-govnavy text-xl no-underline flex items-center" onClick={() => setOpen(false)}>
            <span className="inline-block bg-govnavy px-3 py-1 mr-3 text-white tracking-widest uppercase text-sm">GovAssist AI</span>
            <span className="hidden sm:inline text-slate-500 font-normal text-lg">Government Scheme Assistant</span>
          </Link>
          
          <button className="md:hidden button-secondary" aria-expanded={open} onClick={() => setOpen(!open)}>
            {open ? 'Close' : 'Menu'}
          </button>
          
          <div className={`${open ? 'flex' : 'hidden'} md:flex absolute md:static top-full left-0 right-0 md:items-center gap-6 bg-white p-5 md:p-0 border-b md:border-0 flex-col md:flex-row shadow-lg md:shadow-none`} >
            {links.map(([to,label]) => (
              <NavLink 
                key={to} 
                to={to} 
                onClick={() => setOpen(false)} 
                className={({isActive}) => `nav-link font-medium ${isActive ? 'text-govgreen underline decoration-2 underline-offset-4' : 'text-slate-700'}`}
              >
                {label}
              </NavLink>
            ))}
            
            <div className="md:ml-4 flex flex-col md:flex-row gap-3 pt-4 md:pt-0 border-t md:border-0 border-slate-200 mt-2 md:mt-0">
              {user ? (
                <button className="button-secondary" onClick={() => { onLogout(); setOpen(false); }}>Logout</button>
              ) : (
                <>
                  <Link className="button-secondary" to="/login" onClick={() => setOpen(false)}>Login</Link>
                  <Link className="button-primary" to="/register" onClick={() => setOpen(false)}>Create Account</Link>
                </>
              )}
            </div>
          </div>
        </nav>
      </header>
      
      <main className="flex-1 bg-govlight flex flex-col">
        {children}
      </main>
      
      <footer className="mt-auto bg-govnavy text-slate-300 border-t-8 border-govgreen">
        <div className="shell py-8 grid gap-8 md:grid-cols-2">
          <div>
            <strong className="text-white text-lg block mb-2">GovAssist AI</strong>
            <p className="max-w-lg text-sm leading-relaxed text-slate-300">
              Your information is used to personalize scheme recommendations.
            </p>
          </div>
          <div className="md:text-right flex flex-col md:items-end gap-2 text-sm">
             <div className="flex gap-4 mb-2">
                 <Link to="/about" className="text-slate-300 hover:text-white underline">About Platform</Link>
                 <Link to="/how-it-works" className="text-slate-300 hover:text-white underline">How It Works</Link>
                 <Link to="/schemes" className="text-slate-300 hover:text-white underline">Scheme Directory</Link>
             </div>
             <p className="text-slate-400 max-w-md">
               Recommendations provided by this tool require independent verification against official eligibility rules.
             </p>
          </div>
        </div>
      </footer>
    </div>
  ) 
}
