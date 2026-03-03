'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import Link from 'next/link';

export default function BatchPage() {
  const router = useRouter();
  const [urls, setUrls] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState('');

  const handleBatchScrape = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setResults(null);
    setLoading(true);

    try {
      const urlList = urls.split('\n').filter(url => url.trim());
      const data = await api.scrapeBatch({ urls: urlList, respect_robots: true });
      setResults(data);
      setLoading(false);
    } catch (err) {
      setError('Operational failure: Unable to establish handshake with scrape engine.');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#02040a] text-slate-200 font-sans pb-20">
      {/* 1. Header Navigation */}
      <nav className="border-b border-white/5 bg-[#02040a]/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex justify-between items-center">
          <Link href="/dashboard" className="group flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-slate-500 hover:text-white transition">
            <svg className="w-4 h-4 group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Dashboard
          </Link>
          <div className="flex items-center gap-2">
             <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
             <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">Engine Online</span>
          </div>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto px-6 py-12">
        <header className="mb-10 text-center">
          <h1 className="text-4xl font-light text-white tracking-tight mb-2">Batch Matrix</h1>
          <p className="text-slate-500 text-sm">Deploy multi-threaded crawlers across target clusters.</p>
        </header>

        {/* 2. Input Section */}
        <div className="bg-[#0a0f1d]/60 border border-white/5 rounded-[2.5rem] p-8 shadow-2xl">
          <form onSubmit={handleBatchScrape} className="space-y-8">
            <div className="relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-emerald-500/20 to-blue-500/20 rounded-2xl blur opacity-25 group-focus-within:opacity-100 transition duration-1000"></div>
              <textarea
                id="urls"
                value={urls}
                onChange={(e) => setUrls(e.target.value)}
                className="relative w-full px-6 py-6 bg-[#02040a] border border-white/10 rounded-2xl text-emerald-400 font-mono text-sm placeholder-slate-700 focus:border-emerald-500/50 outline-none transition resize-none min-h-[280px]"
                placeholder="https://target-alpha.com&#10;https://target-beta.io&#10;https://cluster-01.net"
                required
              />
            </div>

            <div className="flex items-center justify-between">
                <div className="text-[10px] font-black uppercase tracking-widest text-slate-600">
                    Format: One URL per line
                </div>
                <button
                type="submit"
                disabled={loading}
                className="group px-10 py-4 bg-white text-black hover:bg-emerald-400 text-xs font-black uppercase tracking-[0.2em] rounded-full transition-all duration-300 disabled:opacity-20 flex items-center gap-3"
                >
                {loading ? (
                    <div className="w-4 h-4 border-2 border-black/20 border-t-black rounded-full animate-spin" />
                ) : 'Execute Sequence'}
                </button>
            </div>
          </form>

          {error && (
            <div className="mt-8 bg-red-500/5 border border-red-500/20 p-4 rounded-xl text-red-500 text-[10px] font-black uppercase tracking-widest flex items-center gap-3">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round"/></svg>
              {error}
            </div>
          )}
        </div>

        {/* 3. Real-time Results Stream */}
        {results && (
          <div className="mt-12 space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="flex justify-between items-end border-b border-white/5 pb-6">
              <div>
                <h3 className="text-xs font-black uppercase tracking-[0.3em] text-slate-500 mb-2">Live Execution Log</h3>
                <div className="flex items-center gap-4">
                  <span className="text-3xl font-light text-white">{results.successful}<span className="text-slate-700 mx-2">/</span>{results.total_urls}</span>
                  <span className="text-[10px] font-black uppercase tracking-widest text-emerald-500 bg-emerald-500/10 px-2 py-1 rounded">Success Rate: {Math.round((results.successful/results.total_urls)*100)}%</span>
                </div>
              </div>
              <button
                onClick={() => router.push(`/session/${results.session_id}`)}
                className="text-[10px] font-black uppercase tracking-widest text-purple-500 hover:text-white transition border-b border-purple-500/20 pb-1"
              >
                Deep Inspection →
              </button>
            </div>

            <div className="grid gap-3">
              {results.results?.map((result: any, index: number) => (
                <div
                  key={index}
                  className={`flex items-center justify-between p-4 bg-[#0a0f1d]/40 border rounded-xl transition-all ${
                    result.success ? 'border-white/5 hover:border-emerald-500/30' : 'border-red-500/10'
                  }`}
                >
                  <div className="flex items-center gap-4 flex-1 truncate">
                    <div className={`w-1.5 h-1.5 rounded-full ${result.success ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : 'bg-red-500 animate-pulse'}`} />
                    <span className="text-xs font-mono text-slate-400 truncate">{result.url}</span>
                  </div>
                  
                  <div className="flex items-center gap-6">
                    {result.success ? (
                      <div className="flex gap-4">
                         <span className="text-[9px] font-black text-slate-600 uppercase tracking-tighter">{result.word_count} WDS</span>
                         <span className="text-[9px] font-black text-slate-600 uppercase tracking-tighter">{result.char_count} CHR</span>
                      </div>
                    ) : (
                      <span className="text-[9px] font-black text-red-500/60 uppercase tracking-tighter">Handshake Failed</span>
                    )}
                    <div className={`text-[10px] font-bold ${result.success ? 'text-emerald-500' : 'text-red-500'}`}>
                      {result.success ? 'PASS' : 'FAIL'}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}