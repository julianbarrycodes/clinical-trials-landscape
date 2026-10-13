# Clinical Trials Landscape

An interactive dashboard exploring clinical trial activity across therapeutic areas, built on public data from the [ClinicalTrials.gov API](https://clinicaltrials.gov/data-api/api).

**Live app:** https://clinical-trials-landscape-jb.streamlit.app

<img width="1488" height="805" alt="image" src="https://github.com/user-attachments/assets/a7ecfc1d-cc11-4374-b654-89a9f66a6e3d" />

## Why this project

Pharma strategy, R&D and data teams regularly need a quick view of the clinical trial landscape: who is running trials, in which phases, and how activity is changing over time. This project builds that view end to end, from raw API data to a filterable dashboard, with explicit data quality checks along the way.

### User stories

- *As a life sciences strategy consultant,* I want to see how many trials are active per condition and phase, so I can size a therapeutic area quickly.
- *As a business development analyst,* I want to see the most active industry sponsors, so I can identify competitors and potential partners.
- *As a data steward,* I want to see which data quality issues were found and fixed, so I can trust the numbers.

## What it does

| Step | Script | What happens |
|------|--------|--------------|
| 1. Fetch | `fetch_more_trials.py` | Pulls trials for several conditions (diabetes, obesity, Alzheimer's, breast cancer) from the ClinicalTrials.gov API v2, following pagination. |
| 2. Clean & check | `clean_and_check.py` | Checks completeness, uniqueness, validity and consistency; normalises phases and sponsor types; parses mixed date formats; flags outliers. Outputs a data quality report. |
| 3. Store | `store_in_sqlite.py` | Loads the cleaned data into a small SQLite database with a trials table, a trial-to-condition link table and the data quality report. |
| 4. Visualise | `app.py` | Streamlit dashboard with filters (condition, phase, sponsor type, start year), KPIs, trends, top sponsors, the data quality report and a downloadable data table. |

## Tech stack

Python · pandas · requests · SQLite · Streamlit · Plotly

## Run it locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

To rebuild the data from scratch, run the scripts in order: `fetch_more_trials.py` → `clean_and_check.py` → `store_in_sqlite.py`.

## Notes and limitations

- Results reflect trials that match the API's condition search, so a trial can appear under more than one condition (handled via the link table).
- Data is a snapshot from the date it was fetched, not live.
- Built with AI-assisted development; design decisions, data quality rules and testing by the author.

## Author

Julian Barry · Life sciences engineer (EPFL MSc) · [LinkedIn](https://www.linkedin.com/in/julian-barry/)
