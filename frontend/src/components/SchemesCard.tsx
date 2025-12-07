import { EligibilityResponse, Scheme } from '../types';

interface SchemesCardProps {
  data: EligibilityResponse | null;
  onViewDetails: (scheme: Scheme) => void;
}

export default function SchemesCard({ data, onViewDetails }: SchemesCardProps) {
  const hasEligibleSchemes = data && data.eligible_schemes.length > 0;
  const hasOnlyIneligible = data && data.eligible_schemes.length === 0 && data.ineligible_schemes.length > 0;

  return (
    <div className="rounded-2xl bg-slate-900/60 backdrop-blur border border-white/10 p-6 shadow-xl">
      <div className="mb-6">
        <h3 className="text-2xl font-bold">Your Matching Schemes</h3>
      </div>

      {/* Empty State */}
      {!data && (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <div className="text-6xl mb-4">📋</div>
          <h4 className="text-lg font-semibold mb-2">No schemes yet</h4>
          <p className="text-sm text-slate-400 max-w-xs">
            Fill your profile on the left and click 'Find My Schemes'
          </p>
        </div>
      )}

      {/* Eligible Schemes */}
      {hasEligibleSchemes && (
        <div className="space-y-4">
          {data.eligible_schemes.map((scheme) => (
            <div
              key={scheme.id}
              className="p-4 rounded-xl bg-slate-800/40 border border-slate-700 hover:border-slate-600 hover:bg-slate-800/60 transition-all duration-200 group"
            >
              <div className="flex items-start justify-between mb-2">
                <h4 className="font-semibold text-lg group-hover:text-blue-300 transition-colors">
                  {scheme.name}
                </h4>
                <div className="flex items-center gap-1 text-green-400 text-sm">
                  <span className="w-2 h-2 bg-green-400 rounded-full"></span>
                  <span>Eligible</span>
                </div>
              </div>

              <div className="flex flex-wrap gap-2 mb-3">
                <span className="px-2 py-1 text-xs font-medium bg-blue-500/20 text-blue-300 rounded-md border border-blue-500/30">
                  {scheme.state}
                </span>
                <span className="px-2 py-1 text-xs font-medium bg-purple-500/20 text-purple-300 rounded-md border border-purple-500/30">
                  {scheme.category}
                </span>
              </div>

              <p className="text-sm text-slate-300 mb-4 line-clamp-2">
                {scheme.short_description}
              </p>

              <button
                onClick={() => onViewDetails(scheme)}
                className="text-sm font-medium text-blue-400 hover:text-blue-300 transition-colors"
              >
                View details →
              </button>
            </div>
          ))}
        </div>
      )}

      {/* No Eligible Schemes Warning */}
      {hasOnlyIneligible && (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <div className="text-6xl mb-4">⚠️</div>
          <h4 className="text-lg font-semibold mb-2">We couldn't find eligible schemes</h4>
          <p className="text-sm text-slate-400 max-w-md mb-4">
            We couldn't find eligible schemes with this profile.
          </p>
          <p className="text-xs text-slate-500">
            Try changing state, occupation, or income; or ask the assistant for help.
          </p>
        </div>
      )}
    </div>
  );
}
