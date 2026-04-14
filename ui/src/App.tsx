import React from 'react';
import { MessageSquare, Settings } from 'lucide-react';
import { useAppStore } from './store';
import { InferenceTab } from './components/InferenceTab';
import { TuningTab } from './components/TuningTab';

function App() {
  const { currentTab, setCurrentTab } = useAppStore();

  return (
    <div className="h-screen flex flex-col">
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-600 to-primary-400 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">PT</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Prompt Tuning Pipeline</h1>
              <p className="text-sm text-gray-500">
                Automated LLM optimization with LLM-as-a-Judge
              </p>
            </div>
          </div>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        <nav className="w-64 bg-white border-r border-gray-200 p-4">
          <div className="space-y-2">
            <button
              onClick={() => setCurrentTab('inference')}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                currentTab === 'inference'
                  ? 'bg-primary-50 text-primary-700 font-medium'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <MessageSquare className="w-5 h-5" />
              <span>Inference</span>
            </button>

            <button
              onClick={() => setCurrentTab('tuning')}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                currentTab === 'tuning'
                  ? 'bg-primary-50 text-primary-700 font-medium'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Settings className="w-5 h-5" />
              <span>Prompt Tuning</span>
            </button>
          </div>

          <div className="mt-8 p-4 bg-gray-50 rounded-lg">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">How it works</h3>
            <ol className="text-xs text-gray-600 space-y-2">
              <li>1. Run queries to test prompts</li>
              <li>2. LLM Judge evaluates responses</li>
              <li>3. System generates improvements</li>
              <li>4. Review and promote winners</li>
            </ol>
          </div>
        </nav>

        <main className="flex-1 bg-gray-50 overflow-hidden">
          {currentTab === 'inference' ? <InferenceTab /> : <TuningTab />}
        </main>
      </div>
    </div>
  );
}

export default App;
