'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { api } from '@/lib/api';
import Link from 'next/link';

export default function SessionDetailPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.id as string;
  
  const [sessionData, setSessionData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await api.getSessionData(Number(sessionId));
        setSessionData(data);
        setLoading(false);
      } catch (error) {
        router.push('/history');
      }
    };
    fetchData();
  }, [sessionId, router]);

  const handleExport = async (format: 'csv' | 'excel' | 'pdf') => {
    setExporting(format);
    try {
      await api.exportSession(Number(sessionId), format);
    } finally {
      setExporting(null);
    }
  };

  if (loading) return (
    <div className="min-h-screen bg-[#02040a] flex items-center justify-center">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-2 border-white/10 border-t-purple-500 mb-4"></div>
        <p className="text-slate-500 text-[10px] uppercase tracking-[0.3em] font-black">Parsing Session Data</p>
      </div>
    </div>
  );

  const { session, data } = sessionData;

  return (
    <div className="min-h-screen bg-[#02040a] text-slate-200 font-sans pb-20">
      {/* 1. Header Navigation */}
      <nav className="border-b border-white/5 bg-[#02040a]/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex justify-between items-center">
          <Link href="/history" className="group flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-slate-500 hover:text-white transition">
            <svg className="w-4 h-4 group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            History Archive
          </Link>
          <div className="text-[10px] font-mono text-slate-500 bg-white/5 px-3 py-1 rounded border border-white/10">
            ID: {session.id}
          </div>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-6 py-12">
        {/* 2. Meta Stats Ribbon */}
        <div className="bg-[#0a0f1d]/60 border border-white/5 rounded-[2rem] p-8 mb-8 relative overflow-hidden">
          <div className="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-end gap-8">
            <div className="space-y-2">
              <h1 className="text-4xl font-light text-white tracking-tight">{session.name}</h1>
              <p className="text-slate-500 text-xs font-medium italic">{new Date(session.created_at).toLocaleString()}</p>
            </div>
            
            <div className="flex gap-8 border-l border-white/5 pl-8">
              <div>
                <p className="text-[10px] uppercase tracking-widest text-slate-500 font-black mb-1">Queue</p>
                <p className="text-2xl font-light text-white">{session.total_urls}</p>
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-widest text-slate-500 font-black mb-1">Processed</p>
                <p className="text-2xl font-light text-emerald-500">{session.completed_urls}</p>
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-widest text-slate-500 font-black mb-1">Status</p>
                <span className="text-[10px] font-black uppercase tracking-tighter px-2 py-1 bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 rounded">
                  {session.status}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* 3. Global Actions */}
        <div className="flex flex-wrap items-center gap-3 mb-12">
          {['csv', 'excel', 'pdf'].map((fmt) => (
            <button
              key={fmt}
              onClick={() => handleExport(fmt as any)}
              disabled={!!exporting}
              className="px-5 py-2.5 bg-white/5 border border-white/10 hover:border-purple-500/50 text-slate-300 text-[10px] font-black uppercase tracking-widest rounded-xl transition flex items-center gap-2 disabled:opacity-30"
            >
              {exporting === fmt ? <div className="w-3 h-3 border-2 border-t-transparent border-white rounded-full animate-spin" /> : 
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round"/></svg>}
              Export {fmt}
            </button>
          ))}
          
          <button className="ml-auto group px-5 py-2.5 border border-red-500/20 text-red-500/50 hover:text-red-500 hover:bg-red-500/5 text-[10px] font-black uppercase tracking-widest rounded-xl transition flex items-center gap-2">
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round"/></svg>
            Purge Session
          </button>
        </div>

        {/* 4. Scraped Data Nodes */}
        <div className="space-y-4">
          <h2 className="text-sm font-bold uppercase tracking-[0.3em] text-slate-500 mb-6 flex items-center gap-3">
            Extracted Payloads
            <div className="h-px bg-white/5 flex-1" />
          </h2>
          
          {data.map((item: any) => (
            <div key={item.id} className="bg-[#0a0f1d]/40 border border-white/5 rounded-2xl overflow-hidden">
              <div className="p-6 flex flex-col md:flex-row justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className={`w-2 h-2 rounded-full ${item.status === 'success' ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : 'bg-red-500 shadow-[0_0_8px_#ef4444]'}`} />
                    <h3 className="text-sm font-mono text-purple-400 truncate max-w-md">{item.url}</h3>
                  </div>
                  <p className="text-white font-medium text-lg">{item.title || 'No Title Detected'}</p>
                </div>
                
                <div className="flex items-center gap-4">
                  <div className="text-right hidden sm:block">
                    <p className="text-[10px] text-slate-600 font-black uppercase">{item.word_count || 0} Words</p>
                    <p className="text-[10px] text-slate-600 font-black uppercase">{item.char_count || 0} Chars</p>
                  </div>
                  <div className="h-10 w-px bg-white/5" />
                  <p className="text-[10px] font-mono text-slate-500">{new Date(item.scraped_at).toLocaleTimeString()}</p>
                </div>
              </div>

              {item.status === 'success' ? (
                <details className="group border-t border-white/5">
                  <summary className="px-6 py-3 cursor-pointer text-[10px] font-black uppercase tracking-widest text-slate-500 hover:bg-white/[0.02] transition list-none flex items-center justify-between">
                    Raw Payload Inspection
                    <svg className="w-4 h-4 group-open:rotate-180 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M19 9l-7 7-7-7" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round"/></svg>
                  </summary>
                  <div className="p-6 bg-black/40">
                    <pre className="text-xs font-mono text-slate-400 leading-relaxed whitespace-pre-wrap selection:bg-purple-500/30">
                      {item.content}
                    </pre>
                  </div>
                </details>
              ) : (
                <div className="px-6 py-4 bg-red-500/5 border-t border-red-500/10">
                  <p className="text-xs font-mono text-red-400">LOG_ERROR: {item.error_message}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}