import { useState } from 'react';
import { UserProfile, EligibilityResponse, Scheme } from '../types';
import ProfileCard from '../components/ProfileCard';
import SchemesCard from '../components/SchemesCard';
import SchemeModal from '../components/SchemeModal';
import AssistantChat from '../components/AssistantChat';
import { AssistantChatErrorBoundary } from '../components/AssistantChatErrorBoundary';

function HomePage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [eligibilityData, setEligibilityData] = useState<EligibilityResponse | null>(null);
  const [selectedScheme, setSelectedScheme] = useState<Scheme | null>(null);

  const handleProfileResolved = (submittedProfile: UserProfile, eligibilityResult: EligibilityResponse) => {
    setProfile(submittedProfile);
    setEligibilityData(eligibilityResult);
  };

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-sm bg-slate-900/50">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold">AI Gov</h1>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <div className="max-w-6xl mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            AI Government{' '}
            <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              Scheme Navigator
            </span>
          </h2>
          <p className="text-lg text-slate-400 max-w-2xl mx-auto">
            Tell us who you are, and we'll match you to welfare schemes you may be eligible for.
          </p>
        </div>

        {/* Main Content */}
        <div className="grid gap-6 md:grid-cols-[minmax(0,1.1fr)_minmax(0,1.2fr)]">
          <ProfileCard onProfileResolved={handleProfileResolved} />
          <SchemesCard 
            data={eligibilityData} 
            onViewDetails={setSelectedScheme}
          />
        </div>

        {/* PWA Install Hint */}
        <p className="mt-8 text-xs text-slate-400 text-center">
          💡 Tip: On supported browsers, you can install this as an app from the address bar menu.
        </p>
      </div>

      {/* Scheme Modal */}
      {selectedScheme && (
        <SchemeModal 
          scheme={selectedScheme} 
          onClose={() => setSelectedScheme(null)} 
        />
      )}

      {/* Assistant Chat */}
      <AssistantChatErrorBoundary>
        <AssistantChat profile={profile} />
      </AssistantChatErrorBoundary>
    </div>
  );
}

export default HomePage;