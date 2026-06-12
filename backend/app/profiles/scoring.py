"""
Risk scoring engine for offender profiling.
Computes criminological risk scores using weighted feature analysis.
"""

from __future__ import annotations

import logging
import math
from typing import Any

logger = logging.getLogger(__name__)

# ── Feature weights for risk scoring ─────────────────────────────────────

RISK_WEIGHTS = {
    "incident_count": 0.25,
    "recidivism_rate": 0.20,
    "network_centrality": 0.15,
    "crime_severity_avg": 0.15,
    "jurisdiction_spread": 0.10,
    "time_acceleration": 0.10,
    "absconding_history": 0.05,
}

SEVERITY_SCORES = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}


def compute_risk_score(
    incident_count: int,
    first_offence_year: int | None = None,
    districts_active: int = 1,
    crime_severities: list[str] | None = None,
    status: str = "undertrial",
    network_degree: int = 0,
    time_between_offences_days: list[int] | None = None,
) -> dict[str, Any]:
    """
    Compute a comprehensive risk score (0-100) with feature breakdown.

    Returns:
        {
            "risk_score": float,
            "risk_level": str,
            "feature_importance": dict,
            "profile_scores": dict,
            "explanation": list[str],
        }
    """
    features = {}
    explanations = []

    # 1. Incident count score (0-100)
    incident_score = min(100, incident_count * 8)
    features["incident_count"] = incident_score
    if incident_count >= 5:
        explanations.append(f"High repeat offender: {incident_count} incidents recorded")

    # 2. Recidivism rate (based on time between offences)
    recidivism_score = 0
    if time_between_offences_days and len(time_between_offences_days) >= 2:
        avg_gap = sum(time_between_offences_days) / len(time_between_offences_days)
        recidivism_score = min(100, max(0, 100 - avg_gap / 3))
        if avg_gap < 90:
            explanations.append(f"Rapid reoffending: avg {int(avg_gap)} days between incidents")
    elif incident_count > 1:
        recidivism_score = 60
    features["recidivism_rate"] = recidivism_score

    # 3. Network centrality (based on connected associates)
    network_score = min(100, network_degree * 12)
    features["network_centrality"] = network_score
    if network_degree >= 5:
        explanations.append(f"Highly connected: {network_degree} known associates")

    # 4. Crime severity average
    severity_score = 50
    if crime_severities:
        avg_sev = sum(SEVERITY_SCORES.get(s, 2) for s in crime_severities) / len(crime_severities)
        severity_score = min(100, avg_sev * 25)
        if avg_sev >= 3:
            explanations.append("Predominantly involved in high-severity crimes")
    features["crime_severity_avg"] = severity_score

    # 5. Jurisdiction spread
    jurisdiction_score = min(100, districts_active * 25)
    features["jurisdiction_spread"] = jurisdiction_score
    if districts_active >= 3:
        explanations.append(f"Cross-jurisdiction activity: {districts_active} districts")

    # 6. Time acceleration (escalating frequency)
    acceleration_score = 50
    if time_between_offences_days and len(time_between_offences_days) >= 3:
        recent = time_between_offences_days[-2:]
        older = time_between_offences_days[:2]
        if sum(older) > 0 and sum(recent) / len(recent) < sum(older) / len(older) * 0.7:
            acceleration_score = 85
            explanations.append("Escalating frequency: recent offences more frequent than historical")
    features["time_acceleration"] = acceleration_score

    # 7. Absconding penalty
    absconding_score = 90 if status == "absconding" else 0
    features["absconding_history"] = absconding_score
    if status == "absconding":
        explanations.append("Currently absconding — high flight risk")

    # Weighted final score
    risk_score = sum(
        features[feat] * RISK_WEIGHTS[feat]
        for feat in RISK_WEIGHTS
    )
    risk_score = round(min(100, max(0, risk_score)), 1)

    # Risk level classification
    if risk_score >= 85:
        risk_level = "critical"
    elif risk_score >= 65:
        risk_level = "high"
    elif risk_score >= 40:
        risk_level = "medium"
    else:
        risk_level = "low"

    # Profile scores for radar chart (matching OffenderProfiling.tsx)
    profile_scores = {
        "aggression": min(100, int(severity_score * 1.1)),
        "sophistication": min(100, int((network_score + jurisdiction_score) / 2)),
        "recidivism": int(recidivism_score),
        "network": int(network_score),
        "mobility": int(jurisdiction_score),
        "financial": min(100, int(network_score * 0.7 + incident_score * 0.3)),
    }

    # Feature importance (normalized)
    total_weight = sum(RISK_WEIGHTS.values())
    feature_importance = {
        feat: round(RISK_WEIGHTS[feat] / total_weight * features[feat] / 100, 3)
        for feat in RISK_WEIGHTS
    }

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "feature_importance": feature_importance,
        "profile_scores": profile_scores,
        "explanation": explanations,
        "raw_features": features,
    }
