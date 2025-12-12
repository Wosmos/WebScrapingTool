'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { api } from '@/lib/api';
import Link from 'next/link';

export default function SessionDetailPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = parseInt(params.id as string);
  
  const [sessionData, setSessionData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await api.getSessionData(sessionId);
        setSessionData(data);
      } catch (error) {
        console.error('Failed to fetch session data');
        router.push('/history');
      } finally {
        setLoading(false);
      }
    };

    if (sessionId) {
      fetchData();
    }
  }, [sessionId, router]);

  const handleExport = async (format: 'csv' | 'excel' | 'pdf') => {
    setExporting(format);
    try {
      await api.exportSession(sessionId, format);
    } catch (error) {
      alert('Export failed. Please try again.');
    } finally {
      setExporting(null);
    }
  };

  const handleDelete = async () => {
    if (confirm('Are you sure you want to delete this session?')) {
      try {
        await api.deleteSession(sessionId);
        router.push('/history');
      } catch (error) {
        alert('Failed to delete session');
      }
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-purple-500 mb-4"></div>
          <p className="text-white text-xl">Loading session...</p>
        </div>
      </div>
    );
  }

  if (!sessionData) {
    return null;
  }

  const { session, data } = sessionData;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Navigation */}
      <nav className="bg-white/5 backdrop-blur-xl border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex justify-between h-20 items-center">
            <Link href="/history" className="flex items-center gap-3 text-white hover:text-purple-300 transition">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              <span className="text-xl font-semibold">Back to History</span>
            </Link>
            <div className="flex items-center gap-3">
              <span className="text-2xl font-bold text-white">Session #{session.id}</span>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-12">
        {/* Session Info Card */}
        <div className="bg-white/5 backdrop-blur-xl rounded-3xl border border-white/10 p-8 mb-8">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h1 className="text-3xl font-bold text-white mb-4">{session.name}</h1>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <div>
                  <p className="text-purple-300 text-sm mb-1">Total URLs</p>
                  <p className="text-2xl font-bold text-white">{session.total_urls}</p>
                </div>
                <div>
                  <p className="text-purple-300 text-sm mb-1">Completed</p>
                  <p className="text-2xl font-bold text-green-400">{session.completed_urls}</p>
                </div>
                <div>
                  <p className="text-purple-300 text-sm mb-1">Status</p>
                  <span className="inline-block px-3 py-1 bg-green-500/20 border border-green-500/50 text-green-300 rounded-lg text-sm font-medium">
                    {session.status}
                  </span>
                </div>
                <div>
                  <p className="text-purple-300 text-sm mb-1">Created</p>
                  <p className="text-white text-sm">{new Date(session.created_at).toLocaleString()}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Export Buttons */}
          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => handleExport('csv')}
              disabled={exporting === 'csv'}
              className="px-6 py-3 bg-blue-500/20 hover:bg-blue-500/30 border border-blue-500/50 text-blue-300 rounded-xl transition disabled:opacity-50 flex items-center gap-2"
            >
              {exporting === 'csv' ? (
                <>
                  <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Exporting...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Export CSV
                </>
              )}
            </button>

            <button
              onClick={() => handleExport('excel')}
              disabled={exporting === 'excel'}
              className="px-6 py-3 bg-green-500/20 hover:bg-green-500/30 border border-green-500/50 text-green-300 rounded-xl transition disabled:opacity-50 flex items-center gap-2"
            >
              {exporting === 'excel' ? (
                <>
                  <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Exporting...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Export Excel
                </>
              )}
            </button>

            <button
              onClick={() => handleExport('pdf')}
              disabled={exporting === 'pdf'}
              className="px-6 py-3 bg-purple-500/20 hover:bg-purple-500/30 border border-purple-500/50 text-purple-300 rounded-xl transition disabled:opacity-50 flex items-center gap-2"
            >
              {exporting === 'pdf' ? (
                <>
                  <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Exporting...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                  Export PDF
                </>
              )}
            </button>

            <button
              onClick={handleDelete}
              className="ml-auto px-6 py-3 bg-red-500/20 hover:bg-red-500/30 border border-red-500/50 text-red-300 rounded-xl transition flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              Delete Session
            </button>
          </div>
        </div>

        {/* Scraped Data */}
        <div className="bg-white/5 backdrop-blur-xl rounded-3xl border border-white/10 p-8">
          <h2 className="text-2xl font-bold text-white mb-6">Scraped Data</h2>
          
          {data && data.length > 0 ? (
            <div className="space-y-4">
              {data.map((item: any) => (
                <div key={item.id} className="bg-white/5 border border-white/10 rounded-2xl p-6 hover:bg-white/10 transition">
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-white mb-2 break-all">{item.url}</h3>
                      {item.title && (
                        <p className="text-purple-200 text-sm mb-2">{item.title}</p>
                      )}
                    </div>
                    <span className={`px-3 py-1 rounded-lg text-sm font-medium ${
                      item.status === 'success' 
                        ? 'bg-green-500/20 border border-green-500/50 text-green-300'
                        : 'bg-red-500/20 border border-red-500/50 text-red-300'
                    }`}>
                      {item.status}
                    </span>
                  </div>

                  <div className="grid grid-cols-3 gap-4 mb-4">
                    <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-3">
                      <p className="text-blue-200 text-xs mb-1">Words</p>
                      <p className="text-blue-300 text-xl font-bold">{item.word_count?.toLocaleString()}</p>
                    </div>
                    <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-3">
                      <p className="text-green-200 text-xs mb-1">Characters</p>
                      <p className="text-green-300 text-xl font-bold">{item.char_count?.toLocaleString()}</p>
                    </div>
                    <div className="bg-purple-500/10 border border-purple-500/30 rounded-xl p-3">
                      <p className="text-purple-200 text-xs mb-1">Scraped</p>
                      <p className="text-purple-300 text-sm font-semibold">{new Date(item.scraped_at).toLocaleTimeString()}</p>
                    </div>
                  </div>

                  {item.content && (
                    <details className="group">
                      <summary className="cursor-pointer text-purple-300 hover:text-purple-200 transition flex items-center gap-2">
                        <svg className="w-5 h-5 group-open:rotate-90 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                        View Content
                      </summary>
                      <div className="mt-4 bg-white/5 border border-white/10 rounded-xl p-4 max-h-64 overflow-y-auto">
                        <pre className="text-purple-100 text-sm whitespace-pre-wrap">{item.content}</pre>
                      </div>
                    </details>
                  )}

                  {item.error_message && (
                    <div className="mt-4 bg-red-500/10 border border-red-500/30 rounded-xl p-3">
                      <p className="text-red-300 text-sm">{item.error_message}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-purple-200 text-center py-8">No data available</p>
          )}
        </div>
      </main>
    </div>
  );
}
