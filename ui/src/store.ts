import { create } from 'zustand';
import type { ChatMessage, Prompt, EvaluationLog } from './types';

interface AppState {
  // Chat state
  messages: ChatMessage[];
  isLoading: boolean;
  addMessage: (message: ChatMessage) => void;
  clearMessages: () => void;
  setLoading: (loading: boolean) => void;

  // Prompts state
  activePrompts: Prompt[];
  experimentalPrompts: Prompt[];
  topExperimentalPrompts: Prompt[];
  setActivePrompts: (prompts: Prompt[]) => void;
  setExperimentalPrompts: (prompts: Prompt[]) => void;
  setTopExperimentalPrompts: (prompts: Prompt[]) => void;

  // Evaluations state
  evaluations: EvaluationLog[];
  setEvaluations: (evaluations: EvaluationLog[]) => void;

  // UI state
  currentTab: 'inference' | 'tuning';
  setCurrentTab: (tab: 'inference' | 'tuning') => void;

  // Optimization state
  lastOptimizationResult: any | null;
  setLastOptimizationResult: (result: any) => void;
}

export const useAppStore = create<AppState>((set) => ({
  // Chat state
  messages: [],
  isLoading: false,
  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),
  clearMessages: () => set({ messages: [] }),
  setLoading: (loading) => set({ isLoading: loading }),

  // Prompts state
  activePrompts: [],
  experimentalPrompts: [],
  topExperimentalPrompts: [],
  setActivePrompts: (prompts) => set({ activePrompts: prompts }),
  setExperimentalPrompts: (prompts) => set({ experimentalPrompts: prompts }),
  setTopExperimentalPrompts: (prompts) => set({ topExperimentalPrompts: prompts }),

  // Evaluations state
  evaluations: [],
  setEvaluations: (evaluations) => set({ evaluations }),

  // UI state
  currentTab: 'inference',
  setCurrentTab: (tab) => set({ currentTab: tab }),

  // Optimization state
  lastOptimizationResult: null,
  setLastOptimizationResult: (result) => set({ lastOptimizationResult: result }),
}));
