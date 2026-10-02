import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { ShieldCheck, Zap, Users, BrainCircuit, ArrowRight, FileSearch, CheckCircle2, Bot, Quote, Check } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background text-slate-100 flex flex-col font-sans">
      <nav className="p-6 flex justify-between items-center max-w-7xl mx-auto w-full border-b border-slate-800/50">
        <div className="flex items-center gap-2 font-bold text-2xl">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center shadow-lg shadow-primary/20">GA</div>
          <span>GovAssist<span className="text-primary">AI</span></span>
        </div>
        <div className="flex gap-4">
          <Link to="/auth/login" className="px-5 py-2 rounded-lg font-medium hover:bg-surface transition-colors">Login</Link>
          <Link to="/auth/register" className="btn-primary">Get Started</Link>
        </div>
      </nav>

      <main className="flex-1 flex flex-col items-center">
        {/* Hero Section */}
        <section className="w-full flex flex-col items-center justify-center text-center p-6 max-w-5xl mx-auto mt-20 mb-20">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary mb-8 text-sm font-semibold border border-primary/20"
          >
            <SparkleIcon /> Multi-Agent RAG Framework v2.0
          </motion.div>
          
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 bg-gradient-to-br from-white to-slate-400 bg-clip-text text-transparent"
          >
            Discover Government Schemes with AI Precision.
          </motion.h1>
          
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-xl text-muted mb-10 max-w-2xl"
          >
            Stop searching through thousands of pages. Our 10-agent AI system analyzes your profile, verifies rules, and finds the exact schemes you qualify for in seconds.
          </motion.p>
          
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="flex flex-col sm:flex-row gap-4"
          >
            <Link to="/auth/register" className="btn-primary flex items-center justify-center gap-2 px-8 py-4 text-lg rounded-xl shadow-xl shadow-primary/20">
              Start Your Search <ArrowRight size={20} />
            </Link>
          </motion.div>

          {/* Animated Statistics */}
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 0.6 }}
            className="grid grid-cols-2 md:grid-cols-4 gap-8 mt-32 w-full max-w-4xl"
          >
            <StatBox value="100+" label="Verified Schemes" icon={<ShieldCheck className="text-secondary" size={28} />} />
            <StatBox value="10" label="AI Agents" icon={<BrainCircuit className="text-primary" size={28} />} />
            <StatBox value="100%" label="Grounded Accuracy" icon={<Zap className="text-yellow-500" size={28} />} />
            <StatBox value="10k+" label="Citizens Helped" icon={<Users className="text-emerald-500" size={28} />} />
          </motion.div>
        </section>

        {/* Feature Cards Section */}
        <section className="w-full bg-surface/50 py-24">
          <div className="max-w-7xl mx-auto px-6">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-5xl font-bold mb-4">Powered by Multi-Agent AI</h2>
              <p className="text-muted max-w-2xl mx-auto">Our intelligent system breaks down complex government policies and matches them to your exact profile.</p>
            </div>
            <div className="grid md:grid-cols-3 gap-8">
              <FeatureCard 
                icon={<Bot size={32} className="text-primary" />}
                title="Profile Extraction Agent"
                description="Automatically extracts key demographic and financial details from your natural language queries."
              />
              <FeatureCard 
                icon={<FileSearch size={32} className="text-secondary" />}
                title="Semantic Search FAISS"
                description="Retrieves the most relevant schemes using high-dimensional vector embeddings of policy documents."
              />
              <FeatureCard 
                icon={<CheckCircle2 size={32} className="text-emerald-500" />}
                title="Eligibility Verification"
                description="Cross-references your profile against strict criteria to guarantee 100% accurate recommendations."
              />
            </div>
          </div>
        </section>

        {/* Testimonials Section */}
        <section className="w-full py-24 max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold mb-4">Citizen Success Stories</h2>
            <p className="text-muted">See how GovAssist AI is changing lives.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <TestimonialCard 
              text="I didn't know I was eligible for the PM Kisan scheme until the AI agent explained the exact rules to me. Saved me hours of research!"
              author="Rajesh Kumar"
              role="Farmer, Punjab"
            />
            <TestimonialCard 
              text="The verification agent accurately pointed out that my income bracket qualified me for the education subsidy. Brilliant platform."
              author="Anita Desai"
              role="Student, Maharashtra"
            />
            <TestimonialCard 
              text="As a small business owner, finding loans was tough. GovAssist found 3 schemes specifically for women entrepreneurs in minutes."
              author="Priya Sharma"
              role="Entrepreneur, Delhi"
            />
          </div>
        </section>

        {/* Pricing/Features Section */}
        <section className="w-full bg-gradient-to-b from-surface/30 to-background py-24">
          <div className="max-w-5xl mx-auto px-6">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-5xl font-bold mb-4">Start Finding Schemes Today</h2>
              <p className="text-muted">100% Free for all Indian Citizens.</p>
            </div>
            <div className="bg-surface border border-slate-700/50 rounded-2xl p-8 md:p-12 shadow-2xl max-w-3xl mx-auto relative overflow-hidden">
              <div className="absolute top-0 right-0 w-64 h-64 bg-primary/10 rounded-full blur-3xl -z-10 translate-x-1/2 -translate-y-1/2"></div>
              <div className="flex flex-col md:flex-row justify-between items-center gap-8">
                <div>
                  <h3 className="text-2xl font-bold mb-2">Citizen Access</h3>
                  <div className="text-4xl font-extrabold text-white mb-6">₹0 <span className="text-lg text-muted font-normal">/forever</span></div>
                  <ul className="space-y-3">
                    <FeatureItem text="Unlimited AI Chat" />
                    <FeatureItem text="Personalized Scheme Recommendations" />
                    <FeatureItem text="Save & Track Applications" />
                    <FeatureItem text="Access to 100+ Verified Schemes" />
                  </ul>
                </div>
                <div className="w-full md:w-auto">
                  <Link to="/auth/register" className="btn-primary w-full md:w-auto px-8 py-4 rounded-xl text-center block shadow-lg shadow-primary/20">
                    Create Free Account
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="w-full border-t border-slate-800/50 bg-surface/30 py-12">
        <div className="max-w-7xl mx-auto px-6 grid md:grid-cols-4 gap-8">
          <div className="col-span-2">
            <div className="flex items-center gap-2 font-bold text-xl mb-4">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center">GA</div>
              <span>GovAssist<span className="text-primary">AI</span></span>
            </div>
            <p className="text-muted max-w-sm">Empowering citizens with AI-driven access to government welfare and schemes. Accurate, fast, and secure.</p>
          </div>
          <div>
            <h4 className="font-semibold mb-4 text-white">Platform</h4>
            <ul className="space-y-2 text-muted">
              <li><Link to="/auth/login" className="hover:text-primary transition-colors">Login</Link></li>
              <li><Link to="/auth/register" className="hover:text-primary transition-colors">Sign Up</Link></li>
              <li><Link to="/dashboard" className="hover:text-primary transition-colors">Dashboard</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-4 text-white">Legal</h4>
            <ul className="space-y-2 text-muted">
              <li><a href="#" className="hover:text-primary transition-colors">Privacy Policy</a></li>
              <li><a href="#" className="hover:text-primary transition-colors">Terms of Service</a></li>
              <li><a href="#" className="hover:text-primary transition-colors">Contact Support</a></li>
            </ul>
          </div>
        </div>
        <div className="max-w-7xl mx-auto px-6 mt-12 pt-8 border-t border-slate-800/50 text-center text-sm text-slate-500">
          © {new Date().getFullYear()} GovAssist AI. All rights reserved.
        </div>
      </footer>
    </div>
  );
}

function StatBox({ value, label, icon }) {
  return (
    <div className="flex flex-col items-center gap-2">
      <div className="p-4 bg-slate-800/50 rounded-2xl mb-2 border border-slate-700/50 shadow-inner">{icon}</div>
      <div className="text-4xl font-extrabold text-white">{value}</div>
      <div className="text-sm font-medium text-muted uppercase tracking-wider">{label}</div>
    </div>
  );
}

function FeatureCard({ icon, title, description }) {
  return (
    <div className="card hover:-translate-y-2 transition-transform duration-300">
      <div className="w-14 h-14 rounded-xl bg-slate-800 flex items-center justify-center mb-6 border border-slate-700">
        {icon}
      </div>
      <h3 className="text-xl font-bold mb-3 text-white">{title}</h3>
      <p className="text-muted leading-relaxed">{description}</p>
    </div>
  );
}

function TestimonialCard({ text, author, role }) {
  return (
    <div className="card relative">
      <Quote className="absolute top-6 right-6 text-slate-700" size={40} />
      <p className="text-slate-300 mb-8 relative z-10 italic">"{text}"</p>
      <div className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary/50 to-secondary/50 flex items-center justify-center font-bold text-white">
          {author.charAt(0)}
        </div>
        <div>
          <div className="font-bold text-white">{author}</div>
          <div className="text-sm text-primary">{role}</div>
        </div>
      </div>
    </div>
  );
}

function FeatureItem({ text }) {
  return (
    <li className="flex items-center gap-3 text-slate-300">
      <Check size={18} className="text-primary flex-shrink-0" />
      <span>{text}</span>
    </li>
  );
}

function SparkleIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M10.8491 2.33535C11.3116 1.48822 12.5218 1.48822 12.9843 2.33535L15.4211 6.80053C15.6315 7.18616 15.9818 7.48512 16.4026 7.63737L21.2721 9.40057C22.1963 9.73516 22.3619 10.9702 21.5647 11.5831L17.3629 14.8142C17.0003 15.0931 16.8206 15.5491 16.899 15.9893L17.8071 21.0858C17.9795 22.0537 16.9292 22.759 16.071 22.251L11.5458 19.5815C11.1551 19.351 10.6783 19.351 10.2876 19.5815L5.76239 22.251C4.90422 22.759 3.85387 22.0537 4.02626 21.0858L4.93437 15.9893C5.01278 15.5491 4.8331 15.0931 4.47047 14.8142L0.268686 11.5831C-0.528549 10.9702 -0.362878 9.73516 0.56133 9.40057L5.43078 7.63737C5.85157 7.48512 6.20188 7.18616 6.41228 6.80053L8.84911 2.33535H10.8491Z" fill="currentColor"/>
    </svg>
  )
}
