import { useState, useRef, useEffect } from 'react';
import { API_BASE_URL } from '../config';
import type { UserProfile } from '../types';

interface AssistantChatProps {
  profile: UserProfile | null;
}

interface SuggestedScheme {
  scheme: {
    id: number;
    name: string;
    state: string;
    category: string;
  };
  summary: string;
  eligibility_explanation?: string;
}

interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  suggestedSchemes?: SuggestedScheme[];
  createdAt: Date;
}

export default function AssistantChat({ profile }: AssistantChatProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentInput, setCurrentInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [voiceOutputEnabled, setVoiceOutputEnabled] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  // Check if speech recognition is supported
  const speechRecognitionSupported = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
  
  // Load voices when component mounts
  useEffect(() => {
    if ('speechSynthesis' in window) {
      // Load voices (some browsers need this)
      window.speechSynthesis.getVoices();
      
      // Some browsers fire this event when voices are loaded
      window.speechSynthesis.onvoiceschanged = () => {
        window.speechSynthesis.getVoices();
      };
    }
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Voice Input (STT)
  const recognitionRef = useRef<any>(null);

  const startListening = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Speech recognition not supported in this browser.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-IN";
    recognition.interimResults = false;
    recognition.continuous = false;

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => {
      setIsListening(false);
      recognitionRef.current = null;
    };
    recognition.onerror = () => {
      setIsListening(false);
      recognitionRef.current = null;
    };

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setCurrentInput(transcript);
    };

    recognitionRef.current = recognition;
    recognition.start();
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
      setIsListening(false);
    }
  };

  // Voice Output (TTS) with better voice selection
  const speakText = (text: string) => {
    if (!voiceOutputEnabled || !("speechSynthesis" in window)) return;
    
    // Cancel any ongoing speech
    stopSpeaking();
    
    const utterance = new SpeechSynthesisUtterance(text);
    
    // Try to get a better quality voice
    const voices = window.speechSynthesis.getVoices();
    
    // Prefer these voices in order (more natural sounding)
    const preferredVoices = [
      'Google UK English Female',
      'Google US English',
      'Microsoft Zira - English (United States)',
      'Microsoft David - English (United States)',
      'Samantha',
      'Karen',
      'Daniel',
      'Moira'
    ];
    
    // Find the best available voice
    let selectedVoice = null;
    for (const preferred of preferredVoices) {
      selectedVoice = voices.find(v => v.name.includes(preferred));
      if (selectedVoice) break;
    }
    
    // Fallback: use any English voice
    if (!selectedVoice) {
      selectedVoice = voices.find(v => v.lang.startsWith('en'));
    }
    
    if (selectedVoice) {
      utterance.voice = selectedVoice;
    }
    
    utterance.lang = "en-IN";
    utterance.rate = 0.95; // Slightly slower for clarity
    utterance.pitch = 1.0;
    utterance.volume = 0.8; // Increased volume
    
    utteranceRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  };

  // Stop speaking
  const stopSpeaking = () => {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      utteranceRef.current = null;
    }
  };

  // Cleanup on unmount or when closing chat
  useEffect(() => {
    return () => {
      stopSpeaking();
    };
  }, []);

  // Stop speaking when chat is closed
  useEffect(() => {
    if (!isOpen) {
      stopSpeaking();
    }
  }, [isOpen]);

  // Stop speaking when voice output is disabled
  useEffect(() => {
    if (!voiceOutputEnabled) {
      stopSpeaking();
    }
  }, [voiceOutputEnabled]);

  const handleSend = async () => {
    if (!currentInput.trim() || loading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      text: currentInput,
      createdAt: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentInput('');
    setLoading(true);

    try {
      const body = {
        text: currentInput,
        name: profile?.name ?? null,
        state: profile?.state ?? null,
        age: profile?.age ?? null,
        gender: profile?.gender ?? null,
        occupation: profile?.occupation ?? null,
        annual_income: profile?.annual_income ?? null,
      };

      console.log('Sending chat request:', body);

      const response = await fetch(`${API_BASE_URL}/assistant/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      });

      console.log('Response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Backend error:', errorText);
        throw new Error(`Backend returned ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      console.log('Received data:', data);

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'assistant',
        text: data.answer || 'No response received',
        suggestedSchemes: data.suggested_schemes || [],
        createdAt: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      // Speak the assistant's response
      speakText(data.answer);
    } catch (err) {
      console.error('Chat error:', err);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'assistant',
        text: `Sorry, something went wrong: ${err instanceof Error ? err.message : 'Unknown error'}. Make sure the backend is running on ${API_BASE_URL}`,
        createdAt: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      {/* Launcher Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-4 right-4 md:bottom-6 md:right-6 z-50 flex items-center gap-2 px-5 py-3 bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 rounded-full shadow-2xl transition-all duration-200 hover:scale-105 font-semibold"
          aria-label="Open AI Assistant"
        >
          <span className="text-xl">💬</span>
          <span className="hidden sm:inline">Ask AI</span>
        </button>
      )}

      {/* Chat Panel */}
      {isOpen && (
        <div className="fixed bottom-4 right-4 md:bottom-6 md:right-6 z-50 w-[calc(100vw-2rem)] sm:w-96 flex flex-col rounded-2xl bg-slate-950/90 backdrop-blur-xl border border-white/10 shadow-2xl overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-white/10">
            <div className="flex items-center gap-2">
              <span className="text-xl">🤖</span>
              <div>
                <h3 className="font-semibold text-sm">AI Scheme Assistant</h3>
                <p className="text-xs text-slate-400">Ask about schemes & eligibility</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 text-xs font-medium bg-blue-500/20 text-blue-300 rounded-full border border-blue-500/30">
                Beta
              </span>
              {voiceOutputEnabled && (
                <span className="px-2 py-0.5 text-xs font-medium bg-green-500/20 text-green-300 rounded-full border border-green-500/30">
                  🔊 Voice
                </span>
              )}
              <button
                onClick={() => setIsOpen(false)}
                className="text-slate-400 hover:text-white transition-colors"
                aria-label="Close chat"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          {/* Voice Output Toggle */}
          <div className="px-4 py-2 bg-slate-900/50 border-b border-white/10 flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <span>Voice Output (TTS)</span>
            </div>
            <div className="flex items-center gap-2">
              {window.speechSynthesis?.speaking && (
                <button
                  onClick={stopSpeaking}
                  className="px-2 py-1 text-xs bg-red-500/20 hover:bg-red-500/30 text-red-300 rounded border border-red-500/30 transition-colors"
                  title="Stop speaking"
                >
                  Stop 🔇
                </button>
              )}
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={voiceOutputEnabled}
                  onChange={() => setVoiceOutputEnabled(!voiceOutputEnabled)}
                  className="sr-only peer"
                />
                <div className="w-9 h-5 bg-slate-700 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-500"></div>
              </label>
            </div>
          </div>

          {/* Profile Tip */}
          {!profile && (
            <div className="px-4 py-2 bg-blue-500/10 border-b border-blue-500/20 text-xs text-blue-300">
              💡 Tip: Fill your profile to get more personalized answers
            </div>
          )}

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3 max-h-72 min-h-[16rem]">
            {messages.length === 0 && (
              <div className="flex flex-col items-center justify-center h-full text-center py-8">
                <div className="text-4xl mb-3">👋</div>
                <p className="text-sm text-slate-400 max-w-xs">
                  Hi! Ask me anything about government schemes, eligibility, or how to apply.
                </p>
                <div className="mt-4 space-y-2 text-xs text-slate-500">
                  <p>Try asking:</p>
                  <p>"What scholarships are available?"</p>
                  <p>"How do I apply for PM-KISAN?"</p>
                </div>
              </div>
            )}

            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] px-3 py-2 rounded-2xl ${
                    msg.sender === 'user'
                      ? 'bg-blue-500/80 text-white rounded-br-sm'
                      : 'bg-white/5 text-slate-100 border border-white/10 rounded-bl-sm'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{msg.text}</p>
                  
                  {/* Suggested Schemes */}
                  {msg.suggestedSchemes && msg.suggestedSchemes.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-white/10">
                      <p className="text-xs text-slate-400 mb-1">Suggested schemes:</p>
                      <ul className="text-xs space-y-1">
                        {msg.suggestedSchemes.map((schemeObj, idx) => (
                          <li key={idx} className="flex items-start gap-1">
                            <span className="text-blue-400">•</span>
                            <button
                              onClick={() => {
                                // Send a follow-up question about this scheme
                                setCurrentInput(`Tell me more about ${schemeObj.scheme.name}`);
                              }}
                              className="text-left hover:text-blue-300 hover:underline transition-colors"
                            >
                              {schemeObj.scheme.name}
                            </button>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="max-w-[85%] px-3 py-2 rounded-2xl bg-white/5 border border-white/10 rounded-bl-sm">
                  <div className="flex items-center gap-2">
                    <div className="flex gap-1">
                      <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                      <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                      <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                    </div>
                    <span className="text-xs text-slate-400">Thinking...</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-3 border-t border-white/10 bg-slate-900/50">
            <div className="flex items-end gap-2">
              <input
                type="text"
                value={currentInput}
                onChange={(e) => setCurrentInput(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={loading}
                placeholder="Ask a question..."
                className="flex-1 px-3 py-2 bg-slate-800/50 border border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition text-sm disabled:opacity-50 disabled:cursor-not-allowed"
              />
              
              {/* Mic Button (STT) */}
              {speechRecognitionSupported && (
                <button
                  onClick={isListening ? stopListening : startListening}
                  disabled={loading}
                  className={`p-2 rounded-full border border-white/10 transition-all duration-200 hover:scale-105 ${
                    isListening 
                      ? 'bg-red-500/60 animate-pulse hover:bg-red-600/60' 
                      : 'bg-slate-800/50 hover:bg-slate-700/50'
                  }`}
                  aria-label={isListening ? "Stop listening" : "Voice input"}
                  title={isListening ? "Click to stop" : "Click to speak"}
                >
                  {isListening ? (
                    <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <rect x="6" y="6" width="12" height="12" rx="2" />
                    </svg>
                  ) : (
                    <svg className="w-5 h-5 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                    </svg>
                  )}
                </button>
              )}

              <button
                onClick={handleSend}
                disabled={loading || !currentInput.trim()}
                className="px-4 py-2 bg-blue-500 hover:bg-blue-600 disabled:bg-slate-700 disabled:cursor-not-allowed rounded-xl transition-colors font-medium text-sm"
                aria-label="Send message"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
