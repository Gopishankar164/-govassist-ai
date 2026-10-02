import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { MessageSquare, UserCircle, Shield, LogOut } from 'lucide-react';

export default function DashboardLayout() {
  const location = useLocation();
  const isActive = (path) => location.pathname === path;

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-surface border-r border-slate-700/50 flex flex-col">
        <div className="p-6">
          <div className="flex items-center gap-2 font-bold text-xl text-white">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center">GA</div>
            <span>GovAssist<span className="text-primary">AI</span></span>
          </div>
        </div>

        <nav className="flex-1 px-4 space-y-2 mt-4">
          <NavItem to="/dashboard/chat" icon={<MessageSquare size={18} />} label="Ask AI" active={isActive('/dashboard/chat')} />
          <NavItem to="/dashboard/profile" icon={<UserCircle size={18} />} label="My Profile" active={isActive('/dashboard/profile')} />
          <NavItem to="/dashboard/admin" icon={<Shield size={18} />} label="Admin Panel" active={isActive('/dashboard/admin')} />
        </nav>

        <div className="p-4 border-t border-slate-700/50">
          <button 
            onClick={() => { localStorage.removeItem('token'); window.location.href = '/'; }}
            className="flex items-center gap-3 w-full px-4 py-2 text-slate-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
          >
            <LogOut size={18} /> Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col relative min-h-0">
        <header className="h-16 flex items-center justify-between px-8 border-b border-slate-700/50 bg-surface/50 backdrop-blur-md">
          <h1 className="font-semibold text-lg text-white capitalize">
            {location.pathname.split('/').pop().replace('-', ' ')}
          </h1>
          <div className="flex items-center gap-4">
            <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-medium">
              U
            </div>
          </div>
        </header>

        <div className="flex-1 overflow-auto p-8 relative">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

function NavItem({ to, icon, label, active }) {
  return (
    <Link 
      to={to} 
      className={`flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-colors ${
        active ? 'bg-primary/10 text-primary' : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
      }`}
    >
      {icon}
      {label}
    </Link>
  );
}
