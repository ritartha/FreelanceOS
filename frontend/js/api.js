/**
 * FreelanceOS - Frontend API Service
 * Handles JWT authentication and API requests.
 */

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

class ApiService {
  constructor() {
    this.token = localStorage.getItem('access_token');
    this.refreshToken = localStorage.getItem('refresh_token');
    this.user = JSON.parse(localStorage.getItem('user'));
  }

  setSession(data) {
    if (!data || !data.access_token || !data.refresh_token) {
      console.error('setSession called with invalid data', data);
      return;
    }

    this.token = data.access_token;
    this.refreshToken = data.refresh_token;
    this.user = data.user;
    
    localStorage.setItem('access_token', this.token);
    localStorage.setItem('refresh_token', this.refreshToken);
    localStorage.setItem('user', JSON.stringify(this.user));
  }

  clearSession() {
    this.token = null;
    this.refreshToken = null;
    this.user = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  }

  isAuthenticated() {
    return !!this.token;
  }

  async fetch(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const config = {
      ...options,
      headers,
    };

    try {
      const response = await fetch(url, config);
      
      // Auto-parse JSON if it's there
      let data = null;
      if (response.status !== 204) {
        data = await response.json();
      }

      // Handle custom error structure: {"success": false, "error": {"message": "..."}}
      if (!response.ok) {
        if (response.status === 401 && this.token) {
          // Token expired, handle refresh here in a real app, for now just logout
          this.clearSession();
          window.location.href = 'index.html';
        }
        
        const errorMsg = data?.error?.message || data?.detail || data?.general?.[0] || data?.general || data?.error || 'An error occurred';
        throw new Error(errorMsg);
      }

      // Unwrap success response: {"success": true, "data": {...}}
      if (data && data.success !== undefined) {
        // If the success envelope is used but data is undefined, fallback to the entire object
        return data.data !== undefined ? data.data : data;
      }

      return data;
    } catch (error) {
      console.error(`API Error on ${endpoint}:`, error);
      if (error.name === 'TypeError') {
        throw new Error("Unable to connect to the server (CORS or network error). Is the backend running?");
      }
      throw error;
    }
  }

  // --- Auth Endpoints ---

  async login(email, password) {
    const data = await this.fetch('/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    this.setSession(data);
    return data;
  }

  async register(email, password, firstName, lastName) {
    const data = await this.fetch('/auth/register/', {
      method: 'POST',
      body: JSON.stringify({
        email,
        password,
        first_name: firstName,
        last_name: lastName
      }),
    });
    this.setSession(data);
    return data;
  }

  async logout() {
    if (this.refreshToken) {
      try {
        await this.fetch('/auth/logout/', {
          method: 'POST',
          body: JSON.stringify({ refresh: this.refreshToken }),
        });
      } catch (e) {
        // Ignore errors on logout
      }
    }
    this.clearSession();
  }

  // --- Dashboard Data Endpoints ---

  async getDashboardSummary() {
    return this.fetch('/dashboard/summary/');
  }
}

// Global singleton instance
const api = new ApiService();

// UI Utility Functions
function showAlert(message, type = 'error') {
  const alertEl = document.getElementById('global-alert');
  if (alertEl) {
    alertEl.textContent = message;
    alertEl.className = `alert alert-${type}`;
    alertEl.style.display = 'block';
    
    setTimeout(() => {
      alertEl.style.display = 'none';
    }, 5000);
  }
}

function showSpinner(buttonEl) {
  const originalText = buttonEl.innerHTML;
  buttonEl.setAttribute('data-original-text', originalText);
  buttonEl.disabled = true;
  buttonEl.innerHTML = '<span class="spinner"></span>';
}

function hideSpinner(buttonEl) {
  const originalText = buttonEl.getAttribute('data-original-text');
  buttonEl.innerHTML = originalText;
  buttonEl.disabled = false;
}
