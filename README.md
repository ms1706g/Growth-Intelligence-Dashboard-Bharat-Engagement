# Growth Intelligence Dashboard for Bharat User Engagement

## Overview

Growth Intelligence Dashboard is a product analytics and growth strategy prototype built to help teams analyze user engagement, campaign effectiveness, localization opportunities, and experimentation strategies across Bharat-focused applications.

The project simulates real-world growth and product decision-making for platforms operating in Tier-2 and Tier-3 India.

---

## Problem Statement

Growth teams often struggle to identify:

- Which user segments are underperforming
- Which campaigns drive the highest conversions
- Which regions or languages require localization
- What experiments should be prioritized
- How operational workflows can be automated

This dashboard provides SQL-driven analytics combined with AI-generated recommendations to support data-driven growth decisions.

---

## Features

### Dashboard Overview

- Total Users
- Active Users
- Job Applications
- Campaign Conversion Rate
<img width="1890" height="497" alt="Screenshot 2026-06-02 065429" src="https://github.com/user-attachments/assets/be707444-a045-4ffd-89b1-b636b1c758ff" />


### SQL Analytics

- Daily Active Users (DAU)
- Language-wise Engagement Analysis
- City-wise Performance Analysis
- Campaign Conversion Tracking
- Funnel Analysis
<img width="1891" height="868" alt="Screenshot 2026-06-02 065500" src="https://github.com/user-attachments/assets/145fcd79-eafa-48c5-8123-d5f2b39a2587" />


### AI Insights

Gemini AI analyzes engagement and campaign data to:

- Identify growth bottlenecks
- Detect underperforming segments
- Recommend business actions

- <img width="1890" height="864" alt="Screenshot 2026-06-02 065448" src="https://github.com/user-attachments/assets/8192cdb3-1843-4579-8fe7-30cfbaa04c57" />


### Experiment Recommendations

Examples:

- Kannada Job Alert Localization
- Tier-3 WhatsApp Reminder Campaign
- Profile Completion Nudge

### Automation Recommendations

- WhatsApp reminders for users who viewed jobs but did not apply
- Language-specific notification workflows
- Automated alerts for underperforming city/language segments
<img width="1917" height="857" alt="Screenshot 2026-06-02 065512" src="https://github.com/user-attachments/assets/0e54c8c9-5071-4c07-a752-c51b0a3b385c" />


---

## Tech Stack

- Python
- SQL
- SQLite
- Streamlit
- Pandas
- Plotly
- Gemini AI

---

## Dataset Design

The synthetic dataset models user behavior across Bharat-focused applications.

### Cities

- Jaipur
- Indore
- Patna
- Mysore
- Lucknow
- Bangalore

### Languages

- Hindi
- Kannada
- Telugu
- Tamil
- English

### Business Assumptions

- Kannada users have lower job application rates
- Tier-3 users engage less with push notifications
- WhatsApp campaigns outperform SMS and Push Notifications

These assumptions are intentionally modeled to simulate realistic growth challenges.

---

## Project Structure

growth-intelligence-dashboard/

├── app.py

├── seed_data.py

├── requirements.txt

├── README.md

└── data/

    └── lokal_growth.db

---

## Installation

```bash
pip install -r requirements.txt
python seed_data.py
streamlit run app.py
