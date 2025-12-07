import { Scheme } from '../types';
import { formatIndianCurrency } from '../utils/formatters';

interface SchemeModalProps {
  scheme: Scheme;
  onClose: () => void;
}

export default function SchemeModal({ scheme, onClose }: SchemeModalProps) {
  return (
    <div 
      className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50"
      onClick={onClose}
    >
      <div 
        className="bg-slate-900 rounded-2xl border border-white/10 max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="sticky top-0 bg-slate-900 border-b border-white/10 p-6 flex items-start justify-between">
          <div>
            <h3 className="text-2xl font-bold mb-2">{scheme.name}</h3>
            <div className="flex flex-wrap gap-2">
              <span className="px-2 py-1 text-xs font-medium bg-blue-500/20 text-blue-300 rounded-md border border-blue-500/30">
                {scheme.state}
              </span>
              <span className="px-2 py-1 text-xs font-medium bg-purple-500/20 text-purple-300 rounded-md border border-purple-500/30">
                {scheme.category}
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-200 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Description */}
          <div>
            <h4 className="text-lg font-semibold mb-2">About this scheme</h4>
            <p className="text-slate-300">{scheme.short_description}</p>
          </div>

          {/* Eligibility Criteria */}
          <div>
            <h4 className="text-lg font-semibold mb-3">Who is this for?</h4>
            <div className="space-y-2 text-sm">
              {scheme.category && (
                <div className="flex items-center gap-2">
                  <span className="text-slate-400">Category:</span>
                  <span className="font-medium">{scheme.category}</span>
                </div>
              )}
              {(scheme.min_age || scheme.max_age) && (
                <div className="flex items-center gap-2">
                  <span className="text-slate-400">Age:</span>
                  <span className="font-medium">
                    {scheme.min_age && scheme.max_age 
                      ? `${scheme.min_age} - ${scheme.max_age} years`
                      : scheme.min_age 
                      ? `${scheme.min_age}+ years`
                      : `Up to ${scheme.max_age} years`}
                  </span>
                </div>
              )}
              {scheme.max_income && (
                <div className="flex items-center gap-2">
                  <span className="text-slate-400">Max Income:</span>
                  <span className="font-medium">{formatIndianCurrency(scheme.max_income)}</span>
                </div>
              )}
              {scheme.occupation && (
                <div className="flex items-center gap-2">
                  <span className="text-slate-400">Occupation:</span>
                  <span className="font-medium capitalize">{scheme.occupation}</span>
                </div>
              )}
            </div>
          </div>

          {/* Application Process */}
          {scheme.application_process && (
            <div>
              <h4 className="text-lg font-semibold mb-3">How to apply</h4>
              <div className="bg-slate-800/40 rounded-lg p-4 border border-slate-700">
                <p className="text-sm text-slate-300 whitespace-pre-line">
                  {scheme.application_process}
                </p>
              </div>
            </div>
          )}

          {/* Official Link */}
          {scheme.official_link && (
            <div>
              <a
                href={scheme.official_link}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-300 rounded-lg border border-blue-500/30 transition-colors"
              >
                <span>Open official link</span>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
