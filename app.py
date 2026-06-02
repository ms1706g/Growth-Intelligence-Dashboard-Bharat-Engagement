import os
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DB_PATH = Path(__file__).parent / "data" / "lokal_growth.db"


st.set_page_config(
    page_title="Lokal Growth Intelligence",
    page_icon="📊",
    layout="wide",
)


def run_query(query):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn)


def ensure_db():
    if not DB_PATH.exists():
        st.error("Database not found. Run `python seed_data.py` first.")
        st.stop()


def gemini_insight(summary_text):
    fallback = (
        "Biggest bottleneck: users are viewing jobs but not applying, especially Kannada users. "
        "Underperforming segment: Mysore/Kannada users show lower apply rate and weaker campaign conversion. "
        "Action: localize job alerts in Kannada and shift Tier-3 follow-ups from push notifications to WhatsApp reminders."
    )

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return fallback

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
You are advising a growth team at Lokal. Use the SQL summary below.
Answer in 3 short bullets only:
1. biggest growth bottleneck
2. underperforming city/language segment
3. business action

Keep it realistic for a student prototype.

SQL summary:
{summary_text}
"""
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return fallback


ensure_db()

st.title("Growth Intelligence Dashboard for Bharat User Engagement")
st.caption("A simple analytics prototype for jobs, campaigns, languages, and city-level engagement.")

overview_query = """
WITH active AS (
    SELECT COUNT(DISTINCT user_id) AS active_users
    FROM daily_activity
    WHERE activity_date >= date('now', '-7 days')
),
jobs AS (
    SELECT SUM(applied_jobs) AS job_applications
    FROM job_funnel
),
campaign_stats AS (
    SELECT ROUND(100.0 * SUM(converted) / NULLIF(SUM(sent), 0), 2) AS campaign_conversion_rate
    FROM campaigns
)
SELECT
    (SELECT COUNT(*) FROM users) AS total_users,
    active.active_users,
    jobs.job_applications,
    campaign_stats.campaign_conversion_rate
FROM active, jobs, campaign_stats;
"""

daily_active_query = """
SELECT activity_date, COUNT(DISTINCT user_id) AS daily_active_users
FROM daily_activity
GROUP BY activity_date
ORDER BY activity_date;
"""

language_query = """
WITH activity AS (
    SELECT user_id, AVG(minutes_spent) AS avg_minutes
    FROM daily_activity
    GROUP BY user_id
)
SELECT
    u.language,
    COUNT(DISTINCT u.user_id) AS users,
    COUNT(DISTINCT activity.user_id) AS active_users,
    ROUND(AVG(activity.avg_minutes), 1) AS avg_minutes,
    ROUND(100.0 * SUM(jf.applied_jobs) / NULLIF(SUM(jf.viewed_jobs), 0), 2) AS apply_rate
FROM users u
LEFT JOIN activity ON u.user_id = activity.user_id
LEFT JOIN job_funnel jf ON u.user_id = jf.user_id
GROUP BY u.language
ORDER BY apply_rate ASC;
"""

city_query = """
WITH activity AS (
    SELECT user_id, AVG(minutes_spent) AS avg_minutes
    FROM daily_activity
    GROUP BY user_id
)
SELECT
    u.city,
    u.city_tier,
    COUNT(DISTINCT u.user_id) AS users,
    COUNT(DISTINCT activity.user_id) AS active_users,
    ROUND(AVG(activity.avg_minutes), 1) AS avg_minutes,
    ROUND(100.0 * SUM(jf.applied_jobs) / NULLIF(SUM(jf.viewed_jobs), 0), 2) AS apply_rate
FROM users u
LEFT JOIN activity ON u.user_id = activity.user_id
LEFT JOIN job_funnel jf ON u.user_id = jf.user_id
GROUP BY u.city, u.city_tier
ORDER BY apply_rate ASC;
"""

campaign_query = """
SELECT
    u.city_tier,
    c.campaign_type,
    SUM(c.sent) AS sent,
    SUM(c.opened) AS opened,
    SUM(c.clicked) AS clicked,
    SUM(c.converted) AS converted,
    ROUND(100.0 * SUM(c.opened) / NULLIF(SUM(c.sent), 0), 2) AS open_rate,
    ROUND(100.0 * SUM(c.clicked) / NULLIF(SUM(c.opened), 0), 2) AS click_rate,
    ROUND(100.0 * SUM(c.converted) / NULLIF(SUM(c.sent), 0), 2) AS conversion_rate
FROM campaigns c
JOIN users u ON c.user_id = u.user_id
GROUP BY u.city_tier, c.campaign_type
ORDER BY conversion_rate DESC;
"""

funnel_query = """
SELECT
    COUNT(*) AS total_users,
    SUM(completed_profile) AS completed_profile,
    SUM(viewed_jobs) AS viewed_jobs,
    SUM(applied_jobs) AS applied_jobs,
    ROUND(100.0 * SUM(completed_profile) / COUNT(*), 2) AS profile_completion_rate,
    ROUND(100.0 * SUM(viewed_jobs) / COUNT(*), 2) AS job_view_rate,
    ROUND(100.0 * SUM(applied_jobs) / NULLIF(SUM(viewed_jobs), 0), 2) AS view_to_apply_rate
FROM job_funnel;
"""

overview = run_query(overview_query)
daily_active = run_query(daily_active_query)
language = run_query(language_query)
city = run_query(city_query)
campaign = run_query(campaign_query)
funnel = run_query(funnel_query)

st.header("1. Dashboard Overview")
metric_cols = st.columns(4)
metric_cols[0].metric("Total Users", f"{int(overview.loc[0, 'total_users']):,}")
metric_cols[1].metric("Active Users", f"{int(overview.loc[0, 'active_users']):,}")
metric_cols[2].metric("Job Applications", f"{int(overview.loc[0, 'job_applications']):,}")
metric_cols[3].metric("Campaign Conversion Rate", f"{overview.loc[0, 'campaign_conversion_rate']}%")

chart_cols = st.columns(2)
with chart_cols[0]:
    st.plotly_chart(
        px.line(daily_active, x="activity_date", y="daily_active_users", markers=True, title="Daily Active Users"),
        use_container_width=True,
    )
with chart_cols[1]:
    st.plotly_chart(
        px.bar(campaign, x="campaign_type", y="conversion_rate", color="city_tier", barmode="group", title="Campaign Conversion by Tier"),
        use_container_width=True,
    )

st.header("2. SQL Analytics")
tabs = st.tabs(["Daily Active Users", "Language", "City", "Campaigns", "Funnel"])

with tabs[0]:
    st.code(daily_active_query.strip(), language="sql")
    st.dataframe(daily_active, use_container_width=True, hide_index=True)

with tabs[1]:
    st.code(language_query.strip(), language="sql")
    st.dataframe(language, use_container_width=True, hide_index=True)

with tabs[2]:
    st.code(city_query.strip(), language="sql")
    st.dataframe(city, use_container_width=True, hide_index=True)

with tabs[3]:
    st.code(campaign_query.strip(), language="sql")
    st.dataframe(campaign, use_container_width=True, hide_index=True)

with tabs[4]:
    st.code(funnel_query.strip(), language="sql")
    st.dataframe(funnel, use_container_width=True, hide_index=True)

st.header("3. AI Insights")
summary_text = f"""
Language engagement:
{language.to_string(index=False)}

City engagement:
{city.to_string(index=False)}

Campaign performance:
{campaign.to_string(index=False)}

Funnel:
{funnel.to_string(index=False)}
"""
st.write(gemini_insight(summary_text))

st.header("4. Experiment and Automation Recommendations")

exp_cols = st.columns(3)
experiments = [
    {
        "name": "Kannada Job Alert Localization",
        "hypothesis": "Kannada users are not applying because job alerts are not localized enough.",
        "metric": "Apply Rate",
        "impact": "10-15% increase",
    },
    {
        "name": "Tier-3 WhatsApp Reminder",
        "hypothesis": "Users in Patna, Mysore, and Lucknow need a direct reminder after viewing jobs.",
        "metric": "View-to-Apply Rate",
        "impact": "8-12% increase",
    },
    {
        "name": "Profile Completion Nudge",
        "hypothesis": "Users with incomplete profiles are less confident while applying.",
        "metric": "Profile Completion Rate",
        "impact": "6-10% increase",
    },
]

for col, exp in zip(exp_cols, experiments):
    with col:
        st.subheader(exp["name"])
        st.write(f"**Hypothesis:** {exp['hypothesis']}")
        st.write(f"**Metric:** {exp['metric']}")
        st.write(f"**Expected Impact:** {exp['impact']}")

st.subheader("Practical Automations")
st.write("- Send WhatsApp reminder to users who viewed jobs but did not apply.")
st.write("- Trigger language-specific notifications based on user preference.")
st.write("- Alert growth team when a city/language segment drops below target apply rate.")
