export interface Prompt {
  id: string;
  prompt_text: string;
  prompt_type: string;
  status: string;
  created_at: string;
  performance_score?: number;
  test_score?: number;
  metadata?: Record<string, any>;
}

export interface EvaluationLog {
  id: string;
  prompt_id: string;
  input_query: string;
  output_response: string;
  judge_feedback: string;
  judge_score: number;
  execution_time_ms: number;
  created_at: string;
}

export interface InferenceRequest {
  query: string;
  use_experimental?: boolean;
  prompt_id?: string;
}

export interface InferenceResponse {
  response: string;
  prompt_id: string;
  prompt_text: string;
  execution_time_ms: number;
  metadata?: Record<string, any>;
}

export interface OptimizationResult {
  status: string;
  experimental_prompt_id?: string;
  test_score?: number;
  original_score?: number;
  improvement_found?: boolean;
  ready_for_promotion?: boolean;
  low_score_count?: number;
  reason?: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  metadata?: {
    execution_time_ms?: number;
    judge_score?: number;
    prompt_id?: string;
  };
}
