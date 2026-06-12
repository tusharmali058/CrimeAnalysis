"""
Synthetic Karnataka Crime Dataset Generator.
Generates ~500 FIRs, ~200 accused, ~300 victims, and ~800 incidents
across all 30 Karnataka districts with realistic distributions.

Usage:
    python -m scripts.seed_synthetic
"""

from __future__ import annotations

import asyncio
import json
import random
import sys
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from faker import Faker

fake = Faker("en_IN")
random.seed(42)

# ══════════════════════════════════════════════════════════════════════════
# Karnataka-specific reference data
# ══════════════════════════════════════════════════════════════════════════

KARNATAKA_DISTRICTS = [
    "Bengaluru Urban", "Bengaluru Rural", "Mysuru", "Mandya", "Tumakuru",
    "Kolar", "Chikkaballapur", "Ramanagara", "Hassan", "Dakshina Kannada",
    "Belagavi", "Ballari", "Kalaburagi", "Vijayapura", "Dharwad",
    "Haveri", "Gadag", "Uttara Kannada", "Shivamogga", "Chikkamagaluru",
    "Kodagu", "Udupi", "Davangere", "Chitradurga", "Chamarajanagar",
    "Bidar", "Raichur", "Koppal", "Yadgir", "Vijayanagara",
]

# Weighted district distribution (Bengaluru gets most cases)
DISTRICT_WEIGHTS = {
    "Bengaluru Urban": 20, "Mysuru": 8, "Belagavi": 7, "Ballari": 6,
    "Kalaburagi": 5, "Dakshina Kannada": 5, "Dharwad": 5, "Tumakuru": 4,
    "Davangere": 4, "Shivamogga": 4, "Vijayapura": 3, "Bengaluru Rural": 3,
    "Hassan": 3, "Mandya": 3, "Haveri": 2, "Chikkamagaluru": 2,
    "Udupi": 2, "Uttara Kannada": 2, "Kolar": 2, "Chitradurga": 2,
    "Bidar": 2, "Raichur": 2, "Koppal": 1, "Yadgir": 1,
    "Chamarajanagar": 1, "Chikkaballapur": 1, "Ramanagara": 1,
    "Kodagu": 1, "Gadag": 1, "Vijayanagara": 1,
}

POLICE_STATIONS = {
    "Bengaluru Urban": ["Whitefield", "Electronic City", "HSR Layout", "Indiranagar", "Koramangala", "Jayanagar", "Yeshwanthpur", "Rajajinagar", "Majestic", "KR Puram"],
    "Mysuru": ["Nazarbad", "Vijayanagar", "Lashkar Mohalla", "Krishnaraja", "Saraswathipuram"],
    "Belagavi": ["Camp", "Tilakwadi", "Shahpur", "Kanabargi", "Gandhinagar"],
    "Ballari": ["Gandhinagar", "Hospet Town", "Kampli", "Kudligi"],
    "Kalaburagi": ["Brahmapur", "Chowk", "Jewargi Colony", "Regd", "Sedam"],
    "Dakshina Kannada": ["Mangaluru East", "Mangaluru South", "Bantwal", "Puttur", "Sullia"],
}

CRIME_TYPES = [
    "Cyber Fraud", "Robbery", "Assault", "Burglary", "Theft",
    "Chain Snatching", "Murder", "UPI Fraud", "Domestic Violence",
    "Drug Trafficking", "Property Forgery", "Kidnapping",
    "Cheating", "Extortion", "Sexual Assault", "Vehicle Theft",
    "Counterfeiting", "Arson", "Rioting", "Dacoity",
]

CRIME_CATEGORIES = {
    "Cyber Fraud": "Cyber", "UPI Fraud": "Cyber", "Counterfeiting": "Cyber",
    "Robbery": "Violent", "Assault": "Violent", "Murder": "Violent",
    "Dacoity": "Violent", "Rioting": "Violent", "Extortion": "Violent",
    "Burglary": "Property", "Theft": "Property", "Chain Snatching": "Property",
    "Vehicle Theft": "Property", "Arson": "Property",
    "Drug Trafficking": "Narcotics",
    "Property Forgery": "Economic", "Cheating": "Economic",
    "Kidnapping": "Violent", "Sexual Assault": "Violent",
    "Domestic Violence": "Violent",
}

# Crime type weights by district type
URBAN_CRIMES = ["Cyber Fraud", "UPI Fraud", "Chain Snatching", "Vehicle Theft", "Burglary", "Cheating"]
RURAL_CRIMES = ["Assault", "Robbery", "Theft", "Domestic Violence", "Property Forgery", "Drug Trafficking"]

IPC_SECTIONS = {
    "Murder": ["302", "34"], "Assault": ["323", "324", "325"], "Robbery": ["392", "394"],
    "Burglary": ["457", "380"], "Theft": ["379", "356"], "Cheating": ["420", "468"],
    "Extortion": ["384", "385"], "Kidnapping": ["363", "365"], "Dacoity": ["395", "396"],
    "Cyber Fraud": ["66C", "66D"], "UPI Fraud": ["66C"], "Sexual Assault": ["376"],
    "Domestic Violence": ["498A", "304B"], "Arson": ["435", "436"],
    "Chain Snatching": ["356", "379"], "Vehicle Theft": ["379"],
    "Drug Trafficking": ["NDPS-20", "NDPS-22"], "Property Forgery": ["420", "467", "468"],
    "Rioting": ["147", "148", "149"], "Counterfeiting": ["489A", "489B"],
}

SEVERITIES = ["low", "medium", "high", "critical"]
FIR_STATUSES = ["registered", "under_investigation", "chargesheeted", "closed"]
ACCUSED_STATUSES = ["on_bail", "absconding", "convicted", "undertrial", "arrested", "released"]

MODUS_OPERANDI = [
    "Targets elderly victims via phone scams, impersonating bank officials",
    "Uses stolen vehicles as getaway, operates across district borders",
    "Social engineering via WhatsApp/Telegram groups, fake investment schemes",
    "Night-time break-in specialist, disables CCTV systems",
    "Targets lone women in secluded areas during evening hours",
    "Uses forged documents for property transactions",
    "Recruits local youth for drug distribution networks",
    "Online romance scams targeting NRIs via matrimonial sites",
    "Organized chain snatching on two-wheelers near traffic signals",
    "Impersonates government officials for extortion",
    "Credit card skimming at ATMs and petrol pumps",
    "Operates hawala channels for cross-border money transfers",
]

KANNADA_FIRST_NAMES = [
    "Ravi", "Suresh", "Ramesh", "Mahesh", "Ganesh", "Venkatesh", "Manjunath",
    "Basavaraj", "Shivaraj", "Kumar", "Prasad", "Nagaraj", "Srinivas",
    "Lakshmi", "Anitha", "Kavitha", "Shobha", "Meera", "Deepa", "Pooja",
    "Vishwanath", "Hanumantha", "Siddaraju", "Ningappa", "Mallappa",
    "Pradeep", "Santosh", "Vinay", "Arun", "Naveen", "Kiran",
]

KANNADA_LAST_NAMES = [
    "Gowda", "Naik", "Patil", "Reddy", "Shetty", "Hegde", "Rao",
    "Swamy", "Murthy", "Sharma", "Acharya", "Kulkarni", "Joshi",
    "Desai", "Meti", "Hadapad", "Madar", "Itnal", "Bagewadi",
]


def weighted_choice(weights: dict) -> str:
    items = list(weights.keys())
    w = list(weights.values())
    return random.choices(items, weights=w, k=1)[0]


def get_ps(district: str) -> str:
    if district in POLICE_STATIONS:
        return random.choice(POLICE_STATIONS[district])
    return f"{district} Town PS"


def get_crime_for_district(district: str) -> str:
    if district in ("Bengaluru Urban", "Bengaluru Rural", "Mysuru"):
        pool = URBAN_CRIMES + CRIME_TYPES
    else:
        pool = RURAL_CRIMES + CRIME_TYPES
    return random.choice(pool)


def random_date(start_year: int = 2023, end_year: int = 2026) -> date:
    start = date(start_year, 1, 1)
    end = date(end_year, 6, 10)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def gen_name() -> str:
    return f"{random.choice(KANNADA_FIRST_NAMES)} {random.choice(KANNADA_LAST_NAMES)}"


# ══════════════════════════════════════════════════════════════════════════
# Data generation
# ══════════════════════════════════════════════════════════════════════════

def generate_firs(n: int = 500) -> list[dict]:
    firs = []
    for i in range(1, n + 1):
        district = weighted_choice(DISTRICT_WEIGHTS)
        crime_type = get_crime_for_district(district)
        d = random_date()
        severity = random.choices(SEVERITIES, weights=[20, 40, 30, 10], k=1)[0]
        status = random.choices(FIR_STATUSES, weights=[25, 35, 25, 15], k=1)[0]
        hour = random.choices(range(24), weights=[
            2, 1, 1, 1, 1, 2, 3, 5, 6, 7, 8, 7, 6, 6, 6, 7, 8, 8, 7, 6, 5, 4, 3, 2
        ], k=1)[0]

        firs.append({
            "fir_number": f"KA-{d.year}-{str(i).zfill(5)}",
            "district": district,
            "police_station": get_ps(district),
            "date_filed": str(d),
            "date_of_offence": str(d - timedelta(days=random.randint(0, 3))),
            "crime_type": crime_type,
            "crime_category": CRIME_CATEGORIES.get(crime_type, "Other"),
            "ipc_sections": IPC_SECTIONS.get(crime_type, ["379"]),
            "description": f"{crime_type} incident reported in {district} district. "
                          f"Complainant reported the crime at {get_ps(district)}.",
            "brief_facts": f"On {d.strftime('%d-%m-%Y')}, a {crime_type.lower()} was committed in the jurisdiction of {get_ps(district)} police station.",
            "status": status,
            "severity": severity,
            "complainant_name": gen_name(),
            "complainant_contact": f"+91{random.randint(7000000000, 9999999999)}",
            "location_name": f"{get_ps(district)} Area, {district}",
            "geo_lat": round(12.0 + random.uniform(0, 6), 6),
            "geo_lon": round(74.0 + random.uniform(0, 4), 6),
            "investigating_officer": f"SI {gen_name()}",
            "time_of_offence": f"{str(hour).zfill(2)}:{random.choice(['00', '15', '30', '45'])}",
            "day_of_week": d.strftime("%A"),
            "month": d.month,
            "year": d.year,
        })
    return firs


def generate_accused(n: int = 200, firs: list[dict] | None = None) -> list[dict]:
    accused_list = []
    all_ids = [f"KAR-{random.choice([2022,2023,2024,2025])}-{str(i).zfill(5)}" for i in range(1, n + 1)]

    for i in range(n):
        district = weighted_choice(DISTRICT_WEIGHTS)
        num_incidents = random.choices(range(1, 13), weights=[30, 20, 15, 10, 8, 5, 4, 3, 2, 1, 1, 1], k=1)[0]
        first_year = random.randint(2018, 2024)

        # Associates (2-5 random connections)
        num_associates = random.randint(0, 5)
        associates = random.sample(
            [aid for aid in all_ids if aid != all_ids[i]],
            min(num_associates, n - 1),
        )

        # Profile scores
        profile = {
            "aggression": random.randint(20, 95),
            "sophistication": random.randint(15, 90),
            "recidivism": random.randint(10, 98),
            "network": random.randint(10, 85),
            "mobility": random.randint(10, 80),
            "financial": random.randint(10, 75),
        }

        # Timeline
        timeline = []
        for y in range(first_year, 2027):
            inc = random.randint(0, min(num_incidents // 2 + 1, 4))
            if inc > 0:
                timeline.append({"year": str(y), "incidents": inc})

        status = random.choices(
            ACCUSED_STATUSES,
            weights=[20, 10, 15, 30, 15, 10],
            k=1,
        )[0]

        risk_score = round(
            profile["aggression"] * 0.2 + profile["recidivism"] * 0.3 +
            profile["network"] * 0.15 + profile["sophistication"] * 0.15 +
            profile["mobility"] * 0.1 + profile["financial"] * 0.1 +
            random.uniform(-10, 10),
            1,
        )
        risk_score = max(10, min(99, risk_score))

        crime_cat = random.choice(list(CRIME_CATEGORIES.values()))

        accused_list.append({
            "accused_id": all_ids[i],
            "name": gen_name(),
            "aliases": [gen_name().split()[0] for _ in range(random.randint(0, 2))],
            "age": random.randint(19, 58),
            "gender": random.choices(["Male", "Female"], weights=[85, 15], k=1)[0],
            "district": district,
            "police_station": get_ps(district),
            "address": f"{random.randint(1, 500)}, {fake.street_name()}, {district}",
            "status": status,
            "category": crime_cat,
            "risk_score": risk_score,
            "last_known_location": f"{get_ps(district)}, {district}",
            "first_offence_date": str(date(first_year, random.randint(1, 12), random.randint(1, 28))),
            "modus_operandi": random.choice(MODUS_OPERANDI),
            "profile_scores": profile,
            "incident_timeline": timeline,
            "associate_ids": associates,
            "fir_id": None,  # Will be linked later
            "incident_count": num_incidents,
        })
    return accused_list


def generate_victims(n: int = 300) -> list[dict]:
    victims = []
    for i in range(n):
        victims.append({
            "name": gen_name(),
            "age": random.randint(16, 72),
            "gender": random.choices(["Male", "Female"], weights=[55, 45], k=1)[0],
            "contact": f"+91{random.randint(7000000000, 9999999999)}",
            "address": f"{random.randint(1, 500)}, {fake.street_name()}, {weighted_choice(DISTRICT_WEIGHTS)}",
            "district": weighted_choice(DISTRICT_WEIGHTS),
            "injury_type": random.choice(["None", "Minor", "Grievous", "Fatal", "Financial Loss"]),
            "loss_amount": round(random.uniform(0, 500000), 2) if random.random() > 0.4 else None,
            "description": "Victim of crime incident",
            "fir_id": None,
        })
    return victims


def generate_incidents(n: int = 800) -> list[dict]:
    incidents = []
    for i in range(n):
        district = weighted_choice(DISTRICT_WEIGHTS)
        d = random_date()
        hour = random.choices(range(24), weights=[
            2, 1, 1, 1, 1, 2, 3, 5, 6, 7, 8, 7, 6, 6, 6, 7, 8, 8, 7, 6, 5, 4, 3, 2
        ], k=1)[0]
        crime_type = get_crime_for_district(district)

        incidents.append({
            "district": district,
            "police_station": get_ps(district),
            "crime_type": crime_type,
            "severity": random.choices(SEVERITIES, weights=[20, 40, 30, 10], k=1)[0],
            "description": f"{crime_type} incident in {district}",
            "incident_time": datetime(d.year, d.month, d.day, hour, random.randint(0, 59), tzinfo=timezone.utc).isoformat(),
            "location_name": f"{get_ps(district)} Area, {district}",
            "geo_lat": round(12.0 + random.uniform(0, 6), 6),
            "geo_lon": round(74.0 + random.uniform(0, 4), 6),
            "hour_of_day": hour,
            "day_of_week": d.strftime("%A")[:3],
        })
    return incidents


def generate_alerts(n: int = 25) -> list[dict]:
    alert_types = ["SPIKE", "GANG", "REPEAT", "HOTSPOT", "FINANCIAL", "FORECAST", "ANOMALY"]
    alerts = []
    for i in range(1, n + 1):
        district = weighted_choice(DISTRICT_WEIGHTS)
        crime = random.choice(CRIME_TYPES)
        atype = random.choice(alert_types)
        severity = random.choices(SEVERITIES, weights=[10, 30, 40, 20], k=1)[0]

        detail_templates = {
            "SPIKE": f"Unusual spike in {crime} cases detected in {district}. 40% above 30-day average.",
            "GANG": f"Potential gang activity identified — 5 co-accused linked across {district} and adjacent districts.",
            "REPEAT": f"Repeat offender KAR-2024-{str(random.randint(100,999)).zfill(5)} active in {district}.",
            "HOTSPOT": f"New crime hotspot emerging near {get_ps(district)}, {district}.",
            "FINANCIAL": f"Suspicious financial pattern: ₹{random.randint(50,500)}K circular transactions in {district}.",
            "FORECAST": f"ML model predicts 25% increase in {crime} for {district} over next 7 days.",
            "ANOMALY": f"Statistical anomaly: {crime} frequency in {district} is 2.3σ above expected baseline.",
        }

        alerts.append({
            "alert_id": f"ALT-{str(i).zfill(3)}",
            "alert_type": atype,
            "district": district,
            "crime": crime,
            "detail": detail_templates.get(atype, f"{atype} alert for {district}"),
            "severity": severity,
            "is_read": random.random() > 0.7,
        })
    return alerts


# ══════════════════════════════════════════════════════════════════════════
# Database seeding
# ══════════════════════════════════════════════════════════════════════════

async def seed_database():
    """Seed the PostgreSQL database with synthetic data."""
    print("🌱 Generating synthetic Karnataka crime data...")

    firs_data = generate_firs(500)
    accused_data = generate_accused(200, firs_data)
    victims_data = generate_victims(300)
    incidents_data = generate_incidents(800)
    alerts_data = generate_alerts(25)

    print(f"   📄 {len(firs_data)} FIRs")
    print(f"   👤 {len(accused_data)} Accused")
    print(f"   🙍 {len(victims_data)} Victims")
    print(f"   🔴 {len(incidents_data)} Incidents")
    print(f"   🚨 {len(alerts_data)} Alerts")

    # Import models
    from app.db.session import get_db_context, init_db
    from app.fir.models import FIR, FIRStatus, CrimeSeverity
    from app.accused.models import Accused, AccusedStatus
    from app.victims.models import Victim
    from app.incidents.models import Incident
    from app.alerts.models import Alert, AlertType, AlertSeverity
    from app.auth.models import User, UserRole
    from app.auth.service import hash_password

    print("\n📦 Creating database tables...")
    await init_db()

    print("📥 Inserting data into PostgreSQL...")

    async with get_db_context() as db:
        # Seed demo users
        demo_users = [
            User(username="admin", email="admin@ksp.gov.in", full_name="System Administrator",
                 hashed_password=hash_password("admin123"), role=UserRole.ADMINISTRATOR,
                 badge_number="KSP-ADM-001", department="SCRB", district="Bengaluru Urban"),
            User(username="investigator", email="investigator@ksp.gov.in", full_name="SI Ramesh Gowda",
                 hashed_password=hash_password("invest123"), role=UserRole.INVESTIGATOR,
                 badge_number="KSP-INV-042", department="Crime Branch", district="Bengaluru Urban"),
            User(username="analyst", email="analyst@ksp.gov.in", full_name="Kavitha Rao",
                 hashed_password=hash_password("analyst123"), role=UserRole.ANALYST,
                 badge_number="KSP-ANL-015", department="Crime Analysis", district="Bengaluru Urban"),
            User(username="supervisor", email="supervisor@ksp.gov.in", full_name="DySP Venkatesh Patil",
                 hashed_password=hash_password("super123"), role=UserRole.SUPERVISOR,
                 badge_number="KSP-SUP-008", department="Supervision", district="Bengaluru Urban"),
            User(username="policymaker", email="policy@ksp.gov.in", full_name="Addl. DGP Nagaraj Hegde",
                 hashed_password=hash_password("policy123"), role=UserRole.POLICYMAKER,
                 badge_number="KSP-POL-003", department="Policy", district="Bengaluru Urban"),
        ]
        for u in demo_users:
            db.add(u)
        await db.flush()
        print(f"   ✅ {len(demo_users)} demo users created")

        # Seed FIRs
        fir_objects = []
        for fd in firs_data:
            fir = FIR(
                fir_number=fd["fir_number"],
                district=fd["district"],
                police_station=fd["police_station"],
                date_filed=date.fromisoformat(fd["date_filed"]),
                date_of_offence=date.fromisoformat(fd["date_of_offence"]) if fd.get("date_of_offence") else None,
                crime_type=fd["crime_type"],
                crime_category=fd.get("crime_category"),
                ipc_sections=fd.get("ipc_sections"),
                description=fd.get("description"),
                brief_facts=fd.get("brief_facts"),
                status=FIRStatus(fd["status"]),
                severity=CrimeSeverity(fd["severity"]),
                complainant_name=fd.get("complainant_name"),
                complainant_contact=fd.get("complainant_contact"),
                location_name=fd.get("location_name"),
                geo_lat=fd.get("geo_lat"),
                geo_lon=fd.get("geo_lon"),
                investigating_officer=fd.get("investigating_officer"),
                time_of_offence=fd.get("time_of_offence"),
                day_of_week=fd.get("day_of_week"),
                month=fd.get("month"),
                year=fd.get("year"),
            )
            db.add(fir)
            fir_objects.append(fir)
        await db.flush()
        print(f"   ✅ {len(fir_objects)} FIRs inserted")

        # Seed Accused (link to random FIRs)
        for ad in accused_data:
            fir_link = random.choice(fir_objects) if fir_objects else None
            accused = Accused(
                accused_id=ad["accused_id"],
                name=ad["name"],
                aliases=ad["aliases"],
                age=ad["age"],
                gender=ad["gender"],
                district=ad["district"],
                police_station=ad.get("police_station"),
                address=ad.get("address"),
                status=AccusedStatus(ad["status"]),
                category=ad.get("category"),
                risk_score=ad["risk_score"],
                last_known_location=ad.get("last_known_location"),
                first_offence_date=date.fromisoformat(ad["first_offence_date"]) if ad.get("first_offence_date") else None,
                modus_operandi=ad.get("modus_operandi"),
                profile_scores=ad.get("profile_scores"),
                incident_timeline=ad.get("incident_timeline"),
                associate_ids=ad.get("associate_ids"),
                fir_id=fir_link.id if fir_link else None,
                incident_count=ad.get("incident_count", 1),
            )
            db.add(accused)
        await db.flush()
        print(f"   ✅ {len(accused_data)} Accused inserted")

        # Seed Victims
        for vd in victims_data:
            fir_link = random.choice(fir_objects) if fir_objects else None
            victim = Victim(
                name=vd["name"],
                age=vd["age"],
                gender=vd["gender"],
                contact=vd.get("contact"),
                address=vd.get("address"),
                district=vd.get("district"),
                injury_type=vd.get("injury_type"),
                loss_amount=vd.get("loss_amount"),
                description=vd.get("description"),
                fir_id=fir_link.id if fir_link else None,
            )
            db.add(victim)
        await db.flush()
        print(f"   ✅ {len(victims_data)} Victims inserted")

        # Seed Incidents
        for ind in incidents_data:
            incident = Incident(
                district=ind["district"],
                police_station=ind.get("police_station"),
                crime_type=ind["crime_type"],
                severity=ind["severity"],
                description=ind.get("description"),
                incident_time=datetime.fromisoformat(ind["incident_time"]),
                location_name=ind.get("location_name"),
                geo_lat=ind.get("geo_lat"),
                geo_lon=ind.get("geo_lon"),
                hour_of_day=ind.get("hour_of_day"),
                day_of_week=ind.get("day_of_week"),
            )
            db.add(incident)
        await db.flush()
        print(f"   ✅ {len(incidents_data)} Incidents inserted")

        # Seed Alerts
        for ald in alerts_data:
            alert = Alert(
                alert_id=ald["alert_id"],
                alert_type=AlertType(ald["alert_type"]),
                district=ald["district"],
                crime=ald["crime"],
                detail=ald["detail"],
                severity=AlertSeverity(ald["severity"]),
                is_read=ald.get("is_read", False),
            )
            db.add(alert)
        await db.flush()
        print(f"   ✅ {len(alerts_data)} Alerts inserted")

    print("\n✨ Database seeding complete!")
    print("\n📋 Demo Credentials:")
    print("   admin / admin123 (Administrator)")
    print("   investigator / invest123 (Investigator)")
    print("   analyst / analyst123 (Analyst)")
    print("   supervisor / super123 (Supervisor)")
    print("   policymaker / policy123 (Policymaker)")


if __name__ == "__main__":
    asyncio.run(seed_database())
