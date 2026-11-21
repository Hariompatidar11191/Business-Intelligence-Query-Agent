# AI Business Intelligence Query Agent

An AI-powered business intelligence application that converts natural-language questions into SQL queries, executes them against a local SQLite sales database, and presents results through interactive tables, automatic visualizations, and CSV exports.

Built using Python, Streamlit, SQLite, and LLM APIs, the application helps users explore business data without writing SQL manually.

## Features

- **Natural Language to SQL:** Convert business questions into executable SQLite queries using LLMs.
- **Multiple AI Providers:** OpenRouter as the primary provider, with Cloudflare Workers AI as an additional provider when configured.
- **Model Fallback:** Automatically attempts a secondary OpenRouter model if the primary model fails.
- **Multi-Question Processing:** Process up to four independent questions in a single prompt.
- **Read-Only SQL Execution:** Restrict database operations to prevent modifications.
- **Query Protection:** Validate SQL, restrict access to sensitive columns, limit returned rows, and enforce query timeouts.
- **Automatic Visualizations:** Generate suitable charts based on query results using Matplotlib.
- **CSV Export:** Download query results for further analysis.
- **Persistent Chat History:** Store conversation history and generated SQL locally using SQLite.
- **Error Handling:** Retry failed SQL generation once before moving to the next AI provider.

## Technology Stack

- Python 3.10+
- Streamlit
- SQLite
- Pandas
- Matplotlib
- OpenRouter API
- Cloudflare Workers AI (optional)

## AI Model Configuration

The application supports multiple AI providers.

| Priority | Provider | Model |
|---|---|---|
| Primary | OpenRouter | `particle-ai/particle-1:free` |
| Fallback | OpenRouter | `openrouter/free` |
| Additional fallback | Cloudflare Workers AI | Configurable models |

The application attempts providers in sequence. If a provider fails, it tries the next configured provider.

The OpenRouter Free Router dynamically selects an available free model, so its underlying model may change.

## Project Structure

```text
Business-Intelligence-Query-Agent/
│
├── app.py
├── create_database.py
├── verify_database.py
├── sales_data_sample.csv
├── requirements.txt
├── .gitignore
└── README.md
```

**Generated local files (not committed to GitHub):**

- `sales.db` – SQLite database generated from the CSV dataset.
- `chat_memory.db` – Stores conversation history and generated SQL.
- `chart_*.png` – Locally generated chart files, if applicable.

## Installation and Local Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd Business-Intelligence-Query-Agent
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Generate the SQLite database

The generated database is excluded from GitHub. Create it locally using the supplied CSV file:

```bash
python create_database.py
```

### 5. Verify the database

```bash
python verify_database.py
```

### 6. Configure API credentials

The application supports environment variables and Streamlit secrets.

Required OpenRouter configuration:

```toml
OPENROUTER_API_KEY = "YOUR_OPENROUTER_API_KEY"
OPENROUTER_MODEL = "particle-ai/particle-1:free"
OPENROUTER_FALLBACK_MODEL = "openrouter/free"
```

Optional Cloudflare configuration:

```toml
CLOUDFLARE_ACCOUNT_ID = "YOUR_CLOUDFLARE_ACCOUNT_ID"
CLOUDFLARE_API_TOKEN = "YOUR_CLOUDFLARE_API_TOKEN"
CLOUDFLARE_AI_MODEL = "@cf/qwen/qwen2.5-coder-32b-instruct"
CLOUDFLARE_FALLBACK_MODELS = "@cf/meta/llama-3.3-70b-instruct-fp8-fast,@cf/meta/llama-3.1-8b-instruct"
```

Only configure Cloudflare if you have the required credentials.

### 7. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

## Example Business Questions

- What is the total sales revenue?
- Which product line generates the highest revenue?
- Show sales by country.
- What are the monthly sales trends?
- Compare revenue across deal sizes.
- Which product lines have the highest average order value?

## Database Security and Data Protection

The application incorporates several safeguards:

- Opens the sales database in read-only mode.
- Restricts SQL execution to permitted `SELECT` and `WITH` queries.
- Uses a SQLite authorizer to restrict access to the intended sales table and block specified sensitive columns.
- Limits query results to 5,000 rows.
- Uses a query timeout to prevent excessively long-running queries.
- Prevents database modification through generated SQL.

The LLM receives the user's question, relevant schema and category context, and conversation context needed to generate SQL. Query results are processed locally and are not sent to the AI provider by the application's normal query workflow.

Conversation history and SQL are stored locally in a separate SQLite database.

## Deployment on Streamlit Community Cloud

1. Push the project to your GitHub repository.
2. Visit [Streamlit Community Cloud](https://share.streamlit.io/).
3. Sign in using GitHub.
4. Select **Create app** and choose your existing repository.
5. Set the branch to `main`.
6. Set the main file path to `app.py`.
7. Open **App settings → Secrets**.
8. Add your OpenRouter credentials using the TOML configuration shown above.
9. Add Cloudflare credentials if you intend to use that provider.
10. Save and deploy the application.

### Database initialization

Because `sales.db` is excluded from GitHub, the deployment must create it from `sales_data_sample.csv` before the application attempts to access it.

Configure the deployment to run:

```bash
python create_database.py
```

before starting the Streamlit application, or modify the application startup process to initialize the database automatically.

**Note:** Streamlit Community Cloud's local filesystem is not guaranteed to provide permanent storage across restarts and redeployments. The locally stored chat history may therefore not persist indefinitely.

## Future Improvements

- Add business KPI dashboards.
- Implement year-over-year and month-over-month analysis.
- Introduce sales forecasting.
- Add SQL query validation and automated test coverage.
- Support additional database systems.
- Improve business insight generation and reporting.

## Author

Developed as a practical AI-powered Business Intelligence project demonstrating natural-language SQL generation, database security, automated data visualization, and LLM integration.
