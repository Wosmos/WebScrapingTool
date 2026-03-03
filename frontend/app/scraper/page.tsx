'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
// import { api } from '@/lib/api';
import Link from 'next/link';

export default function ScraperPage() {
  const router = useRouter();
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  const handleScrape = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setResult(null);
    setLoading(true);

    try {
      // Simulation for design view
      // const data = await api.scrapeSingleUrl({ url, respect_robots: true });
      // setResult(data);
      
      // Temporary mock for visual testing
      setTimeout(() => {
        setResult({
          session_id: '123',
          metrics: { word_count: 1240, char_count: 8540, line_count: 142 },
          content: "Example extracted content from the target website..."
        });
        setLoading(false);
      }, 1500);
    } catch (err) {
      setError('Failed to scrape URL. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#02040a] text-slate-200 font-sans">
      {/* 1. Integrated Navigation */}
      <nav className="border-b border-white/5 bg-[#02040a]/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex justify-between items-center">
          <Link href="/dashboard" className="group flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-slate-500 hover:text-white transition">
            <svg className="w-4 h-4 group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Dashboard
          </Link>
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-purple-500 animate-pulse shadow-[0_0_8px_#a855f7]" />
            <span className="text-sm font-medium text-white tracking-tight">Single URL Scraper</span>
          </div>
          <div className="w-20" /> {/* Spacer for symmetry */}
        </div>
      </nav>

      <main className="max-w-5xl mx-auto px-6 py-12">
        {/* 2. Scraper Input Card */}
        <div className="bg-[#0a0f1d]/60 backdrop-blur-2xl rounded-[2rem] border border-white/5 p-8 mb-8 shadow-2xl">
          <form onSubmit={handleScrape} className="space-y-6">
            <div className="space-y-2">
              <label htmlFor="url" className="text-[10px] uppercase tracking-[0.2em] font-bold text-slate-500 ml-1">
                Target Endpoint
              </label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-500 group-focus-within:text-purple-400 transition-colors">
                  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                  </svg>
                </div>
                <input
                  id="url"
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="w-full pl-12 pr-4 py-4 bg-white/5 border border-white/10 rounded-xl text-white placeholder-slate-600 focus:ring-1 focus:ring-purple-500/50 outline-none transition-all text-lg"
                  placeholder="https://example.com"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-white text-black font-black py-4 rounded-xl hover:bg-slate-200 transition-all disabled:opacity-50 active:scale-[0.98] shadow-[0_0_20px_rgba(255,255,255,0.05)]"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-3 italic">
                  <div className="w-4 h-4 border-2 border-black/20 border-t-black rounded-full animate-spin"></div>
                  INITIALIZING EXTRACTION...
                </span>
              ) : (
                'RUN SCRAPER'
              )}
            </button>
          </form>

          {error && (
            <div className="mt-6 bg-red-500/10 border border-red-500/20 text-red-400 text-xs px-4 py-3 rounded-xl flex items-center gap-2">
              <span className="w-1.5 h-1.5 bg-red-500 rounded-full animate-pulse" />
              {error}
            </div>
          )}
        </div>

        {/* 3. Result Section (High Contrast) */}
        {result && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-purple-500/10 border border-purple-500/20 p-6 rounded-[2rem]">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-purple-500 flex items-center justify-center text-white">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white tracking-tight">Extraction Complete</h3>
                  <p className="text-xs text-purple-400 font-mono">Session: {result.session_id}</p>
                </div>
              </div>
              <button
                onClick={() => router.push(`/session/${result.session_id}`)}
                className="px-6 py-3 bg-white/5 border border-white/10 hover:bg-white/10 text-white text-xs font-bold uppercase tracking-widest rounded-xl transition"
              >
                Inspect Full Session
              </button>
            </div>
            
            {/* Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[
                { label: 'Words', value: result.metrics?.word_count, color: 'text-blue-400' },
                { label: 'Characters', value: result.metrics?.char_count, color: 'text-emerald-400' },
                { label: 'Lines', value: result.metrics?.line_count, color: 'text-purple-400' }
              ].map((m, i) => (
                <div key={i} className="bg-[#0a0f1d] border border-white/5 p-6 rounded-2xl">
                  <p className="text-[10px] uppercase tracking-widest font-bold text-slate-500 mb-2">{m.label}</p>
                  <p className={`text-3xl font-light ${m.color}`}>{m.value?.toLocaleString()}</p>
                </div>
              ))}
            </div>

            {/* Terminal Preview */}
            <div className="bg-black border border-white/10 rounded-[2rem] overflow-hidden shadow-2xl">
              <div className="bg-white/5 px-6 py-3 border-b border-white/10 flex items-center justify-between">
                <span className="text-[10px] uppercase tracking-[0.2em] font-bold text-slate-500">Raw Data Preview</span>
                <div className="flex gap-1.5">
                  <div className="w-2 h-2 rounded-full bg-white/10" />
                  <div className="w-2 h-2 rounded-full bg-white/10" />
                  <div className="w-2 h-2 rounded-full bg-white/10" />
                </div>
              </div>
              <div className="p-8 max-h-[500px] overflow-y-auto custom-scrollbar font-mono text-sm leading-relaxed text-purple-200/80">
                <pre className="whitespace-pre-wrap">{result.content}</pre>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}