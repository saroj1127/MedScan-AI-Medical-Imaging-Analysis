# MedScan-AI-Medical-Imaging-Analysis

**BBIS 7502 Applied Project**
ICL Graduate Business School, Auckland, New Zealand

**Student:** Saroj Kumar Tamang

> ⚠️ **Warning:** This system is not a medical device. It has not been clinically validated. Do not use it for real clinical decisions.

---

## What You Need First

- Python 3.10 or above
- MySQL 8.0, installed and running on your computer
- A Google account for OAuth login
- A Google Gemini API key from https://aistudio.google.com
- Google OAuth credentials from https://console.cloud.google.com

---

## Setup Instructions

### Step 1: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Add your Gemini API key

Open `app.py` and replace:

```python
api_key = "YOUR_GEMINI_API_KEY"
```

### Step 3: Add your database password

Open `app.py` and replace:

```python
password = "YOUR_DB_PASSWORD"
```

### Step 4: Set up Google OAuth

1. Copy `secrets.toml` to `.streamlit/secrets.toml`.
2. Fill in `YOUR_GOOGLE_CLIENT_ID` and `YOUR_GOOGLE_CLIENT_SECRET`.
3. In Google Cloud Console, add `http://localhost:8501/oauth2callback` as an authorised redirect URI.

### Step 5: Set up the database

```bash
mysql -u root -p < database_setup.sql
```

### Step 6: Run the application

```bash
streamlit run app.py
```

### Step 7: Open the application

Open your browser and go to http://localhost:8501

---

## File Structure

| File | Description |
|------|-------------|
| `app.py` | Main application file |
| `requirements.txt` | Python dependencies |
| `secrets.toml` | OAuth credentials template (no real keys inside) |
| `database_setup.sql` | MySQL database setup script |
| `code_change_summary.pdf` | Summary of changes from the baseline |
| `Spreadsheet_testing.xlsx` | Full testing results |
| `README.pdf` | Run instructions (PDF copy) |

---

## Baseline Source

- **Repository:** https://github.com/simranjeet97/Awsome_AI_Agents
- **Author:** Simranjeet Singh (simranjeet97)
- **Folder:** `GenAI_Medical_Imaging_Agent`
- **Licence:** Apache 2.0

---

## Important Notes

- The Gemini 2.5 Flash free tier allows 20 requests per day.
- API keys and OAuth secrets are not included in this repository, for security reasons.
- All testing used public, de-identified proxy datasets from Kaggle.
- No real patient data was used at any point in this project.
