/**
 * Analytics API service — matches PatternAnalytics.tsx + CrimeMap.tsx.
 */

import api from "./client";

export interface DistrictMapData {
  id: string;
  name: string;
  cases: number;
  risk: string;
  change: string;
}

export interface HotspotData {
  name: string;
  type: string;
  case_count: number;
}

export interface HourlyDataPoint {
  hour: string;
  property: number;
  violent: number;
  cyber: number;
}

export interface MonthlyTrendPoint {
  month: string;
  actual: number;
  predicted: number;
  anomaly: boolean;
}

export interface AnomalyData {
  id: string;
  desc: string;
  district: string;
  severity: string;
  deviation: string;
  detected: string;
  model: string;
}

export const analyticsApi = {
  /** Districts for CrimeMap */
  getDistricts: () => api.get<DistrictMapData[]>("/analytics/districts"),

  /** Hotspots for map overlay */
  getHotspots: (district?: string) =>
    api.get<HotspotData[]>("/analytics/hotspots", { district }),

  /** Hourly crime distribution */
  getHourly: (district?: string) =>
    api.get<HourlyDataPoint[]>("/analytics/hourly", { district }),

  /** Monthly actual vs predicted */
  getMonthlyTrend: (year?: number) =>
    api.get<MonthlyTrendPoint[]>("/analytics/monthly-trend", { year }),

  /** Weekly × hourly heatmap */
  getHeatmap: () => api.get<any[]>("/analytics/heatmap"),

  /** Anomalies */
  getAnomalies: () => api.get<AnomalyData[]>("/analytics/anomalies"),

  /** Socio-economic correlations */
  getSocioEconomic: () => api.get<any[]>("/analytics/socio-economic"),
};
