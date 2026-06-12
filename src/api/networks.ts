/**
 * Networks API service — matches CriminalNetwork.tsx.
 */

import api from "./client";

export interface GraphNode {
  id: string;
  label: string;
  type: string;
  incidents: number;
  x: number;
  y: number;
  radius: number;
}

export interface GraphEdge {
  source: string;
  target: string;
  label: string;
  weight: number;
}

export interface NetworkGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
  stats: Record<string, any>;
}

export interface NetworkAnalytics {
  centrality: Record<string, number>;
  communities: string[][];
  key_nodes: any[];
  stats: Record<string, any>;
}

export const networksApi = {
  /** Get network graph */
  getGraph: (accusedId?: string, depth = 2) =>
    api.get<NetworkGraph>("/networks/graph", {
      accused_id: accusedId,
      depth,
    }),

  /** Get network analytics */
  getAnalytics: () => api.get<NetworkAnalytics>("/networks/analytics"),

  /** Search network nodes */
  search: (query: string) =>
    api.get<any[]>("/networks/search", { q: query }),
};
