/**
 * Chat API service — matches CrimeAIChat.tsx Message interface.
 */

import api from "./client";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  citations?: string[];
  confidence?: number;
  followups?: string[];
}

export interface ChatRequest {
  content: string;
  session_id?: string;
  language?: "EN" | "KN";
}

export const chatApi = {
  /** Send a message and get AI response */
  send: (data: ChatRequest) => api.post<ChatMessage>("/chat/send", data),

  /** Get all sessions */
  sessions: () => api.get<any[]>("/chat/sessions"),

  /** Get chat history for a session */
  history: (sessionId: string) => api.get<any>(`/chat/history/${sessionId}`),

  /** Delete a session */
  deleteSession: (sessionId: string) =>
    api.delete(`/chat/sessions/${sessionId}`),

  /** Export chat as PDF */
  exportPdf: (sessionId: string) =>
    api.download(
      "/chat/export-pdf",
      `ksp_chat_${sessionId.slice(0, 8)}.pdf`,
      { session_id: sessionId }
    ),
};
