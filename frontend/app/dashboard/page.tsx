'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
// import { api } from '@/lib/api';
import Link from 'next/link';

export default function DashboardPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const fetchData = async () => {
      try {
        // const result = await api.getDashboard();
        // setData(result);
        
        // Mocking data for design preview
        setTimeout(() => {
          setData({
            user: { username: 'DigitalAlchemist' },
            recent_sessions: [
              { id: '102', name: 'Product Catalog Alpha', total_urls: 150, created_at: new Date().toISOString() },
              { id: '101', name: 'Competitor Pricing', total_urls: 12, created_at: new Date().toISOString() }
            ]
          });
          setLoading(false);
        }, 800);
      } catch (error) {
        router.push('/login');
      }
    };

    fetchData();
  }, [router]);

  const handleLogout = async () => {
    // await api.logout();
    router.push('/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#02040a] flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-10 w-10 border-2 border-white/10 border-t-purple-500 mb-4"></div>
          <p className="text-slate-500 text-[10px] uppercase tracking-[0.3em] font-bold">Initializing Interface</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#02040a] text-slate-200 font-sans">
      {/* 1. Sleek Navigation */}
      <nav className="border-b border-white/5 bg-[#02040a]/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-20 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-blue-600 rounded-xl flex items-center justify-center shadow-[0_0_15px_rgba(147,51,234,0.3)]">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <span className="text-xl font-light tracking-tighter text-white">Console<span className="font-bold text-purple-500">.</span></span>
          </div>
          
          <div className="flex items-center gap-6">
            <div className="hidden md:block text-right">
              <p className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Operator</p>
              <p className="text-sm font-medium text-white">{data?.user?.username}</p>
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 border border-white/5 bg-white/5 hover:bg-red-500/10 hover:border-red-500/20 hover:text-red-400 text-slate-400 text-xs font-bold uppercase tracking-widest rounded-lg transition-all"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-12">
        <header className="mb-12">
          <h1 className="text-4xl font-light text-white tracking-tight">Command Center</h1>
          <p className="text-slate-500 mt-2 text-sm">Select a module to begin data extraction.</p>
        </header>

        {/* 2. Quick Actions: Modular Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
          {[
            { 
              title: 'Single Node', 
              desc: 'Extract content from a specific URL target.', 
              href: '/scraper', 
              icon: 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z',
              color: 'group-hover:text-blue-400'
            },
            { 
              title: 'Batch Matrix', 
              desc: 'Execute multi-threaded extraction sequences.', 
              href: '/batch', 
              icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10',
              color: 'group-hover:text-emerald-400'
            },
            { 
              title: 'Neural History', 
              desc: 'Review past session logs and datasets.', 
              href: '/history', 
              icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
              color: 'group-hover:text-purple-400'
            },
          ].map((action, i) => (
            <Link key={i} href={action.href} className="group relative bg-[#0a0f1d]/40 border border-white/5 p-8 rounded-[2rem] hover:bg-[#0a0f1d]/80 hover:border-white/10 transition-all duration-500 overflow-hidden">
              <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
                 <svg className="w-24 h-24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={action.icon} />
                </svg>
              </div>
              <div className="relative z-10">
                <div className="w-12 h-12 bg-white/5 rounded-xl flex items-center justify-center mb-6 border border-white/10 group-hover:border-white/20 transition-all">
                  <svg className={`w-6 h-6 text-slate-400 ${action.color} transition-colors`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={action.icon} />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-white mb-2">{action.title}</h3>
                <p className="text-slate-500 text-sm leading-relaxed mb-6">{action.desc}</p>
                <span className={`text-[10px] font-black uppercase tracking-widest ${action.color} transition-colors`}>Initialize Component →</span>
              </div>
            </Link>
          ))}
        </div>

        {/* 3. Recent Sessions Table-Style */}
        <section className="bg-[#0a0f1d]/60 backdrop-blur-2xl rounded-[2.5rem] border border-white/5 overflow-hidden shadow-2xl">
          <div className="p-8 border-b border-white/5 flex justify-between items-center bg-white/[0.02]">
            <h2 className="text-sm font-bold uppercase tracking-[0.2em] text-slate-400">Recent Operational Logs</h2>
            <Link href="/history" className="text-[10px] font-black uppercase tracking-widest text-purple-500 hover:text-purple-400 transition">
              View Full Archive
            </Link>
          </div>
          
          <div className="divide-y divide-white/5">
            {data?.recent_sessions?.length > 0 ? (
              data.recent_sessions.map((session: any) => (
                <div key={session.id} className="p-6 hover:bg-white/[0.02] transition-colors group flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="flex-1">
                    <h3 className="text-white font-medium group-hover:text-purple-400 transition">{session.name}</h3>
                    <div className="flex items-center gap-6 mt-2">
                      <span className="text-[10px] text-slate-600 flex items-center gap-1.5 uppercase font-bold tracking-wider">
                        <div className="w-1 h-1 rounded-full bg-slate-700" />
                        {session.total_urls} Targets
                      </span>
                      <span className="text-[10px] text-slate-600 flex items-center gap-1.5 uppercase font-bold tracking-wider">
                        <div className="w-1 h-1 rounded-full bg-slate-700" />
                        {new Date(session.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="px-3 py-1 bg-emerald-500/5 border border-emerald-500/20 text-emerald-500 text-[10px] font-black uppercase tracking-widest rounded-full">
                      Stored
                    </span>
                    <Link href={`/session/${session.id}`} className="p-2 text-slate-600 hover:text-white transition">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </Link>
                  </div>
                </div>
              ))
            ) : (
              <div className="py-20 text-center">
                <p className="text-slate-600 text-xs font-bold uppercase tracking-widest italic">No active logs detected in the current cycle.</p>
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}