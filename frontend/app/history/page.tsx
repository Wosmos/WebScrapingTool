'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import Link from 'next/link';

export default function HistoryPage() {
  const [sessions, setSessions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const data = await api.getSessions();
        setSessions(data.sessions || []);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch sessions');
        setLoading(false);
      }
    };

    fetchSessions();
  }, []);

  return (
    <div className="min-h-screen bg-[#02040a] text-slate-200 font-sans">
      {/* 1. Consistent Navigation */}
      <nav className="border-b border-white/5 bg-[#02040a]/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex justify-between items-center">
          <Link href="/dashboard" className="group flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-slate-500 hover:text-white transition">
            <svg className="w-4 h-4 group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Dashboard
          </Link>
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-blue-500 shadow-[0_0_8px_#3b82f6]" />
            <span className="text-sm font-medium text-white tracking-tight">Scraping History</span>
          </div>
          <div className="w-20" /> 
        </div>
      </nav>

      <main className="max-w-5xl mx-auto px-6 py-12">
        <div className="flex justify-between items-end mb-10">
          <div>
            <h1 className="text-4xl font-light text-white tracking-tight mb-2">Archive</h1>
            <p className="text-slate-500 text-[10px] uppercase tracking-[0.2em] font-bold">Total Sessions: {sessions.length}</p>
          </div>
          <Link href="/scraper" className="px-6 py-2.5 bg-white text-black text-xs font-black uppercase rounded-lg hover:bg-slate-200 transition">
            New Extraction
          </Link>
        </div>

        {/* 2. History Content */}
        <div className="space-y-4">
          {loading ? (
            <div className="bg-[#0a0f1d]/60 border border-white/5 rounded-[2rem] p-20 text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-2 border-white/10 border-t-purple-500 mb-4"></div>
              <p className="text-slate-500 text-xs font-bold uppercase tracking-widest">Synchronizing History...</p>
            </div>
          ) : sessions.length > 0 ? (
            sessions.map((session: any) => (
              <Link 
                href={`/session/${session.id}`} 
                key={session.id} 
                className="block bg-[#0a0f1d]/40 border border-white/5 rounded-2xl p-6 hover:border-purple-500/40 hover:bg-[#0a0f1d]/80 transition-all group relative overflow-hidden"
              >
                {/* Subtle highlight bar on hover */}
                <div className="absolute left-0 top-0 bottom-0 w-1 bg-purple-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                  <div className="space-y-1">
                    <div className="flex items-center gap-3">
                      <h3 className="text-lg font-medium text-white group-hover:text-purple-400 transition">{session.name}</h3>
                      <span className="text-[10px] font-mono px-2 py-0.5 bg-white/5 border border-white/10 rounded text-slate-500">
                        #{session.id}
                      </span>
                    </div>
                    
                    <div className="flex flex-wrap gap-6 pt-2">
                      <div className="flex items-center gap-2 text-slate-500">
                        <svg className="w-4 h-4 text-purple-500/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                        </svg>
                        <span className="text-xs italic"><span className="text-slate-300 font-bold">{session.total_urls}</span> Target Nodes</span>
                      </div>
                      <div className="flex items-center gap-2 text-slate-500">
                        <svg className="w-4 h-4 text-purple-500/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span className="text-xs uppercase tracking-tighter">{new Date(session.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 w-full md:w-auto border-t md:border-t-0 border-white/5 pt-4 md:pt-0">
                    {session.completed_at ? (
                      <span className="text-[10px] font-black uppercase tracking-widest text-emerald-500 bg-emerald-500/10 px-3 py-1.5 rounded-full border border-emerald-500/20">
                        Success
                      </span>
                    ) : (
                      <span className="text-[10px] font-black uppercase tracking-widest text-amber-500 bg-amber-500/10 px-3 py-1.5 rounded-full border border-amber-500/20 animate-pulse">
                        In Progress
                      </span>
                    )}
                    <svg className="w-5 h-5 text-slate-700 group-hover:text-white group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              </Link>
            ))
          ) : (
            /* Empty State */
            <div className="bg-[#0a0f1d]/40 border border-white/5 rounded-[2rem] p-20 text-center">
              <div className="w-16 h-16 bg-white/5 rounded-2xl flex items-center justify-center mx-auto mb-6 border border-white/10">
                <svg className="w-8 h-8 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-xl font-light text-white mb-2">Zero Records Found</h3>
              <p className="text-slate-500 text-sm mb-8">Your extraction archive is currently empty.</p>
              <Link href="/scraper" className="inline-block px-8 py-3 bg-purple-600 text-white text-xs font-black uppercase rounded-xl hover:bg-purple-500 transition shadow-lg shadow-purple-900/20">
                Initialize First Scrape
              </Link>
            </div>
          )}
        </div>
      </main>

      {/* Decorative Branding */}
      <footer className="max-w-5xl mx-auto px-6 py-12 border-t border-white/5 text-center">
         <p className="text-[10px] text-slate-700 uppercase tracking-[0.5em] font-black">
          ScraperPro Engine v2.0.4 — Records encrypted
        </p>
      </footer>
    </div>
  );
}