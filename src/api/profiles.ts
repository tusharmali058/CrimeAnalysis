/**
 * Profiles API service — matches OffenderProfiling.tsx.
 */

import api from "./client";

export interface OffenderProfile {
  id: string;
  name: string;
  alias: string[];
  age?: number;
  gender?: string;
  district: string;
  ps?: string;
  incidents: number;
  status: string;
  category?: string;
  riskScore: number;
  lastKnown?: string;
  firstOffence?: string;
  modus?: string;
  associates: string[];
  profile: Record<string, number>;
  timeline: Array<{ year: string; incidents: number }>;
}

export interface RiskAssessment {
  accused_id: string;
  risk_score: number;
  risk_level: string;
  feature_importance: Record<string, number>;
  profile_scores: Record<string, number>;
  explanation: string[];
}

export const profilesApi = {
  /** List offender profiles */
  list: (params?: {
    district?: string;
    category?: string;
    min_risk?: number;
    search?: string;
    page?: number;
    page_size?: number;
  }) => api.get<OffenderProfile[]>("/profiles/list", params),

  /** Get single offender profile */
  get: (accusedId: string) =>
    api.get<OffenderProfile>(`/profiles/${accusedId}`),

  /** Get risk assessment */
  getRiskAssessment: (accusedId: string) =>
    api.get<RiskAssessment>(`/profiles/${accusedId}/risk-assessment`),

  /** Get timeline */
  getTimeline: (accusedId: string) =>
    api.get<any>(`/profiles/${accusedId}/timeline`),

  /** Get associates */
  getAssociates: (accusedId: string) =>
    api.get<any>(`/profiles/${accusedId}/associates`),
};
