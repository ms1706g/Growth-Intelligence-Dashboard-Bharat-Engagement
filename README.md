# Growth Intelligence Dashboard for Bharat User Engagement

A simple student-level Streamlit prototype for the Lokal AI Strategy Internship.

It uses Python, SQLite, SQL, Pandas, Plotly, Streamlit, and Gemini API support to help product and growth teams identify engagement problems across Bharat user segments.

## Setup

```bash
pip install -r requirements.txt
python seed_data.py
streamlit run app.py --server.port 8503
```

Open:

```text
http://localhost:8503
```

## Gemini API

The dashboard works without an API key using a realistic fallback insight.

To enable Gemini:

```bash
set GEMINI_API_KEY=your_key_here
```

On macOS/Linux:

```bash
export GEMINI_API_KEY=your_key_here
```

## Project Structure

```text
growth-intelligence-dashboard/
  app.py
  seed_data.py
  requirements.txt
  README.md
  data/
    lokal_growth.db
```

