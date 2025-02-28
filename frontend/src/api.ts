/**
 * API client for the Material Generator API.
 */
import type { GenerationResponse } from './types';

// Base URL for API requests (configurable)
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

/**
 * Generate materials from a natural language query.
 * 
 * @param params - Query parameters
 * @returns Promise with the API response
 */
export async function generateMaterials({ 
  query, 
  n_samples = 5, 
  temperature = 1.2 
}: { 
  query: string; 
  n_samples?: number; 
  temperature?: number 
}): Promise<GenerationResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        n_samples,
        temperature,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to generate materials');
    }

    return await response.json() as GenerationResponse;
  } catch (error) {
    console.error('Error generating materials:', error);
    throw error;
  }
}

/**
 * Get the full URL for a structure file.
 * 
 * @param path - Structure file path
 * @returns Full URL
 */
export function getStructureUrl(path: string | null): string | null {
  if (!path) return null;
  
  // If path is already a full URL, return it
  if (path.startsWith('http')) {
    return path;
  }
  
  // Handle the standard path format from the API
  if (path.startsWith('/api/structures/')) {
    // The API URL without the trailing /api
    const baseUrl = API_BASE_URL.endsWith('/api') 
      ? API_BASE_URL.slice(0, -4) 
      : API_BASE_URL.replace(/\/api\/?$/, '');
    
    return `${baseUrl}${path}`;
  }
  
  // For any other relative path, just append to the API structures endpoint
  const filename = path.split('/').pop();
  return `${API_BASE_URL}/structures/${filename}`;
}

/**
 * Health check for the API.
 * 
 * @returns Promise with the API response
 */
export async function checkApiHealth(): Promise<{ status: string; message: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    
    if (!response.ok) {
      throw new Error('API health check failed');
    }
    
    return await response.json();
  } catch (error) {
    console.error('API health check failed:', error);
    throw error;
  }
}