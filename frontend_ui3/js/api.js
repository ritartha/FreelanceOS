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
      'Accept': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const config = { ...options, headers };

    try {
      const response = await window.fetch(url, config);

      let data = null;
      if (response.status !== 204) {
        const text = await response.text();
        try {
          data = JSON.parse(text);
        } catch (parseErr) {
          console.error(`Non-JSON response from ${endpoint}:`, text.substring(0, 200));
          throw new Error(`Server returned an unexpected response (HTTP ${response.status}). Check that the backend is running.`);
        }
      }

      if (!response.ok) {
        if (response.status === 401 && this.token) {
          this.clearSession();
          window.location.href = 'index.html';
        }
        const errorMsg = data?.error?.message || data?.detail || data?.general?.[0] || data?.general || (typeof data?.error === 'string' ? data.error : null) || 'An error occurred';
        throw new Error(errorMsg);
      }

      if (data && data.success !== undefined) {
        return data.data !== undefined ? data.data : data;
      }

      return data;
    } catch (error) {
      console.error(`API Error on ${endpoint}:`, error);
      if (error.name === 'TypeError') {
        throw new Error("Unable to connect to the server. Is the backend running?");
      }
      throw error;
    }
  }

  // Auth
  async login(email, password) {
    const data = await this.fetch('/auth/login/', { method: 'POST', body: JSON.stringify({ email, password }) });
    this.setSession(data);
    return data;
  }

  async register(email, password, firstName, lastName) {
    const data = await this.fetch('/auth/register/', {
      method: 'POST',
      body: JSON.stringify({ email, password, first_name: firstName, last_name: lastName }),
    });
    this.setSession(data);
    return data;
  }

  async logout() {
    if (this.refreshToken) {
      try { await this.fetch('/auth/logout/', { method: 'POST', body: JSON.stringify({ refresh: this.refreshToken }) }); } catch (e) { }
    }
    this.clearSession();
  }

  async getMe() { return this.fetch('/auth/me/'); }

  // Dashboard
  async getDashboardSummary() { return this.fetch('/dashboard/summary/'); }

  // Clients
  async getClients(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return this.fetch(`/clients/${qs ? '?' + qs : ''}`);
  }
  async getClient(id) { return this.fetch(`/clients/${id}/`); }
  async createClient(data) { return this.fetch('/clients/', { method: 'POST', body: JSON.stringify(data) }); }
  async updateClient(id, data) { return this.fetch(`/clients/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }); }
  async deleteClient(id) { return this.fetch(`/clients/${id}/`, { method: 'DELETE' }); }

  // Contacts
  async getContacts(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return this.fetch(`/contacts/${qs ? '?' + qs : ''}`);
  }
  async getContact(id) { return this.fetch(`/contacts/${id}/`); }
  async createContact(data) { return this.fetch('/contacts/', { method: 'POST', body: JSON.stringify(data) }); }
  async updateContact(id, data) { return this.fetch(`/contacts/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }); }
  async deleteContact(id) { return this.fetch(`/contacts/${id}/`, { method: 'DELETE' }); }

  // Projects
  async getProjects(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return this.fetch(`/projects/${qs ? '?' + qs : ''}`);
  }
  async getProject(id) { return this.fetch(`/projects/${id}/`); }
  async createProject(data) { return this.fetch('/projects/', { method: 'POST', body: JSON.stringify(data) }); }
  async updateProject(id, data) { return this.fetch(`/projects/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }); }
  async deleteProject(id) { return this.fetch(`/projects/${id}/`, { method: 'DELETE' }); }

  // Tasks
  async getTasks(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return this.fetch(`/tasks/${qs ? '?' + qs : ''}`);
  }
  async getTask(id) { return this.fetch(`/tasks/${id}/`); }
  async createTask(data) { return this.fetch('/tasks/', { method: 'POST', body: JSON.stringify(data) }); }
  async updateTask(id, data) { return this.fetch(`/tasks/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }); }
  async deleteTask(id) { return this.fetch(`/tasks/${id}/`, { method: 'DELETE' }); }

  // Invoices
  async getInvoices(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return this.fetch(`/invoices/${qs ? '?' + qs : ''}`);
  }
  async getInvoice(id) { return this.fetch(`/invoices/${id}/`); }
  async createInvoice(data) { return this.fetch('/invoices/', { method: 'POST', body: JSON.stringify(data) }); }
  async updateInvoice(id, data) { return this.fetch(`/invoices/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }); }
  async deleteInvoice(id) { return this.fetch(`/invoices/${id}/`, { method: 'DELETE' }); }
}

const api = new ApiService();

function showAlert(message, type = 'error') {
  const alertEl = document.getElementById('global-alert');
  if (alertEl) {
    alertEl.textContent = message;
    alertEl.className = `alert alert-${type}`;
    alertEl.style.display = 'block';
    setTimeout(() => { alertEl.style.display = 'none'; }, 5000);
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