const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export interface LoginResponse {
  success: boolean;
  message: string;
  token?: string;
  username?: string;
  expires_in?: number;
}

export interface ScrapeRequest {
  url: string;
  respect_robots?: boolean;
}

export interface BatchScrapeRequest {
  urls: string[];
  respect_robots?: boolean;
}

class ApiClient {
  private getAuthHeader(): HeadersInit {
    const token = localStorage.getItem('auth_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }

  async login(username: string, password: string): Promise<LoginResponse> {
    const response = await fetch(`${API_URL}/api/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    
    if (!response.ok) {
      throw new Error('Login failed');
    }
    
    const data = await response.json();
    if (data.token) {
      localStorage.setItem('auth_token', data.token);
      localStorage.setItem('username', data.username);
    }
    return data;
  }

  async logout(): Promise<void> {
    await fetch(`${API_URL}/api/logout`, {
      method: 'POST',
      headers: this.getAuthHeader(),
    });
    localStorage.removeItem('auth_token');
    localStorage.removeItem('username');
  }

  async getDashboard() {
    const response = await fetch(`${API_URL}/api/dashboard`, {
      headers: this.getAuthHeader(),
    });
    
    if (!response.ok) throw new Error('Failed to fetch dashboard');
    return response.json();
  }

  async getSessions() {
    const response = await fetch(`${API_URL}/api/sessions`, {
      headers: this.getAuthHeader(),
    });
    
    if (!response.ok) throw new Error('Failed to fetch sessions');
    return response.json();
  }

  async scrapeSingleUrl(data: ScrapeRequest) {
    const response = await fetch(`${API_URL}/api/scrape`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...this.getAuthHeader(),
      },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) throw new Error('Scraping failed');
    return response.json();
  }

  async scrapeBatch(data: BatchScrapeRequest) {
    const response = await fetch(`${API_URL}/api/scrape/batch`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...this.getAuthHeader(),
      },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) throw new Error('Batch scraping failed');
    return response.json();
  }

  async getSessionData(sessionId: number) {
    const response = await fetch(`${API_URL}/api/session/${sessionId}`, {
      headers: this.getAuthHeader(),
    });
    
    if (!response.ok) throw new Error('Failed to fetch session data');
    return response.json();
  }
}

export const api = new ApiClient();
