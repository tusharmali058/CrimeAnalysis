/**
 * Auth API service.
 */

import api, { setTokens, clearTokens } from "./client";

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
  badge_number?: string;
  department?: string;
  district?: string;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export const authApi = {
  login: async (username: string, password: string): Promise<TokenResponse> => {
    const data = await api.post<TokenResponse>("/auth/login", {
      username,
      password,
    });
    setTokens(data.access_token, data.refresh_token);
    return data;
  },

  register: async (userData: {
    username: string;
    email: string;
    full_name: string;
    password: string;
    role?: string;
  }): Promise<TokenResponse> => {
    const data = await api.post<TokenResponse>("/auth/register", userData);
    setTokens(data.access_token, data.refresh_token);
    return data;
  },

  me: () => api.get<User>("/auth/me"),

  logout: () => {
    clearTokens();
  },

  updateProfile: (data: Partial<User>) => api.patch<User>("/auth/me", data),
};
