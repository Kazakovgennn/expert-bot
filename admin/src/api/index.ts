import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Добавляем токен к каждому запросу
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface Dialog {
  id: number;
  user_id: number;
  user_name: string;
  user_question: string;
  final_answer: string;
  source: string;
  confidence: number;
  asked_at: string;
  answered_at: string | null;
}

export interface Knowledge {
  id: number;
  question: string;
  answer: string;
  category: string;
  is_active: boolean;
  confidence_threshold: number;
  created_at: string;
}

// Auth
export const login = (data: LoginRequest) => api.post<LoginResponse>('/auth/login', data);
export const logout = () => localStorage.removeItem('access_token');

// Dialogs
export const getDialogs = (page: number = 1, limit: number = 50, userId?: number, source?: string) => {
  const params = new URLSearchParams();
  params.append('page', page.toString());
  params.append('limit', limit.toString());
  if (userId) params.append('user_id', userId.toString());
  if (source) params.append('source', source);
  return api.get<{ data: Dialog[]; total: number; pages: number }>(`/dialogs/?${params.toString()}`);
};

export const getDialogStats = () => api.get<{ total: number; bot_answered: number; expert_answered: number; pending: number }>('/dialogs/stats/summary');

// Knowledge
export const getKnowledge = (page: number = 1, limit: number = 50, search?: string) => {
  const params = new URLSearchParams();
  params.append('page', page.toString());
  params.append('limit', limit.toString());
  if (search) params.append('search', search);
  return api.get<{ data: Knowledge[]; total: number; pages: number }>(`/knowledge/?${params.toString()}`);
};

export const createKnowledge = (data: { question: string; answer: string; category?: string }) =>
  api.post<Knowledge>('/knowledge/', data);

export const updateKnowledge = (id: number, data: Partial<Knowledge>) =>
  api.put<Knowledge>(`/knowledge/${id}`, data);

export const deleteKnowledge = (id: number) => api.delete(`/knowledge/${id}`);

export default api;