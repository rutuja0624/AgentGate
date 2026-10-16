import React from 'react';
import { ShieldCheck, GitPullRequest, Activity, Database, CheckCircle2, Terminal } from 'lucide-react';

export const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Navigation Header */}
      <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-violet-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <ShieldCheck className="h-6 w-6 text-white" />
            </div>
            <div>
              <span className="font-bold text-xl tracking-tight text-white">AgentGate</span>
              <span className="ml-2 text-xs px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                Phase 0 Verified
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <CheckCircle2 className="w-3.5 h-3.5" />
              Gateway & Engine Online
            </span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-10 space-y-8">
        {/* Hero Section */}
        <div className="rounded-2xl border border-slate-800 bg-gradient-to-b from-slate-900/80 to-slate-900/20 p-8 shadow-xl">
          <h1 className="text-3xl font-extrabold text-white tracking-tight sm:text-4xl">
            Verification Gate for Pull Requests
          </h1>
          <p className="mt-3 text-base text-slate-400 max-w-3xl leading-relaxed">
            Multi-stage autonomous PR verification powered by code-graph dependency analysis,
            deterministic AST security scanners, sandboxed test execution inside network-less Docker containers,
            and specialized LLM reviewer agents.
          </p>

          <div className="mt-6 flex flex-wrap gap-3">
            <div className="flex items-center space-x-2 text-xs bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700/50">
              <Activity className="w-4 h-4 text-indigo-400" />
              <span className="text-slate-300">FastAPI Python 3.12 Engine</span>
            </div>
            <div className="flex items-center space-x-2 text-xs bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700/50">
              <Terminal className="w-4 h-4 text-violet-400" />
              <span className="text-slate-300">Spring Boot 3.3 Gateway</span>
            </div>
            <div className="flex items-center space-x-2 text-xs bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700/50">
              <Database className="w-4 h-4 text-emerald-400" />
              <span className="text-slate-300">PostgreSQL 16 + Redis 7</span>
            </div>
          </div>
        </div>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="rounded-xl border border-slate-800/80 bg-slate-900/40 p-6 space-y-3">
            <div className="w-10 h-10 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
              <GitPullRequest className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-lg text-white">Pull Request Pipeline</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Ingests GitHub pull requests, builds reverse-dependency blast-radius graphs, runs Semgrep & Radon, and executes tests in isolated sandboxes.
            </p>
          </div>

          <div className="rounded-xl border border-slate-800/80 bg-slate-900/40 p-6 space-y-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-lg text-white">Evidence-Backed Risk</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Produces a verified 0–100 merge risk score where findings are classified with cryptographic certainty and test confirmation before review.
            </p>
          </div>

          <div className="rounded-xl border border-slate-800/80 bg-slate-900/40 p-6 space-y-3">
            <div className="w-10 h-10 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
              <Activity className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-lg text-white">Empirical Benchmark</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Monitors and compares precision, recall, and false-positive rates across LLM-only, LLM-static, and full sandboxed execution pipelines.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 py-6 text-center text-xs text-slate-500">
        AgentGate System Foundation • Capgemini Software Engineering Portfolio
      </footer>
    </div>
  );
};

export default App;
