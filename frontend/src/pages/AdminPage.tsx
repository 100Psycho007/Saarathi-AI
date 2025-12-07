import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Scheme } from '../types';
import { API_BASE_URL } from '../config';
import { useAuth } from '../contexts/AuthContext';

interface AdminStats {
  totalSchemes: number;
  schemesByState: Record<string, number>;
  schemesByCategory: Record<string, number>;
}

interface AIExtractionResult {
  scheme_id: number;
  scheme_name: string;
  status: string;
  extracted?: any;
  reason?: string;
}

function AdminPage() {
  const { logout, getAuthHeaders } = useAuth();
  const [schemes, setSchemes] = useState<Scheme[]>([]);
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [aiExtracting, setAiExtracting] = useState(false);
  const [syncState, setSyncState] = useState('');
  const [syncing, setSyncing] = useState(false);
  const [extractionResults, setExtractionResults] = useState<AIExtractionResult[]>([]);
  const [timeLeft, setTimeLeft] = useState<number>(0);

  // Token expiration countdown
  useEffect(() => {
    const updateTimeLeft = () => {
      const expires = localStorage.getItem('admin_token_expires');
      if (expires) {
        const remaining = Math.max(0, parseInt(expires) - Date.now());
        setTimeLeft(Math.floor(remaining / 1000));
      }
    };

    updateTimeLeft();
    const interval = setInterval(updateTimeLeft, 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    loadSchemes();
  }, []);

  const loadSchemes = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/schemes/`);
      const data = await response.json();
      setSchemes(data);
      
      // Calculate stats
      const stats: AdminStats = {
        totalSchemes: data.length,
        schemesByState: {},
        schemesByCategory: {}
      };
      
      data.forEach((scheme: Scheme) => {
        stats.schemesByState[scheme.state] = (stats.schemesByState[scheme.state] || 0) + 1;
        stats.schemesByCategory[scheme.category] = (stats.schemesByCategory[scheme.category] || 0) + 1;
      });
      
      setStats(stats);
    } catch (error) {
      console.error('Failed to load schemes:', error);
    } finally {
      setLoading(false);
    }
  };

  const runAIExtraction = async () => {
    setAiExtracting(true);
    setExtractionResults([]);
    try {
      const response = await fetch(`${API_BASE_URL}/admin/ai/extract-eligibility-batch?limit=10`, {
        method: 'POST',
        headers: getAuthHeaders(),
      });
      const data = await response.json();
      
      if (data.results) {
        setExtractionResults(data.results);
      }
      
      // Reload schemes to see updated data
      await loadSchemes();
    } catch (error) {
      console.error('AI extraction failed:', error);
    } finally {
      setAiExtracting(false);
    }
  };

  const syncMySchemeData = async () => {
    if (!syncState.trim()) return;
    
    setSyncing(true);
    try {
      const response = await fetch(`${API_BASE_URL}/admin/sync/myscheme?state=${encodeURIComponent(syncState)}`, {
        method: 'POST',
        headers: getAuthHeaders(),
      });
      const data = await response.json();
      
      alert(`Sync completed: ${data.inserted} inserted, ${data.updated} updated`);
      await loadSchemes();
      setSyncState('');
    } catch (error) {
      console.error('Sync failed:', error);
      alert('Sync failed. Check console for details.');
    } finally {
      setSyncing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-sm bg-slate-900/50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link to="/" className="text-blue-400 hover:text-blue-300 transition-colors">
              ← Back to App
            </Link>
            <h1 className="text-xl font-bold">Admin Dashboard</h1>
            <span className="px-2 py-1 text-xs font-medium bg-red-500/20 text-red-300 rounded-full border border-red-500/30">
              Admin Only
            </span>
          </div>
          <div className="flex items-center gap-4">
            {timeLeft > 0 && (
              <div className={`px-3 py-1.5 text-xs rounded-full border ${
                timeLeft < 60 
                  ? 'bg-red-500/20 text-red-300 border-red-500/30' 
                  : 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30'
              }`}>
                Session: {Math.floor(timeLeft / 60)}:{(timeLeft % 60).toString().padStart(2, '0')}
              </div>
            )}
            <button
              onClick={logout}
              className="px-4 py-2 text-sm bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6">
              <h3 className="text-lg font-semibold mb-2">Total Schemes</h3>
              <p className="text-3xl font-bold text-blue-400">{stats.totalSchemes}</p>
            </div>
            
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6">
              <h3 className="text-lg font-semibold mb-2">States Covered</h3>
              <p className="text-3xl font-bold text-green-400">{Object.keys(stats.schemesByState).length}</p>
            </div>
            
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6">
              <h3 className="text-lg font-semibold mb-2">Categories</h3>
              <p className="text-3xl font-bold text-purple-400">{Object.keys(stats.schemesByCategory).length}</p>
            </div>
          </div>
        )}

        {/* Admin Actions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* AI Extraction */}
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6">
            <h3 className="text-xl font-semibold mb-4">AI Eligibility Extraction</h3>
            <p className="text-slate-300 mb-4">
              Use AI to automatically extract eligibility criteria from scheme descriptions.
            </p>
            <button
              onClick={runAIExtraction}
              disabled={aiExtracting}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:opacity-50 text-white px-4 py-2 rounded-lg transition-colors"
            >
              {aiExtracting ? 'Extracting...' : 'Run AI Extraction (Batch)'}
            </button>
            
            {extractionResults.length > 0 && (
              <div className="mt-4 max-h-40 overflow-y-auto">
                <h4 className="font-medium mb-2">Extraction Results:</h4>
                {extractionResults.map((result, idx) => (
                  <div key={idx} className="text-sm mb-1">
                    <span className={`inline-block w-2 h-2 rounded-full mr-2 ${
                      result.status === 'success' ? 'bg-green-400' : 
                      result.status === 'error' ? 'bg-red-400' : 'bg-yellow-400'
                    }`}></span>
                    {result.scheme_name} - {result.status}
                    {result.reason && <span className="text-slate-400"> ({result.reason})</span>}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Data Sync */}
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6">
            <h3 className="text-xl font-semibold mb-4">Data Synchronization</h3>
            <p className="text-slate-300 mb-4">
              Sync schemes from external data sources like myScheme.
            </p>
            <div className="flex gap-2 mb-4">
              <input
                type="text"
                value={syncState}
                onChange={(e) => setSyncState(e.target.value)}
                placeholder="Enter state name (e.g., Karnataka)"
                className="flex-1 bg-slate-800/50 border border-slate-600 rounded-lg px-3 py-2 text-white placeholder-slate-400"
              />
              <button
                onClick={syncMySchemeData}
                disabled={syncing || !syncState.trim()}
                className="bg-green-600 hover:bg-green-700 disabled:bg-green-800 disabled:opacity-50 text-white px-4 py-2 rounded-lg transition-colors"
              >
                {syncing ? 'Syncing...' : 'Sync'}
              </button>
            </div>
          </div>
        </div>

        {/* Schemes Table */}
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold">All Schemes</h3>
            <button
              onClick={loadSchemes}
              disabled={loading}
              className="bg-slate-600 hover:bg-slate-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg transition-colors"
            >
              {loading ? 'Loading...' : 'Refresh'}
            </button>
          </div>

          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400 mx-auto"></div>
              <p className="mt-2 text-slate-400">Loading schemes...</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="text-left py-3 px-2">Name</th>
                    <th className="text-left py-3 px-2">State</th>
                    <th className="text-left py-3 px-2">Category</th>
                    <th className="text-left py-3 px-2">Age Range</th>
                    <th className="text-left py-3 px-2">Income Range</th>
                    <th className="text-left py-3 px-2">Occupation</th>
                  </tr>
                </thead>
                <tbody>
                  {schemes.map((scheme) => (
                    <tr key={scheme.id} className="border-b border-white/5 hover:bg-white/5">
                      <td className="py-3 px-2 font-medium">{scheme.name}</td>
                      <td className="py-3 px-2">
                        <span className="px-2 py-1 text-xs bg-blue-500/20 text-blue-300 rounded-full">
                          {scheme.state}
                        </span>
                      </td>
                      <td className="py-3 px-2">
                        <span className="px-2 py-1 text-xs bg-purple-500/20 text-purple-300 rounded-full">
                          {scheme.category}
                        </span>
                      </td>
                      <td className="py-3 px-2 text-sm text-slate-300">
                        {scheme.min_age || scheme.max_age ? 
                          `${scheme.min_age || 0} - ${scheme.max_age || '∞'}` : 
                          'Not set'
                        }
                      </td>
                      <td className="py-3 px-2 text-sm text-slate-300">
                        {scheme.max_income !== null ? 
                          `₹${scheme.max_income || '∞'}` : 
                          'Not set'
                        }
                      </td>
                      <td className="py-3 px-2 text-sm text-slate-300">
                        {scheme.occupation || 'Any'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default AdminPage;