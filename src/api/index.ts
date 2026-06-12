/**
 * KSP Crime Intelligence Platform — API Module Index
 *
 * Usage:
 *   import { chatApi, dashboardApi, networksApi } from '@/api';
 *   const response = await chatApi.send({ content: "Show crime stats" });
 */

export { default as api } from "./client";
export {
  setTokens,
  clearTokens,
  getAccessToken,
  isAuthenticated,
} from "./client";
export { authApi } from "./auth";
export { chatApi } from "./chat";
export { dashboardApi } from "./dashboard";
export { networksApi } from "./networks";
export { analyticsApi } from "./analytics";
export { profilesApi } from "./profiles";

// Re-export types
export type { User, TokenResponse } from "./auth";
export type { ChatMessage, ChatRequest } from "./chat";
export type {
  KPI,
  CrimeTrendPoint,
  DistrictRanking,
  CrimeTypeDistribution,
  DashboardData,
} from "./dashboard";
export type { GraphNode, GraphEdge, NetworkGraph } from "./networks";
export type {
  DistrictMapData,
  HotspotData,
  HourlyDataPoint,
  MonthlyTrendPoint,
  AnomalyData,
} from "./analytics";
export type { OffenderProfile, RiskAssessment } from "./profiles";
