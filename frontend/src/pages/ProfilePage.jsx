import React from 'react';
import { useForm } from 'react-hook-form';

export default function ProfilePage() {
  const { register, handleSubmit } = useForm({
    defaultValues: {
      age: 22,
      income: 150000,
      gender: 'Female',
      occupation: 'Student',
      state: 'Tamil Nadu',
      category: 'General'
    }
  });

  const onSubmit = (data) => {
    console.log("Profile updated:", data);
    alert("Profile saved successfully!");
  };

  return (
    <div className="max-w-2xl mx-auto w-full">
      <div className="card">
        <h2 className="text-xl font-bold text-white mb-6 border-b border-slate-700/50 pb-4">Citizen Profile</h2>
        
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Age</label>
              <input type="number" {...register('age')} className="input-field" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Annual Income (₹)</label>
              <input type="number" {...register('income')} className="input-field" />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Gender</label>
              <select {...register('gender')} className="input-field">
                <option>Male</option>
                <option>Female</option>
                <option>Transgender</option>
                <option>Other</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">State</label>
              <input type="text" {...register('state')} className="input-field" />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Occupation</label>
              <select {...register('occupation')} className="input-field">
                <option>Student</option>
                <option>Farmer</option>
                <option>Employed</option>
                <option>Self-Employed</option>
                <option>Unemployed</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Category</label>
              <select {...register('category')} className="input-field">
                <option>General</option>
                <option>OBC</option>
                <option>SC</option>
                <option>ST</option>
              </select>
            </div>
          </div>

          <button type="submit" className="btn-primary w-full">Save Profile</button>
        </form>
      </div>
    </div>
  );
}
