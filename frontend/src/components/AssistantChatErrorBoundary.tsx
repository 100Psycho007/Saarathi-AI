import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
}

export class AssistantChatErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error('AssistantChat error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="fixed bottom-4 right-4 md:bottom-6 md:right-6 z-50 w-[calc(100vw-2rem)] sm:w-96 p-4 rounded-2xl bg-slate-950/90 backdrop-blur-xl border border-red-500/30 shadow-2xl">
          <div className="flex items-start gap-3">
            <span className="text-2xl">⚠️</span>
            <div className="flex-1">
              <h3 className="font-semibold text-sm text-red-400 mb-1">Assistant temporarily paused</h3>
              <p className="text-xs text-slate-300">You can continue using scheme search.</p>
              <button
                onClick={() => this.setState({ hasError: false })}
                className="mt-2 px-3 py-1 text-xs bg-blue-500/20 hover:bg-blue-500/30 text-blue-300 rounded border border-blue-500/30 transition-colors"
              >
                Try again
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
