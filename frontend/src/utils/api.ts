import { API_BASE_URL } from '../config';

export class AuthenticatedAPI {
  private static getAuthHeaders(): Record<string, string> {
    const token = localStorage.getItem('admin_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }

  private static isTokenExpired(): boolean {
    const expires = localStorage.getItem('admin_token_expires');
    return !expires || Date.now() > parseInt(expires);
  }

  static async request(endpoint: string, options: RequestInit = {}): Promise<Response> {
    // Check if token is expired
    if (this.isTokenExpired()) {
      localStorage.removeItem('admin_token');
      localStorage.removeItem('admin_token_expires');
      window.location.href = '/login';
      throw new Error('Token expired');
    }

    const headers = {
      'Content-Type': 'application/json',
      ...this.getAuthHeaders(),
      ...options.headers,
    };

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    // If unauthorized, redirect to login
    if (response.status === 401) {
      localStorage.removeItem('admin_token');
      localStorage.removeItem('admin_token_expires');
      window.location.href = '/login';
      throw new Error('Unauthorized');
    }

    return response;
  }

  static async get(endpoint: string): Promise<Response> {
    return this.request(endpoint, { method: 'GET' });
  }

  static async post(endpoint: string, data?: any): Promise<Response> {
    return this.request(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }
}