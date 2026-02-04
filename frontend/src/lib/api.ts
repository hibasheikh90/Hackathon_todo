
/**
 * API client utility for making authenticated requests
 * Automatically attaches JWT token to requests
 */
class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
  }

  /**
   * Makes a request with automatic token attachment
   */
  async request(endpoint: string, options: RequestInit = {}) {
    const url = `${this.baseUrl}${endpoint}`;

    // Get the auth token if available
    const token = this.getToken();

    const headers = {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers,
    } as Record<string, string>;

    const config: RequestInit = {
      ...options,
      headers,
    };

    try {
      const response = await fetch(url, config);

      // Handle different response statuses
      if (!response.ok) {
        // Don't throw for 401 - let the caller handle authentication
        if (response.status === 401) {
          // Remove invalid token
          if (typeof window !== 'undefined') {
            localStorage.removeItem('auth_token');
          }
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Try to parse JSON response, fall back to text if not JSON
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      } else {
        return await response.text();
      }
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  /**
   * Get auth token from storage
   */
  private getToken(): string | null {
    if (typeof window !== 'undefined') {
      // Try to get from localStorage
      const storedToken = localStorage.getItem('auth_token');
      if (storedToken) {
        return storedToken;
      }
    }
    return null;
  }

  /**
   * GET request
   */
  async get<T = any>(endpoint: string): Promise<T> {
    return this.request(endpoint, { method: 'GET' });
  }

  /**
   * POST request
   */
  async post<T = any>(endpoint: string, data?: any): Promise<T> {
    return this.request(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  /**
   * PUT request
   */
  async put<T = any>(endpoint: string, data: any): Promise<T> {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  /**
   * PATCH request
   */
  async patch<T = any>(endpoint: string, data: any): Promise<T> {
    return this.request(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  /**
   * DELETE request
   */
  async delete<T = any>(endpoint: string): Promise<T> {
    return this.request(endpoint, { method: 'DELETE' });
  }
}

// Create a singleton instance
const apiClient = new ApiClient();

export { apiClient };
export type { ApiClient };