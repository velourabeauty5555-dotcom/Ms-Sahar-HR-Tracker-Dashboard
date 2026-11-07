# Ms Sahar - HR Tracker Dashboard

A Streamlit app for keeping track of HR client contacts, communication status, and follow-up dates.

## Features

- Add client contact details, including optional CC email addresses.
- Track contact dates, job positions, status, follow-up dates, and notes.
- Search client records by client, company, email, or phone.
- View dashboard totals and follow-up reminders.
- Import client records from an `.xlsx` Excel workbook. Existing records are kept, and duplicate email addresses are skipped.
- Upload and download PDF documents linked to each client. PDF files are stored in the `client_documents` folder beside the tracker database.
- Download a PDF report with client details, follow-up status, and linked PDF documents.
- Download client records as a CSV file.
- Save records in a local SQLite database (`hr_clients.db`).

## Run on Windows

1. Install Python 3.9 or later from [python.org](https://www.python.org/downloads/). During setup, enable **Add Python to PATH**.
2. Extract the downloaded ZIP file.
3. Double-click `run_tracker.bat`. On its first run, it creates a private virtual environment and installs the required packages.
4. Open the local URL printed in the terminal. Keep the terminal window open while using the app.

The SQLite database (`hr_clients.db`) is created in the app folder the first time the app runs. Keep that file to preserve client records, and do not share it unless you intend to share those records.

## Run manually

Install the requirements and start Streamlit:

```bash
python -m pip install -r requirements.txt
python -m streamlit run TRACKER.py
```







