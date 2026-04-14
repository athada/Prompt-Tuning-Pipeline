import React, { useState } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { useAppStore } from '../store';
import { apiService } from '../api';
import { ChatMessage as ChatMessageType } from '../types';

export const InferenceTab: React.FC = () => {
  const [inputValue, setInputValue] = useState('');
  const { messages, isLoading, addMessage, setLoading } = useAppStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage: ChatMessageType = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    addMessage(userMessage);
    setInputValue('');
    setLoading(true);

    try {
      const response = await apiService.runInference({
        query: inputValue,
        use_experimental: false,
      });

      const assistantMessage: ChatMessageType = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        metadata: {
          execution_time_ms: response.execution_time_ms,
          judge_score: response.metadata?.judge_score,
          prompt_id: response.prompt_id,
        },
      };

      addMessage(assistantMessage);
    } catch (error) {
      const errorMessage: ChatMessageType = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Error: ${error instanceof Error ? error.message : 'Failed to get response'}`,
        timestamp: new Date(),
      };
      addMessage(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-20">
            <p className="text-xl mb-2">Start a conversation</p>
            <p className="text-sm">Ask a question to test the active prompt</p>
          </div>
        ) : (
          messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))
        )}
        {isLoading && (
          <div className="flex items-center space-x-2 text-gray-500">
            <Loader2 className="w-5 h-5 animate-spin" />
            <span>Thinking...</span>
          </div>
        )}
      </div>

      <div className="border-t border-gray-200 p-4">
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type your message..."
            className="input flex-1"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className="btn btn-primary flex items-center space-x-2"
          >
            <Send className="w-4 h-4" />
            <span>Send</span>
          </button>
        </form>
      </div>
    </div>
  );
};

const ChatMessage: React.FC<{ message: ChatMessageType }> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[70%] rounded-lg p-4 ${
          isUser
            ? 'bg-primary-600 text-white'
            : 'bg-white border border-gray-200'
        }`}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
        {message.metadata && !isUser && (
          <div className="mt-2 pt-2 border-t border-gray-200 text-xs text-gray-500 space-y-1">
            {message.metadata.execution_time_ms && (
              <div>Execution time: {message.metadata.execution_time_ms.toFixed(0)}ms</div>
            )}
            {message.metadata.judge_score && (
              <div>
                Judge score:{' '}
                <span
                  className={
                    message.metadata.judge_score >= 7
                      ? 'text-green-600 font-medium'
                      : message.metadata.judge_score >= 5
                      ? 'text-yellow-600 font-medium'
                      : 'text-red-600 font-medium'
                  }
                >
                  {message.metadata.judge_score.toFixed(1)}/10
                </span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
