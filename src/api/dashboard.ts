/**
 * Dashboard API service — matches OverviewDashboard.tsx.
 */

import api from "./client";

export interface KPI {
  label: string;
  value: string;
  change: string;
  up: boolean;
  color: string;
}

export interface CrimeTrendPoint {
  month: string;
  IPC: number;
  violent: number;
  cyber: number;
}

export interface DistrictRanking {
  district: string;
  cases: number;
  change: number;
}

export interface CrimeTypeDistribution {
  name: string;
  value: number;
  color: string;
}

export interface DashboardData {
  kpis: KPI[];
  crime_trends: CrimeTrendPoint[];
  district_ranking: DistrictRanking[];
  crime_types: CrimeTypeDistribution[];
}

export const dashboardApi = {
  /** Get full dashboard data */
  getDashboard: (timeRange = "1y") =>
    api.get<DashboardData>("/dashboard", { time_range: timeRange }),

  /** Get KPIs only */
  getKpis: () => api.get<KPI[]>("/dashboard/kpis"),

  /** Get crime trends */
  getCrimeTrends: (year?: number) =>
    api.get<CrimeTrendPoint[]>("/dashboard/crime-trends", { year }),

  /** Get district ranking */
  getDistrictRanking: () =>
    api.get<DistrictRanking[]>("/dashboard/district-ranking"),

  /** Get crime type distribution */
  getCrimeTypes: () =>
    api.get<CrimeTypeDistribution[]>("/dashboard/crime-types"),
};
