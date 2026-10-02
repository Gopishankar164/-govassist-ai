import React from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';

export default function LoginPage() {
  const { register, handleSubmit, formState: { errors } } = useForm();
  const navigate = useNavigate();

  const onSubmit = async (data) => {
    try {
      const res = await axios.post('/api/v1/auth/login', data);
      localStorage.setItem('token', res.data.access_token);
      navigate('/dashboard/chat');
    } catch (error) {
      alert('Login failed: ' + (error.response?.data?.detail || error.message));
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6">
      <div className="card w-full max-w-md">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-white mb-2">Welcome Back</h2>
          <p className="text-muted">Sign in to GovAssist AI</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Email</label>
            <input 
              {...register('email', { required: true })} 
              className="input-field" 
              type="email" 
              placeholder="name@example.com"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Password</label>
            <input 
              {...register('password', { required: true })} 
              className="input-field" 
              type="password" 
              placeholder="••••••••"
            />
          </div>
          
          <button type="submit" className="btn-primary w-full py-3 mt-6">
            Sign In
          </button>
        </form>

        <p className="text-center text-sm text-muted mt-6">
          Don't have an account? <Link to="/auth/register" className="text-primary hover:underline">Register</Link>
        </p>
      </div>
    </div>
  );
}
