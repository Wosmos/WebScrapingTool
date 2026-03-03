import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-[#000000] text-white selection:bg-purple-500/50 overflow-x-hidden font-sans">
      {/* 1. STICKY NAV */}
      <nav className="fixed top-0 w-full z-[100] border-b border-white/10 bg-black/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 h-16 flex justify-between items-center">
          <div className="flex items-center gap-2 font-black text-xl tracking-tighter">
            <div className="w-6 h-6 bg-purple-600 rounded-sm rotate-45" />
            SCRAPER<span className="text-purple-500">PRO</span>
          </div>
          <div className="hidden md:flex gap-8 text-xs uppercase tracking-widest font-bold text-slate-400">
            <a href="#features" className="hover:text-purple-400 transition">Engine</a>
            <a href="#terminal" className="hover:text-purple-400 transition">API</a>
            <a href="#pricing" className="hover:text-purple-400 transition">Pricing</a>
          </div>
          <Link href="/login" className="text-xs font-black uppercase border-2 border-white px-5 py-2 hover:bg-white hover:text-black transition duration-300">
            Launch App
          </Link>
        </div>
      </nav>

      {/* 2. HERO SECTION */}
      <section className="relative pt-32 pb-20 px-6 border-b border-white/5">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="inline-block px-3 py-1 border border-purple-500/50 text-purple-400 text-[10px] font-bold uppercase tracking-widest mb-6">
                Enterprise Web Intelligence
              </div>
              <h1 className="text-7xl md:text-9xl font-black leading-[0.85] tracking-tighter mb-8">
                RAW <br /> DATA. <br /> <span className="text-purple-600">FAST.</span>
              </h1>
              <p className="text-slate-400 text-lg md:text-xl max-w-md leading-relaxed mb-10">
                The most aggressive web scraper on the market. Bypass 403s, solve CAPTCHAs, and scale to billions of rows.
              </p>
              <div className="flex gap-4">
                <button className="bg-purple-600 hover:bg-purple-500 text-white font-black px-8 py-4 rounded-full transition-all hover:scale-105">
                  START SCRAPING
                </button>
                <button className="border border-white/20 hover:bg-white/10 text-white font-black px-8 py-4 rounded-full transition">
                  DOCS
                </button>
              </div>
            </div>
            <div className="relative">
              <div className="aspect-square bg-gradient-to-tr from-purple-900/40 to-transparent rounded-[3rem] border border-white/10 p-8 relative overflow-hidden group">
                 <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] opacity-20"></div>
                 <div className="relative h-full border border-white/20 rounded-2xl bg-black/60 backdrop-blur-3xl p-6 flex flex-col justify-center">
                    <div className="flex gap-2 mb-4">
                        <div className="w-3 h-3 rounded-full bg-red-500" />
                        <div className="w-3 h-3 rounded-full bg-yellow-500" />
                        <div className="w-3 h-3 rounded-full bg-green-500" />
                    </div>
                    <code className="text-purple-400 text-sm leading-6">
                      <span className="text-slate-500">// Fetching Amazon pricing...</span><br/>
                      const data = await scraper.target('amazon')<br/>
                      &nbsp;&nbsp;.select('.price')<br/>
                      &nbsp;&nbsp;.proxy('ultra-high-res')<br/>
                      &nbsp;&nbsp;.execute();<br/>
                      <span className="text-green-400">Success: 1,402 items synced.</span>
                    </code>
                 </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 3. BENTO FEATURES */}
      <section id="features" className="py-24 px-6 max-w-7xl mx-auto">
        <h2 className="text-4xl font-black tracking-tighter mb-16 uppercase">The Infrastructure</h2>
        <div className="grid md:grid-cols-12 gap-4">
          <div className="md:col-span-8 h-[300px] bg-[#111] border border-white/10 rounded-[2.5rem] p-10 hover:border-purple-500 transition group relative overflow-hidden">
            <h3 className="text-3xl font-black mb-4 group-hover:text-purple-500 transition">Global Proxy Mesh</h3>
            <p className="text-slate-400 max-w-sm">Access 50M+ residential IPs in 190 countries. Zero latency, zero bans.</p>
            <div className="absolute bottom-0 right-0 p-8 opacity-10 group-hover:opacity-30 transition">
                <svg className="w-32 h-32" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>
            </div>
          </div>
          <div className="md:col-span-4 h-[300px] bg-purple-600 rounded-[2.5rem] p-10 flex flex-col justify-end shadow-[0_0_50px_-12px_rgba(168,85,247,0.5)]">
            <h3 className="text-3xl font-black leading-none mb-2">99.9% Uptime</h3>
            <p className="font-bold text-purple-200">Battle-tested reliability.</p>
          </div>
          <div className="md:col-span-4 h-[300px] bg-[#111] border border-white/10 rounded-[2.5rem] p-10">
            <h3 className="text-2xl font-black mb-4">JS Rendering</h3>
            <p className="text-slate-400">Headless Chrome support for SPA and dynamic content.</p>
          </div>
          <div className="md:col-span-8 h-[300px] bg-gradient-to-r from-slate-900 to-black border border-white/10 rounded-[2.5rem] p-10 flex items-center justify-between">
            <div>
                <h3 className="text-2xl font-black mb-2">Automated CAPTCHA</h3>
                <p className="text-slate-400">AI-powered solvers for hCaptcha, ReCaptcha, and Cloudflare.</p>
            </div>
            <div className="hidden sm:block w-32 h-32 bg-white/5 rounded-full animate-pulse border border-white/10"></div>
          </div>
        </div>
      </section>

      {/* 4. LIVE API TERMINAL SECTION */}
      <section id="terminal" className="py-24 bg-[#0a0a0a] border-y border-white/5">
        <div className="max-w-7xl mx-auto px-6 text-center">
            <h2 className="text-5xl font-black tracking-tighter mb-12 uppercase">Dev-First Experience</h2>
            <div className="max-w-4xl mx-auto bg-black border border-white/20 rounded-xl overflow-hidden text-left shadow-2xl">
                <div className="bg-white/5 px-4 py-2 flex items-center gap-2 border-b border-white/10">
                    <div className="w-2 h-2 rounded-full bg-red-500" />
                    <span className="text-[10px] text-slate-500 font-mono font-bold uppercase tracking-widest">bash — 80x24</span>
                </div>
                <div className="p-6 font-mono text-sm sm:text-base leading-7">
                    <p className="text-slate-500">$ curl -X POST https://api.scraperpro.com/v1/extract \</p>
                    <p className="text-purple-400">&nbsp;&nbsp;-H "Authorization: Bearer $API_KEY" \</p>
                    <p className="text-purple-400">&nbsp;&nbsp;-d '&#123;"url": "https://example.com", "stealth": true&#125;'</p>
                    <p className="text-white mt-4 animate-pulse">_</p>
                </div>
            </div>
        </div>
      </section>

      {/* 5. PRICING SECTION */}
      <section id="pricing" className="py-24 px-6 max-w-7xl mx-auto">
        <div className="text-center mb-16">
            <h2 className="text-5xl font-black uppercase tracking-tighter">Scale your data</h2>
            <p className="text-slate-400 mt-4">Transparent pricing for every stage of growth.</p>
        </div>
        <div className="grid md:grid-cols-3 gap-8">
            {[
                { name: 'Starter', price: '$0', desc: 'Perfect for small projects' },
                { name: 'Growth', price: '$99', desc: 'For scaling businesses', popular: true },
                { name: 'Enterprise', price: 'Custom', desc: 'High-volume infrastructure' }
            ].map((plan, i) => (
                <div key={i} className={`p-10 rounded-[2.5rem] border ${plan.popular ? 'border-purple-600 bg-purple-600/5' : 'border-white/10 bg-[#111]'} relative overflow-hidden`}>
                    {plan.popular && <span className="absolute top-6 right-6 bg-purple-600 text-[10px] font-black px-3 py-1 rounded-full uppercase">Most Popular</span>}
                    <h3 className="text-xl font-black uppercase mb-2">{plan.name}</h3>
                    <div className="text-5xl font-black mb-4">{plan.price}<span className="text-sm font-normal text-slate-500">/mo</span></div>
                    <p className="text-slate-400 text-sm mb-8">{plan.desc}</p>
                    <button className={`w-full py-4 rounded-xl font-black transition ${plan.popular ? 'bg-purple-600 hover:bg-purple-500' : 'bg-white text-black hover:bg-slate-200'}`}>
                        GET STARTED
                    </button>
                </div>
            ))}
        </div>
      </section>

      {/* 6. CTA / FOOTER */}
      <footer className="bg-white text-black pt-20 pb-10 px-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-start md:items-center gap-10">
          <div>
            <h2 className="text-6xl md:text-8xl font-black tracking-tighter leading-none mb-4 uppercase">Let's <br /> Dig.</h2>
            <p className="font-bold text-slate-500 uppercase tracking-widest text-xs">Ready to own the web?</p>
          </div>
          <div className="flex flex-col items-end gap-4 w-full md:w-auto">
            <button className="w-full md:w-auto px-10 py-5 bg-black text-white font-black hover:scale-105 transition">CREATE FREE ACCOUNT</button>
            <div className="flex gap-6 font-black text-[10px] uppercase">
                <a href="#" className="hover:underline">Github</a>
                <a href="#" className="hover:underline">Twitter</a>
                <a href="#" className="hover:underline">Status</a>
            </div>
          </div>
        </div>
        <div className="max-w-7xl mx-auto mt-20 pt-10 border-t border-black/10 text-[10px] font-black uppercase tracking-widest text-slate-400">
            © 2026 SCRAPERPRO CORP. SYSTEMS OPERATIONAL.
        </div>
      </footer>
    </div>
  );
}