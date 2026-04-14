import axios from 'axios';
import type { 
  Prompt, 
  EvaluationLog, 
  InferenceRequest, 
  InferenceResponse,
  OptimizationResult
} from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // Inference
  runInference: async (request: InferenceRequest): Promise<InferenceResponse> => {
    const response = await api.post<InferenceResponse>('/inference', request);
    return response.data;
  },

  // Prompts
  getActivePrompts: async (): Promise<Prompt[]> => {
    const response = await api.get<Prompt[]>('/prompts/active');
    return response.data;
  },

  getExperimentalPrompts: async (limit = 50): Promise<Prompt[]> => {
    const response = await api.get<Prompt[]>('/prompts/experimental', {
      params: { limit },
    });
    return response.data;
  },

  getTopExperimentalPrompts: async (limit = 10): Promise<Prompt[]> => {
    const response = await api.get<Prompt[]>('/prompts/experimental/top', {
      params: { limit },
    });
    return response.data;
  },

  promotePrompt: async (experimentalPromptId: string, archiveOld = true) => {
    const response = await api.post('/prompts/promote', {
      experimental_prompt_id: experimentalPromptId,
      archive_old_prompt: archiveOld,
    });
    return response.data;
  },

  // Evaluations
  getRecentEvaluations: async (limit = 100): Promise<EvaluationLog[]> => {
    const response = await api.get<EvaluationLog[]>('/evaluations/recent', {
      params: { limit },
    });
    return response.data;
  },

  getEvaluationsForPrompt: async (promptId: string, limit = 50): Promise<EvaluationLog[]> => {
    const response = await api.get<EvaluationLog[]>(`/evaluations/prompt/${promptId}`, {
      params: { limit },
    });
    return response.data;
  },

  // Optimization
  triggerOptimization: async (batchSize?: number) => {
    const response = await api.post('/optimization/trigger', {
      batch_size: batchSize,
      force_regenerate: false,
    });
    return response.data;
  },

  getOptimizationStatus: async (workflowId: string): Promise<OptimizationResult> => {
    const response = await api.get<OptimizationResult>(`/optimization/status/${workflowId}`);
    return response.data;
  },

  // Health
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};
