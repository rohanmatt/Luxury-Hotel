"""
generate_data.py
Generates synthetic data for Belgravia Health & Fitness BI demo.
Covers: Membership, Sales, Capacity/Scheduling, Marketing.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

SEED = 42
np.random.seed(SEED)
random.seed(SEED)

BRANDS = ["Genesis Health + Fitness", "Ninja Parc", "Jump Swim Schools", "Belgravia Kids Swim"]
LOCATIONS = {
    "Genesis Health + Fitness": ["Sydney CBD", "Melbourne South", "Brisbane North", "Perth West"],
    "Ninja Parc": ["Sydney Olympic Park", "Melbourne Arena", "Gold Coast"],
    "Jump Swim Schools": ["Parramatta", "Chatswood", "Bondi", "St Kilda"],
    "Belgravia Kids Swim": ["Canberra", "Newcastle", "Wollongong"],
}
MEMBERSHIP_TYPES = ["Casual", "Monthly", "Annual", "Family", "Student", "Senior"]
CHANNELS = ["Google Ads", "Facebook", "Instagram", "Email", "Referral", "Walk-in", "SEO"]
CLASSES = ["Yoga", "Spin", "HIIT", "Pilates", "Boxing", "Aqua Aerobics", "Swim Lesson", "Ninja Course"]

START = datetime(2023, 1, 1)
END = datetime(2024, 12, 31)
N_DAYS = (END - START).days + 1
DATES = [START + timedelta(days=i) for i in range(N_DAYS)]


def random_date(start=START, end=END):
    return start + timedelta(days=random.randint(0, (end - start).days))


# ── Membership Data ────────────────────────────────────────────────────────────
def generate_membership(n=5000):
    rows = []
    for i in range(n):
        brand = random.choice(BRANDS)
        location = random.choice(LOCATIONS[brand])
        join_date = random_date()
        mtype = random.choices(MEMBERSHIP_TYPES, weights=[5, 30, 25, 15, 15, 10])[0]
        duration = {
            "Casual": None,
            "Monthly": random.randint(1, 24),
            "Annual": random.randint(1, 3) * 12,
            "Family": random.randint(6, 36),
            "Student": random.randint(3, 12),
            "Senior": random.randint(6, 36),
        }[mtype]
        cancel_date = None
        if duration and random.random() < 0.35:
            cancel_date = join_date + timedelta(days=random.randint(30, duration * 30))
            if cancel_date > END:
                cancel_date = None

        monthly_fee = {
            "Casual": round(random.uniform(15, 25), 2),
            "Monthly": round(random.uniform(45, 80), 2),
            "Annual": round(random.uniform(35, 65), 2),
            "Family": round(random.uniform(90, 150), 2),
            "Student": round(random.uniform(30, 50), 2),
            "Senior": round(random.uniform(35, 55), 2),
        }[mtype]

        rows.append({
            "member_id": f"M{i+1:05d}",
            "brand": brand,
            "location": location,
            "membership_type": mtype,
            "join_date": join_date.date(),
            "cancel_date": cancel_date.date() if cancel_date else None,
            "active": cancel_date is None,
            "monthly_fee": monthly_fee,
            "age_group": random.choices(["18-25", "26-35", "36-45", "46-55", "55+"], weights=[20, 30, 25, 15, 10])[0],
            "gender": random.choices(["M", "F", "Other"], weights=[45, 50, 5])[0],
            "nps_score": random.choices(range(0, 11), weights=[2,1,1,2,3,5,7,10,15,20,34])[0],
        })
    return pd.DataFrame(rows)


# ── Sales & Revenue Data ───────────────────────────────────────────────────────
def generate_sales(n=8000):
    rows = []
    for i in range(n):
        brand = random.choice(BRANDS)
        location = random.choice(LOCATIONS[brand])
        sale_date = random_date()
        product = random.choices(
            ["New Membership", "Renewal", "Personal Training", "Merchandise", "Supplement", "Event"],
            weights=[30, 25, 20, 10, 8, 7]
        )[0]
        base = {"New Membership": 200, "Renewal": 150, "Personal Training": 120,
                "Merchandise": 60, "Supplement": 45, "Event": 80}[product]
        amount = round(base * random.uniform(0.7, 1.8), 2)

        rows.append({
            "sale_id": f"S{i+1:05d}",
            "brand": brand,
            "location": location,
            "sale_date": sale_date.date(),
            "product": product,
            "amount": amount,
            "channel": random.choices(CHANNELS, weights=[20, 18, 15, 12, 10, 15, 10])[0],
            "staff_id": f"ST{random.randint(1, 50):03d}",
            "month": sale_date.strftime("%Y-%m"),
            "quarter": f"Q{(sale_date.month-1)//3+1} {sale_date.year}",
        })
    return pd.DataFrame(rows)


# ── Capacity & Scheduling Data ─────────────────────────────────────────────────
def generate_capacity(n=3000):
    rows = []
    for i in range(n):
        brand = random.choice(BRANDS)
        location = random.choice(LOCATIONS[brand])
        class_date = random_date()
        cls = random.choice(CLASSES)
        capacity = random.choice([10, 15, 20, 25, 30])
        booked = random.randint(int(capacity * 0.3), capacity)
        attended = random.randint(int(booked * 0.6), booked)
        hour = random.choices(range(6, 21), weights=[3,5,8,7,6,4,3,5,8,9,8,6,5,4,3])[0]

        rows.append({
            "session_id": f"C{i+1:05d}",
            "brand": brand,
            "location": location,
            "class": cls,
            "date": class_date.date(),
            "day_of_week": class_date.strftime("%A"),
            "hour": hour,
            "capacity": capacity,
            "booked": booked,
            "attended": attended,
            "utilisation_pct": round(booked / capacity * 100, 1),
            "no_show_rate": round((booked - attended) / max(booked, 1) * 100, 1),
            "instructor_id": f"I{random.randint(1, 20):03d}",
            "month": class_date.strftime("%Y-%m"),
        })
    return pd.DataFrame(rows)


# ── Marketing Data ─────────────────────────────────────────────────────────────
def generate_marketing(n=500):
    rows = []
    campaign_names = [
        "Summer Splash", "New Year New You", "Family Fun Pack", "Back to School",
        "Ninja Challenge", "Swim Safe", "Winter Wellness", "Refer a Friend",
        "Student Promo", "Senior Fit", "HIIT the Gym", "Aqua Blast"
    ]
    for i in range(n):
        brand = random.choice(BRANDS)
        channel = random.choice(CHANNELS)
        month_offset = random.randint(0, 23)
        month_date = START + timedelta(days=30 * month_offset)
        spend = round(random.uniform(500, 15000), 2)
        impressions = int(spend * random.uniform(80, 200))
        clicks = int(impressions * random.uniform(0.01, 0.05))
        leads = int(clicks * random.uniform(0.05, 0.2))
        conversions = int(leads * random.uniform(0.1, 0.4))

        rows.append({
            "campaign_id": f"CM{i+1:04d}",
            "brand": brand,
            "channel": channel,
            "campaign_name": random.choice(campaign_names),
            "month": month_date.strftime("%Y-%m"),
            "spend": spend,
            "impressions": impressions,
            "clicks": clicks,
            "leads": leads,
            "conversions": conversions,
            "cpc": round(spend / max(clicks, 1), 2),
            "cpl": round(spend / max(leads, 1), 2),
            "cpa": round(spend / max(conversions, 1), 2),
            "roas": round((conversions * 150) / max(spend, 1), 2),
        })
    return pd.DataFrame(rows)


# ── Profits & Cost Data ────────────────────────────────────────────────────────
COST_CATEGORIES = ["Staff Wages", "Facility Lease", "Utilities", "Equipment", "Insurance",
                   "Marketing", "Maintenance", "Admin & IT", "Instructor Fees"]

def generate_profits(n=800):
    """Monthly P&L data per brand/location with revenue, itemised costs, and net profit."""
    rows = []
    for month_offset in range(24):  # 2023–2024
        month_date = START + timedelta(days=30 * month_offset)
        month_str = month_date.strftime("%Y-%m")
        quarter = f"Q{(month_date.month-1)//3+1} {month_date.year}"

        for brand in BRANDS:
            for location in LOCATIONS[brand]:
                # Revenue streams
                membership_rev = round(random.uniform(18000, 75000) * (1 + month_offset * 0.005), 2)
                pt_rev = round(random.uniform(4000, 20000), 2)
                retail_rev = round(random.uniform(1000, 8000), 2)
                events_rev = round(random.uniform(500, 5000), 2)
                total_revenue = membership_rev + pt_rev + retail_rev + events_rev

                # Cost structure
                cost_staff = round(total_revenue * random.uniform(0.28, 0.38), 2)
                cost_lease = round(random.uniform(4000, 18000), 2)
                cost_utilities = round(random.uniform(800, 4000), 2)
                cost_equipment = round(random.uniform(300, 3000), 2)
                cost_insurance = round(random.uniform(400, 1500), 2)
                cost_marketing = round(total_revenue * random.uniform(0.04, 0.10), 2)
                cost_maintenance = round(random.uniform(200, 2000), 2)
                cost_admin = round(random.uniform(500, 2500), 2)
                cost_instructor = round(total_revenue * random.uniform(0.05, 0.12), 2)

                total_costs = sum([cost_staff, cost_lease, cost_utilities, cost_equipment,
                                   cost_insurance, cost_marketing, cost_maintenance,
                                   cost_admin, cost_instructor])
                gross_profit = total_revenue - total_costs
                profit_margin = round(gross_profit / max(total_revenue, 1) * 100, 2)
                ebitda = gross_profit + cost_equipment * 0.1  # simplified

                rows.append({
                    "month": month_str,
                    "quarter": quarter,
                    "brand": brand,
                    "location": location,
                    "revenue_membership": membership_rev,
                    "revenue_pt": pt_rev,
                    "revenue_retail": retail_rev,
                    "revenue_events": events_rev,
                    "total_revenue": round(total_revenue, 2),
                    "cost_staff": cost_staff,
                    "cost_lease": cost_lease,
                    "cost_utilities": cost_utilities,
                    "cost_equipment": cost_equipment,
                    "cost_insurance": cost_insurance,
                    "cost_marketing": cost_marketing,
                    "cost_maintenance": cost_maintenance,
                    "cost_admin": cost_admin,
                    "cost_instructor": cost_instructor,
                    "total_costs": round(total_costs, 2),
                    "gross_profit": round(gross_profit, 2),
                    "profit_margin_pct": profit_margin,
                    "ebitda": round(ebitda, 2),
                })
    return pd.DataFrame(rows)


def load_all():
    """Return all datasets as a dict. Cache-friendly for Streamlit."""
    return {
        "membership": generate_membership(),
        "sales": generate_sales(),
        "capacity": generate_capacity(),
        "marketing": generate_marketing(),
        "profits": generate_profits(),
    }


if __name__ == "__main__":
    data = load_all()
    for name, df in data.items():
        df.to_csv(f"{name}.csv", index=False)
        print(f"✅  {name}.csv — {len(df):,} rows")