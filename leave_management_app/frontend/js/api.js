/**
 * API Client for Leave Management System
 */

const API_BASE_URL = 'http://localhost:8000/api';

class APIClient {
    constructor() {
        this.token = localStorage.getItem('access_token');
    }

    getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json',
        };

        if (includeAuth && this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        return headers;
    }

    async handleResponse(response) {
        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
            throw new Error(error.detail || 'Request failed');
        }

        // Handle 204 No Content
        if (response.status === 204) {
            return null;
        }

        return response.json();
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('access_token', token);
    }

    clearToken() {
        this.token = null;
        localStorage.removeItem('access_token');
        localStorage.removeItem('current_user');
    }

    isAuthenticated() {
        return !!this.token;
    }

    // Authentication endpoints
    async login(username, password) {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: this.getHeaders(false),
            body: JSON.stringify({ username, password }),
        });

        const data = await this.handleResponse(response);
        this.setToken(data.access_token);
        return data;
    }

    async register(userData) {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: this.getHeaders(false),
            body: JSON.stringify(userData),
        });

        return this.handleResponse(response);
    }

    async getCurrentUser() {
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            method: 'GET',
            headers: this.getHeaders(),
        });

        const user = await this.handleResponse(response);
        localStorage.setItem('current_user', JSON.stringify(user));
        return user;
    }

    logout() {
        this.clearToken();
        window.location.href = '/login';
    }

    // User endpoints
    async getUsers(skip = 0, limit = 100) {
        const response = await fetch(`${API_BASE_URL}/users/?skip=${skip}&limit=${limit}`, {
            method: 'GET',
            headers: this.getHeaders(),
        });

        return this.handleResponse(response);
    }

    async getUserStats() {
        const response = await fetch(`${API_BASE_URL}/users/me/stats`, {
            method: 'GET',
            headers: this.getHeaders(),
        });

        return this.handleResponse(response);
    }

    async getUser(userId) {
        const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
            method: 'GET',
            headers: this.getHeaders(),
        });

        return this.handleResponse(response);
    }

    async updateUser(userId, userData) {
        const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
            method: 'PUT',
            headers: this.getHeaders(),
            body: JSON.stringify(userData),
        });

        return this.handleResponse(response);
    }

    // Leave request endpoints
    async createLeaveRequest(leaveData) {
        const response = await fetch(`${API_BASE_URL}/leaves/`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(leaveData),
        });

        return this.handleResponse(response);
    }

    async getLeaveRequests(params = {}) {
        const queryParams = new URLSearchParams();
        if (params.skip) queryParams.append('skip', params.skip);
        if (params.limit) queryParams.append('limit', params.limit);
        if (params.status_filter) queryParams.append('status_filter', params.status_filter);
        if (params.user_id) queryParams.append('user_id', params.user_id);

        const response = await fetch(`${API_BASE_URL}/leaves/?${queryParams}`, {
            method: 'GET',
            headers: this.getHeaders(),
        });

        return this.handleResponse(response);
    }

    async getMyLeaveRequests(skip = 0, limit = 100) {
        const response = await fetch(`${API_BASE_URL}/leaves/my?skip=${skip}&limit=${limit}`, {
            method: 'GET',
            headers: this.getHeaders(),
        });

        return this.handleResponse(response);
    }

    async getPendingRequests(skip = 0, limit = 100) {
        const response = await fetch(`${API_BASE_URL}/leaves/pending?skip=${skip}&limit=${limit}`, {
            method: 'GET',
            headers: this.getHeaders(),
        });

        return this.handleResponse(response);
    }

    async getDashboardStats() {
        const response = await fetch(`${API_BASE_URL}/leaves/dashboard`, {
            method: 'GET',
            headers: this.getHeaders(),
        });

        return this.handleResponse(response);
    }

    async getLeaveRequest(requestId) {
        const response = await fetch(`${API_BASE_URL}/leaves/${requestId}`, {
            method: 'GET',
            headers: this.getHeaders(),
        });

        return this.handleResponse(response);
    }

    async updateLeaveRequest(requestId, leaveData) {
        const response = await fetch(`${API_BASE_URL}/leaves/${requestId}`, {
            method: 'PUT',
            headers: this.getHeaders(),
            body: JSON.stringify(leaveData),
        });

        return this.handleResponse(response);
    }

    async approveLeaveRequest(requestId, approved, rejectionReason = null) {
        const response = await fetch(`${API_BASE_URL}/leaves/${requestId}/approve`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify({
                approved,
                rejection_reason: rejectionReason,
            }),
        });

        return this.handleResponse(response);
    }

    async cancelLeaveRequest(requestId) {
        const response = await fetch(`${API_BASE_URL}/leaves/${requestId}`, {
            method: 'DELETE',
            headers: this.getHeaders(),
        });

        return this.handleResponse(response);
    }
}

// Create global API client instance
const api = new APIClient();
