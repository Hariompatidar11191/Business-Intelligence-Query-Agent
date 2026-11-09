# AI Business Intelligence Query Agent

An AI-powered business analytics application that converts natural-language questions into SQLite queries using Gemini, executes them against a sales database, and presents the results as tables, charts, and short business insights.

## Features

- Natural-language-to-SQL with the Google Gemini API
- SQLite database querying
- Read-only SQL execution to protect the database
- Automatic chart selection with Matplotlib
- AI-generated business insights
- CSV and chart downloads
- Streamlit chat interface

## Technology

- Python
- Streamlit
- SQLite
- Pandas
- Matplotlib
- Google Gen AI SDK (`google-genai`)
- Gemini 3.8 Flash (`gemini-3.8-flash`)

## Project files

```
.
├── app.py
├── requirements.txt
├── sales.db
├── sales_data_sample.csv
└── README.md
```

## Run locally

1. Create and activate a Python virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create `.streamlit/secrets.toml`:

   ```toml
   GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
   ```

   Alternatively, set the `GEMINI_API_KEY` environment variable.

4. Start the app:

   ```bash
   streamlit run app.py
   ```

## Deploy on Streamlit Community Cloud

1. Connect this GitHub repository to Streamlit Community Cloud.
2. Set the app entry point to `app.py`.
3. Open **App settings → Secrets**.
4. Add the following TOML secret and save:

   ```toml
   GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
   ```

5. Streamlit will install packages from `requirements.txt` and redeploy the app.

Never commit your API key or `.streamlit/secrets.toml` to GitHub. If an API key was exposed, revoke it and generate a replacement in Google AI Studio.

## Example questions

- What is the total sales revenue?
- Show sales by product line.
- Which country generates the highest revenue?
- Show monthly sales trends.
- Which customers have generated the highest sales?

## Model configuration

The app defaults to the stable model ID `gemini-3.8-flash`. To select another supported Gemini model, set the `GEMINI_MODEL` environment variable or Streamlit secret and confirm the model is enabled for your API key.

## Data protection

The app opens `sales.db` in read-only mode and accepts only read-only SQL queries. Keep a backup of your database before changing or replacing it.
