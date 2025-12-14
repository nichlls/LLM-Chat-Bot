import { useState } from 'react';
import type { CarRecommendation, ApiResponse } from '../types/api';

const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const useCarRecommendations = () => {
  const [results, setResults] = useState<CarRecommendation[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  const fetchRecommendations = async (prompt: string) => {
    setIsLoading(true);
    setError('');
    setResults([]);

    try {
      const encodedPrompt = encodeURIComponent(prompt.trim());
      const response = await fetch(`${apiUrl}/recommendations?prompt=${encodedPrompt}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: ApiResponse = await response.json();

      if (data.status === 'success') {
        setResults(data.results);
      } else {
        throw new Error('API returned unsuccessful status');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const clearResults = () => {
    setResults([]);
    setError('');
  };

  return {
    results,
    isLoading,
    error,
    fetchRecommendations,
    clearResults,
  };
};
