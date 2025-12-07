import { useNavigate } from 'react-router-dom';

function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-sm bg-slate-900/50">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <h1 className="text-xl font-bold">Saarathi AI</h1>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1 flex items-center justify-center px-4 py-12">
        <div className="max-w-4xl mx-auto text-center">
          {/* Main Headline */}
          <h2 className="text-5xl md:text-6xl lg:text-7xl font-bold mb-6 leading-tight">
            Saarathi AI: Welfare Schemes{' '}
            <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              Made Understandable
            </span>
          </h2>

          {/* Subtext */}
          <p className="text-xl md:text-2xl text-slate-300 mb-12 max-w-3xl mx-auto">
            Helping every citizen discover and apply for the benefits they are eligible for.
          </p>

          {/* Value Pillars */}
          <div className="grid md:grid-cols-3 gap-6 mb-12 max-w-3xl mx-auto">
            <div className="backdrop-blur-sm bg-white/5 rounded-2xl p-6 border border-white/10">
              <div className="text-3xl mb-3">✔</div>
              <h3 className="font-semibold text-lg mb-2">Simple eligibility matching</h3>
              <p className="text-sm text-slate-400">
                Answer a few questions and discover schemes tailored to you
              </p>
            </div>

            <div className="backdrop-blur-sm bg-white/5 rounded-2xl p-6 border border-white/10">
              <div className="text-3xl mb-3">✔</div>
              <h3 className="font-semibold text-lg mb-2">Clear application steps</h3>
              <p className="text-sm text-slate-400">
                Get step-by-step guidance on how to apply for each scheme
              </p>
            </div>

            <div className="backdrop-blur-sm bg-white/5 rounded-2xl p-6 border border-white/10">
              <div className="text-3xl mb-3">✔</div>
              <h3 className="font-semibold text-lg mb-2">Voice-friendly assistance</h3>
              <p className="text-sm text-slate-400">
                Chat with our AI assistant to understand schemes better
              </p>
            </div>
          </div>

          {/* CTA Button */}
          <button
            onClick={() => navigate('/app')}
            className="group relative inline-flex items-center gap-3 px-8 py-4 text-lg font-semibold rounded-2xl bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 transition-all duration-300 shadow-lg hover:shadow-xl hover:scale-105"
          >
            <span>Enter Saarathi AI</span>
            <svg 
              className="w-5 h-5 group-hover:translate-x-1 transition-transform" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </button>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 backdrop-blur-sm bg-slate-900/50">
        <div className="max-w-6xl mx-auto px-4 py-6 text-center">
          <p className="text-sm text-slate-400">
            Making government schemes accessible to all citizens
          </p>
        </div>
      </footer>
    </div>
  );
}

export default LandingPage;
