import React, { useEffect, useState } from 'react';
import {
  RefreshCw,
  TrendingUp,
  CheckCircle2,
  AlertCircle,
  Clock,
  Sparkles,
} from 'lucide-react';
import { useAppStore } from '../store';
import { apiService } from '../api';
import { format } from 'date-fns';

export const TuningTab: React.FC = () => {
  const {
    activePrompts,
    experimentalPrompts,
    topExperimentalPrompts,
    evaluations,
    lastOptimizationResult,
    setActivePrompts,
    setExperimentalPrompts,
    setTopExperimentalPrompts,
    setEvaluations,
    setLastOptimizationResult,
  } = useAppStore();

  const [isOptimizing, setIsOptimizing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [active, experimental, top, evals] = await Promise.all([
        apiService.getActivePrompts(),
        apiService.getExperimentalPrompts(20),
        apiService.getTopExperimentalPrompts(5),
        apiService.getRecentEvaluations(50),
      ]);

      setActivePrompts(active);
      setExperimentalPrompts(experimental);
      setTopExperimentalPrompts(top);
      setEvaluations(evals);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleTriggerOptimization = async () => {
    setIsOptimizing(true);
    try {
      const result = await apiService.triggerOptimization();
      
      setTimeout(async () => {
        const status = await apiService.getOptimizationStatus(result.workflow_id);
        setLastOptimizationResult(status);
        await loadData();
      }, 5000);
    } catch (error) {
      console.error('Optimization failed:', error);
    } finally {
      setIsOptimizing(false);
    }
  };

  const handlePromotePrompt = async (promptId: string) => {
    if (!confirm('Promote this experimental prompt to active? This will archive the current active prompt.')) {
      return;
    }

    try {
      await apiService.promotePrompt(promptId);
      await loadData();
    } catch (error) {
      console.error('Promotion failed:', error);
      alert('Failed to promote prompt');
    }
  };

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Prompt Tuning Dashboard</h2>
        <div className="flex space-x-2">
          <button onClick={loadData} className="btn btn-secondary flex items-center space-x-2">
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
          <button
            onClick={handleTriggerOptimization}
            disabled={isOptimizing}
            className="btn btn-primary flex items-center space-x-2"
          >
            <Sparkles className={`w-4 h-4 ${isOptimizing ? 'animate-pulse' : ''}`} />
            <span>{isOptimizing ? 'Optimizing...' : 'Trigger Optimization'}</span>
          </button>
        </div>
      </div>

      {lastOptimizationResult && (
        <OptimizationResultCard result={lastOptimizationResult} />
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ActivePromptsSection prompts={activePrompts} />
        <ExperimentalPromptsSection
          prompts={topExperimentalPrompts}
          onPromote={handlePromotePrompt}
        />
      </div>

      <RecentEvaluationsSection evaluations={evaluations} />
    </div>
  );
};

const OptimizationResultCard: React.FC<{ result: any }> = ({ result }) => {
  if (!result || result.status === 'running') {
    return (
      <div className="card bg-blue-50 border border-blue-200">
        <div className="flex items-center space-x-2">
          <RefreshCw className="w-5 h-5 animate-spin text-blue-600" />
          <span className="font-medium text-blue-900">Optimization in progress...</span>
        </div>
      </div>
    );
  }

  const improved = result.improvement_found;

  return (
    <div className={`card ${improved ? 'bg-green-50 border border-green-200' : 'bg-gray-50'}`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3">
          {improved ? (
            <CheckCircle2 className="w-6 h-6 text-green-600 mt-1" />
          ) : (
            <AlertCircle className="w-6 h-6 text-gray-600 mt-1" />
          )}
          <div>
            <h3 className="text-lg font-semibold mb-2">
              {improved ? 'Improvement Found!' : 'No Improvements Needed'}
            </h3>
            {improved && result.test_score && (
              <div className="space-y-1 text-sm">
                <p>
                  New prompt score: <strong>{result.test_score.toFixed(2)}</strong>
                </p>
                <p>
                  Original score: <strong>{result.original_score?.toFixed(2) || 'N/A'}</strong>
                </p>
                {result.ready_for_promotion && (
                  <p className="text-green-700 font-medium mt-2">
                    ✓ Ready for promotion to active
                  </p>
                )}
              </div>
            )}
            {result.reason && <p className="text-sm text-gray-600 mt-1">{result.reason}</p>}
          </div>
        </div>
      </div>
    </div>
  );
};

const ActivePromptsSection: React.FC<{ prompts: any[] }> = ({ prompts }) => {
  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
        <CheckCircle2 className="w-5 h-5 text-green-600" />
        <span>Active Prompts</span>
      </h3>
      <div className="space-y-4">
        {prompts.length === 0 ? (
          <p className="text-gray-500 text-sm">No active prompts</p>
        ) : (
          prompts.map((prompt) => (
            <div key={prompt.id} className="border border-gray-200 rounded-lg p-4">
              <div className="flex justify-between items-start mb-2">
                <span className="badge badge-success">Active</span>
                <span className="text-sm text-gray-500">
                  Score: {prompt.performance_score?.toFixed(2) || 'N/A'}
                </span>
              </div>
              <p className="text-sm text-gray-700 whitespace-pre-wrap">{prompt.prompt_text}</p>
              <div className="mt-2 text-xs text-gray-500">
                <p>Usage: {prompt.metadata?.usage_count || 0} times</p>
                <p>Version: {prompt.metadata?.version || 1}</p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

const ExperimentalPromptsSection: React.FC<{
  prompts: any[];
  onPromote: (id: string) => void;
}> = ({ prompts, onPromote }) => {
  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
        <TrendingUp className="w-5 h-5 text-blue-600" />
        <span>Top Experimental Prompts</span>
      </h3>
      <div className="space-y-4">
        {prompts.length === 0 ? (
          <p className="text-gray-500 text-sm">No experimental prompts</p>
        ) : (
          prompts.map((prompt) => (
            <div key={prompt.id} className="border border-gray-200 rounded-lg p-4">
              <div className="flex justify-between items-start mb-2">
                <span className="badge badge-info">Experimental</span>
                <span className="text-sm text-gray-500">
                  Score: {prompt.test_score?.toFixed(2) || 'N/A'}
                </span>
              </div>
              <p className="text-sm text-gray-700 whitespace-pre-wrap mb-2">
                {prompt.prompt_text}
              </p>
              {prompt.metadata?.generation_rationale && (
                <div className="text-xs text-gray-600 bg-gray-50 p-2 rounded mb-2">
                  <strong>Rationale:</strong> {prompt.metadata.generation_rationale}
                </div>
              )}
              <button
                onClick={() => onPromote(prompt.id)}
                className="btn btn-primary text-xs mt-2"
              >
                Promote to Active
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

const RecentEvaluationsSection: React.FC<{ evaluations: any[] }> = ({ evaluations }) => {
  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
        <Clock className="w-5 h-5 text-gray-600" />
        <span>Recent Evaluations</span>
      </h3>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                Query
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                Score
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                Feedback
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                Time
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {evaluations.slice(0, 10).map((eval) => (
              <tr key={eval.id}>
                <td className="px-4 py-2 text-sm text-gray-900 max-w-xs truncate">
                  {eval.input_query}
                </td>
                <td className="px-4 py-2 text-sm">
                  <span
                    className={`font-medium ${
                      eval.judge_score >= 7
                        ? 'text-green-600'
                        : eval.judge_score >= 5
                        ? 'text-yellow-600'
                        : 'text-red-600'
                    }`}
                  >
                    {eval.judge_score.toFixed(1)}
                  </span>
                </td>
                <td className="px-4 py-2 text-sm text-gray-600 max-w-md truncate">
                  {eval.judge_feedback}
                </td>
                <td className="px-4 py-2 text-sm text-gray-500">
                  {format(new Date(eval.created_at), 'HH:mm:ss')}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
