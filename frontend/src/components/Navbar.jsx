import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Bot, Sun, Moon, LogIn, UserPlus, LayoutDashboard, Search, BarChart3, Shield, User, LogOut } from 'lucide-react';

export function Navbar({ theme, toggleTheme, user, logout }) {
  const location = useLocation();
  const navigate = useNavigate();

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="sticky top-0 z-50 glass-panel border-b border-gray-800 px-6 py-3.5 mb-2 transition-all">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand Logo */}
        <Link to="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-xl gradient-bg-primary flex items-center justify-center shadow-lg group-hover:scale-105 transition-transform">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-xl tracking-tight gradient-text-primary">GovAssist AI</span>
              <span className="text-[10px] uppercase tracking-widest font-bold px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">Enterprise RAG</span>
            </div>
            <p className="text-xs text-gray-400 font-medium">Multi-Agent Scheme Intelligence</p>
          </div>
        </Link>

        {/* Navigation Links */}
        <div className="hidden md:flex items-center gap-1 bg-gray-900/50 p-1.5 rounded-2xl border border-gray-800">
          <Link
            to="/"
            className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all ${
              isActive('/') ? 'bg-indigo-600 text-white shadow-md' : 'text-gray-400 hover:text-white hover:bg-gray-800/60'
            }`}
          >
            Home
          </Link>
          <Link
            to="/assistant"
            className={`px-4 py-2 rounded-xl text-sm font-semibold flex items-center gap-2 transition-all ${
              isActive('/assistant') ? 'bg-indigo-600 text-white shadow-md' : 'text-gray-400 hover:text-white hover:bg-gray-800/60'
            }`}
          >
            <Bot className="w-4 h-4 text-cyan-400" />
            AI Assistant
          </Link>
          <Link
            to="/schemes"
            className={`px-4 py-2 rounded-xl text-sm font-semibold flex items-center gap-2 transition-all ${
              isActive('/schemes') ? 'bg-indigo-600 text-white shadow-md' : 'text-gray-400 hover:text-white hover:bg-gray-800/60'
            }`}
          >
            <Search className="w-4 h-4" />
            Search Schemes
          </Link>
          <Link
            to="/dashboard"
            className={`px-4 py-2 rounded-xl text-sm font-semibold flex items-center gap-2 transition-all ${
              isActive('/dashboard') ? 'bg-indigo-600 text-white shadow-md' : 'text-gray-400 hover:text-white hover:bg-gray-800/60'
            }`}
          >
            <LayoutDashboard className="w-4 h-4" />
            Dashboard
          </Link>
          <Link
            to="/analytics"
            className={`px-4 py-2 rounded-xl text-sm font-semibold flex items-center gap-2 transition-all ${
              isActive('/analytics') ? 'bg-indigo-600 text-white shadow-md' : 'text-gray-400 hover:text-white hover:bg-gray-800/60'
            }`}
          >
            <BarChart3 className="w-4 h-4" />
            Analytics
          </Link>
          <Link
            to="/admin"
            className={`px-4 py-2 rounded-xl text-sm font-semibold flex items-center gap-2 transition-all ${
              isActive('/admin') ? 'bg-indigo-600 text-white shadow-md' : 'text-gray-400 hover:text-white hover:bg-gray-800/60'
            }`}
          >
            <Shield className="w-4 h-4 text-amber-400" />
            Admin
          </Link>
        </div>

        {/* Right Actions & Theme Switcher */}
        <div className="flex items-center gap-3">
          <button
            onClick={toggleTheme}
            className="p-2.5 rounded-xl bg-gray-900/60 border border-gray-800 text-gray-300 hover:text-white hover:border-gray-700 transition-all"
            title="Toggle Light/Dark Theme"
          >
            {theme === 'dark' ? <Sun className="w-5 h-5 text-amber-400" /> : <Moon className="w-5 h-5 text-indigo-400" />}
          </button>

          {user ? (
            <div className="flex items-center gap-2">
              <Link
                to="/profile"
                className="flex items-center gap-2.5 px-3.5 py-2 rounded-xl bg-gray-900/80 border border-gray-800 hover:border-indigo-500/50 transition-all"
              >
                <div className="w-8 h-8 rounded-lg bg-indigo-600/30 text-indigo-400 font-bold flex items-center justify-center text-sm border border-indigo-500/40">
                  {user.full_name ? user.full_name[0].toUpperCase() : 'U'}
                </div>
                <div className="hidden lg:block text-left">
                  <p className="text-xs font-bold text-gray-200">{user.full_name}</p>
                  <p className="text-[10px] text-gray-400">{user.email}</p>
                </div>
              </Link>
              <button
                onClick={() => { logout(); navigate('/login'); }}
                className="p-2.5 rounded-xl bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20 transition-all"
                title="Logout"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                to="/login"
                className="px-4 py-2 rounded-xl text-sm font-semibold text-gray-300 hover:text-white hover:bg-gray-800/60 transition-all flex items-center gap-1.5"
              >
                <LogIn className="w-4 h-4" />
                Login
              </Link>
              <Link
                to="/register"
                className="px-4 py-2 rounded-xl text-sm font-semibold gradient-bg-primary text-white shadow-lg hover:shadow-indigo-500/30 transition-all flex items-center gap-1.5"
              >
                <UserPlus className="w-4 h-4" />
                Register
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
