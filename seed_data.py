import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path


DB_PATH = Path(__file__).parent / "data" / "lokal_growth.db"

CITIES = ["Jaipur", "Indore", "Patna", "Mysore", "Lucknow", "Bangalore"]
LANGUAGES = ["Hindi", "Kannada", "Telugu", "Tamil", "English"]
CAMPAIGNS = ["WhatsApp", "Push Notification", "SMS"]


def city_tier(city):
    if city in {"Mysore", "Patna", "Lucknow"}:
        return "Tier-3"
    return "Tier-2"


def seed():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript(
        """
        DROP TABLE IF EXISTS users;
        DROP TABLE IF EXISTS daily_activity;
        DROP TABLE IF EXISTS job_funnel;
        DROP TABLE IF EXISTS campaigns;

        CREATE TABLE users (
            user_id INTEGER PRIMARY KEY,
            city TEXT,
            city_tier TEXT,
            language TEXT,
            signup_date TEXT
        );

        CREATE TABLE daily_activity (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            activity_date TEXT,
            sessions INTEGER,
            minutes_spent INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        );

        CREATE TABLE job_funnel (
            funnel_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            viewed_jobs INTEGER,
            applied_jobs INTEGER,
            completed_profile INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        );

        CREATE TABLE campaigns (
            campaign_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            campaign_type TEXT,
            sent INTEGER,
            opened INTEGER,
            clicked INTEGER,
            converted INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        );
        """
    )

    random.seed(42)
    start = date.today() - timedelta(days=30)
    users = []

    for user_id in range(1, 901):
        city = random.choices(
            CITIES,
            weights=[18, 16, 15, 13, 16, 22],
            k=1,
        )[0]
        language = random.choices(
            LANGUAGES,
            weights=[36, 17, 16, 12, 19],
            k=1,
        )[0]
        signup_date = start + timedelta(days=random.randint(0, 30))
        users.append((user_id, city, city_tier(city), language, signup_date.isoformat()))

    cur.executemany(
        "INSERT INTO users (user_id, city, city_tier, language, signup_date) VALUES (?, ?, ?, ?, ?)",
        users,
    )

    for user_id, city, tier, language, _ in users:
        base_active_prob = 0.45
        if city in {"Bangalore", "Jaipur"}:
            base_active_prob += 0.12
        if language == "Kannada":
            base_active_prob -= 0.08
        if tier == "Tier-3":
            base_active_prob -= 0.05

        for day_offset in range(21):
            activity_date = date.today() - timedelta(days=day_offset)
            if random.random() < base_active_prob:
                sessions = random.randint(1, 4)
                minutes = random.randint(3, 24)
                if language == "Kannada":
                    minutes = max(2, minutes - random.randint(2, 7))
                cur.execute(
                    "INSERT INTO daily_activity (user_id, activity_date, sessions, minutes_spent) VALUES (?, ?, ?, ?)",
                    (user_id, activity_date.isoformat(), sessions, minutes),
                )

        viewed_jobs = 1 if random.random() < 0.76 else 0
        completed_profile = 1 if random.random() < 0.62 else 0

        apply_rate = 0.31
        if language == "Kannada":
            apply_rate = 0.17
        if city in {"Mysore", "Patna", "Lucknow"}:
            apply_rate -= 0.04
        if completed_profile == 0:
            apply_rate -= 0.08

        applied_jobs = 1 if viewed_jobs and random.random() < max(0.05, apply_rate) else 0
        cur.execute(
            "INSERT INTO job_funnel (user_id, viewed_jobs, applied_jobs, completed_profile) VALUES (?, ?, ?, ?)",
            (user_id, viewed_jobs, applied_jobs, completed_profile),
        )

        for campaign in CAMPAIGNS:
            sent = 1
            open_rate = {"WhatsApp": 0.58, "Push Notification": 0.34, "SMS": 0.27}[campaign]
            click_rate = {"WhatsApp": 0.28, "Push Notification": 0.12, "SMS": 0.09}[campaign]
            conversion_rate = {"WhatsApp": 0.46, "Push Notification": 0.22, "SMS": 0.18}[campaign]

            if tier == "Tier-3" and campaign == "Push Notification":
                open_rate -= 0.11
                click_rate -= 0.05
                conversion_rate -= 0.10
            if language == "Kannada" and campaign != "WhatsApp":
                conversion_rate -= 0.06

            opened = 1 if random.random() < max(0.02, open_rate) else 0
            clicked = 1 if opened and random.random() < max(0.01, click_rate) else 0
            converted = 1 if clicked and random.random() < max(0.005, conversion_rate) else 0
            cur.execute(
                """
                INSERT INTO campaigns (user_id, campaign_type, sent, opened, clicked, converted)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user_id, campaign, sent, opened, clicked, converted),
            )

    conn.commit()
    conn.close()
    print(f"Seeded database at {DB_PATH}")


if __name__ == "__main__":
    seed()
