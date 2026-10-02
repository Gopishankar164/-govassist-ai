import React, { useState } from 'react';
import { UploadCloud, Shield, FileText } from 'lucide-react';
import axios from 'axios';

export default function AdminPage() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post('/api/v1/ingest', formData);
      alert('Document ingested: ' + res.data.message);
    } catch (err) {
      alert('Upload failed.');
    } finally {
      setUploading(false);
      setFile(null);
    }
  };

  return (
    <div className="max-w-4xl mx-auto w-full space-y-6">
      <div className="grid grid-cols-3 gap-4">
        <div className="card border-primary/20 bg-primary/5">
          <Shield className="text-primary mb-2" size={24} />
          <div className="text-sm text-slate-400">Total Users</div>
          <div className="text-2xl font-bold text-white mt-1">1,245</div>
        </div>
        <div className="card border-secondary/20 bg-secondary/5">
          <FileText className="text-secondary mb-2" size={24} />
          <div className="text-sm text-slate-400">Indexed Schemes</div>
          <div className="text-2xl font-bold text-white mt-1">8,432</div>
        </div>
        <div className="card border-emerald-500/20 bg-emerald-500/5">
          <Shield className="text-emerald-500 mb-2" size={24} />
          <div className="text-sm text-slate-400">Avg Accuracy</div>
          <div className="text-2xl font-bold text-white mt-1">96.4%</div>
        </div>
      </div>

      <div className="card">
        <h2 className="text-xl font-bold text-white mb-6 border-b border-slate-700/50 pb-4">Document Ingestion (RAG Pipeline)</h2>
        
        <form onSubmit={handleUpload} className="flex flex-col items-center justify-center p-8 border-2 border-dashed border-slate-700 rounded-xl bg-surface/50 hover:bg-surface transition-colors cursor-pointer" onClick={() => document.getElementById('fileUpload').click()}>
          <UploadCloud size={48} className="text-primary mb-4" />
          <div className="text-white font-medium mb-1">Click to upload Government Documents</div>
          <div className="text-sm text-slate-400 mb-4">Supports PDF, JSON, Gazette Notifications</div>
          
          <input 
            id="fileUpload" 
            type="file" 
            className="hidden" 
            onChange={(e) => setFile(e.target.files[0])}
            accept=".pdf,.json,.txt"
          />
          
          {file && (
            <div className="mb-4 text-emerald-400 text-sm font-medium">Selected: {file.name}</div>
          )}

          <button 
            type="submit" 
            disabled={!file || uploading}
            className="btn-primary"
            onClick={(e) => e.stopPropagation()}
          >
            {uploading ? 'Processing...' : 'Upload & Rebuild Index'}
          </button>
        </form>
      </div>
    </div>
  );
}
