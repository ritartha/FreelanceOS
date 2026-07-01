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

  async fetchBlob(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = {
      'Accept': options.accept || '*/*',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = 'Bearer ' + this.token;
    }

    const config = { ...options, headers };
    delete config.accept;

    try {
      const response = await window.fetch(url, config);

      if (!response.ok) {
        let message = `Request failed with HTTP ${response.status}`;
        try {
          const text = await response.text();
          const data = text ? JSON.parse(text) : null;
          message = data?.error?.message || data?.detail || message;
        } catch (e) { }

        if (response.status === 401 && this.token) {
          this.clearSession();
          window.location.href = 'index.html';
        }

        throw new Error(message);
      }

      return {
        blob: await response.blob(),
        filename: response.headers.get('Content-Disposition')?.match(/filename="?([^"]+)"?/)?.[1] || null,
      };
    } catch (error) {
      console.error(`API Blob Error on ${endpoint}:`, error);
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

  // Quotations
  async getQuotations(params = {}) { const qs = new URLSearchParams(params).toString(); return this.fetch(`/quotations/${qs ? '?' + qs : ''}`); }
  async getQuotation(id) { return this.fetch(`/quotations/${id}/`); }
  async createQuotation(data) { return this.fetch('/quotations/', { method: 'POST', body: JSON.stringify(data) }); }
  async updateQuotation(id, data) { return this.fetch(`/quotations/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }); }
  async deleteQuotation(id) { return this.fetch(`/quotations/${id}/`, { method: 'DELETE' }); }

  // Contracts
  async getContracts(params = {}) { const qs = new URLSearchParams(params).toString(); return this.fetch(`/contracts/${qs ? '?' + qs : ''}`); }
  async getContract(id) { return this.fetch(`/contracts/${id}/`); }
  async createContract(data) { return this.fetch('/contracts/', { method: 'POST', body: JSON.stringify(data) }); }
  async updateContract(id, data) { return this.fetch(`/contracts/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }); }
  async deleteContract(id) { return this.fetch(`/contracts/${id}/`, { method: 'DELETE' }); }

  // Proposals
  async getProposals(params = {}) { const qs = new URLSearchParams(params).toString(); return this.fetch(`/proposals/${qs ? '?' + qs : ''}`); }
  async getProposal(id) { return this.fetch(`/proposals/${id}/`); }
  async createProposal(data) { return this.fetch('/proposals/', { method: 'POST', body: JSON.stringify(data) }); }
  async updateProposal(id, data) { return this.fetch(`/proposals/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }); }
  async deleteProposal(id) { return this.fetch(`/proposals/${id}/`, { method: 'DELETE' }); }

  // Time Logs
  async getTimeLogs(params = {}) { const qs = new URLSearchParams(params).toString(); return this.fetch(`/time-logs/${qs ? '?' + qs : ''}`); }
  async createTimeLog(data) { return this.fetch('/time-logs/', { method: 'POST', body: JSON.stringify(data) }); }
  async updateTimeLog(id, data) { return this.fetch(`/time-logs/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }); }
  async deleteTimeLog(id) { return this.fetch(`/time-logs/${id}/`, { method: 'DELETE' }); }

  // Expenses
  async getExpenses(params = {}) { const qs = new URLSearchParams(params).toString(); return this.fetch(`/expenses/${qs ? '?' + qs : ''}`); }
  async getExpense(id) { return this.fetch(`/expenses/${id}/`); }
  async createExpense(data) { return this.fetch('/expenses/', { method: 'POST', body: JSON.stringify(data) }); }
  async updateExpense(id, data) { return this.fetch(`/expenses/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }); }
  async deleteExpense(id) { return this.fetch(`/expenses/${id}/`, { method: 'DELETE' }); }

  // Reports
  async getRevenueReport(params = {}) { const qs = new URLSearchParams(params).toString(); return this.fetch(`/reports/revenue/${qs ? '?' + qs : ''}`); }
  async getExpenseReport(params = {}) { const qs = new URLSearchParams(params).toString(); return this.fetch(`/reports/expenses/${qs ? '?' + qs : ''}`); }
  async getProfitReport(params = {}) { const qs = new URLSearchParams(params).toString(); return this.fetch(`/reports/profit/${qs ? '?' + qs : ''}`); }
  async getTopClients(params = {}) { const qs = new URLSearchParams(params).toString(); return this.fetch(`/reports/top-clients/${qs ? '?' + qs : ''}`); }
  async getTaxSummary(params = {}) { const qs = new URLSearchParams(params).toString(); return this.fetch(`/reports/tax/${qs ? '?' + qs : ''}`); }
  async downloadReportCSV(type, params = {}) {
    const qs = new URLSearchParams({ type, ...params }).toString();
    return this.fetchBlob(`/reports/export/csv/?${qs}`, { accept: 'text/csv' });
  }

  // Calendar
  async getCalendarEvents(params = {}) { const qs = new URLSearchParams(params).toString(); return this.fetch(`/calendar/events/${qs ? '?' + qs : ''}`); }
  async createCalendarEvent(data) { return this.fetch('/calendar/events/', { method: 'POST', body: JSON.stringify(data) }); }
  async updateCalendarEvent(id, data) { return this.fetch(`/calendar/events/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }); }
  async deleteCalendarEvent(id) { return this.fetch(`/calendar/events/${id}/`, { method: 'DELETE' }); }

  // Portfolio
  async getPortfolioItems(params = {}) { const qs = new URLSearchParams(params).toString(); return this.fetch(`/portfolio/items/${qs ? '?' + qs : ''}`); }
  async getPortfolioItem(id) { return this.fetch(`/portfolio/items/${id}/`); }
  async createPortfolioItem(data) { return this.fetch('/portfolio/items/', { method: 'POST', body: JSON.stringify(data) }); }
  async updatePortfolioItem(id, data) { return this.fetch(`/portfolio/items/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }); }
  async deletePortfolioItem(id) { return this.fetch(`/portfolio/items/${id}/`, { method: 'DELETE' }); }

  // Notes
  async getNotes(params = {}) { const qs = new URLSearchParams(params).toString(); return this.fetch(`/notes/${qs ? '?' + qs : ''}`); }
  async createNote(data) { return this.fetch('/notes/', { method: 'POST', body: JSON.stringify(data) }); }
  async updateNote(id, data) { return this.fetch(`/notes/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }); }
  async deleteNote(id) { return this.fetch(`/notes/${id}/`, { method: 'DELETE' }); }

  // Notifications
  async getNotifications(params = {}) { const qs = new URLSearchParams(params).toString(); return this.fetch(`/notifications/${qs ? '?' + qs : ''}`); }
  async markNotificationRead(id) { return this.fetch(`/notifications/${id}/`, { method: 'PATCH', body: JSON.stringify({ is_read: true }) }); }
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