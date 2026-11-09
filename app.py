import os
import re
import sqlite3
from contextlib import closing
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from google import genai

# -----------------------------
# Streamlit configuration
# -----------------------------
st.set_page_config(page_title="AI BI Agent", layout="wide")
st.title("AI Business Intelligence Chat Agent")

# -----------------------------
# Gemini configuration
# -----------------------------
def get_api_key():
    """Read the key from Streamlit Secrets, with env-var fallback for local use."""
    try:
        key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        key = None
    return key or os.getenv("GEMINI_API_KEY")


GEMINI_API_KEY = get_api_key()
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

if not GEMINI_API_KEY:
    st.error(
        "Gemini API key is missing. Add GEMINI_API_KEY to "
        "Streamlit Community Cloud → App settings → Secrets."
    )
    st.stop()

client = genai.Client(api_key=GEMINI_API_KEY)


def generate_text(prompt: str) -> str:
    """Call Gemini through the supported Google Gen AI SDK."""
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )
    text = response.text
    if not text:
        raise RuntimeError("Gemini returned an empty response. Please retry.")
    return text.strip()


# -----------------------------
# Database connection
# -----------------------------
DB_PATH = Path(__file__).resolve().parent / "sales.db"
if not DB_PATH.exists():
    st.error(
        "sales.db was not found. Make sure the database file is present "
        "in the repository root alongside app.py."
    )
    st.stop()


def get_connection():
    # Query-only mode protects the committed sales database from AI-generated writes.
    uri = f"file:{DB_PATH.as_posix()}?mode=ro"
    connection = sqlite3.connect(uri, uri=True, check_same_thread=False)
    connection.execute("PRAGMA query_only = ON")
    return connection


# -----------------------------
# SQL execution (read-only)
# -----------------------------
def run_multiple_sql(sql_text: str):
    # Remove optional Markdown fences returned by the model.
    cleaned = re.sub(r"`{3}(?:sql)?", "", sql_text, flags=re.IGNORECASE).strip()
    queries = [query.strip() for query in cleaned.split(";") if query.strip()]
    results = []

    if not queries:
        return [("", "Gemini did not generate a SQL query.")]

    with closing(get_connection()) as conn:
        for query in queries:
            # Only allow read-only SELECT / WITH queries.
            if not re.match(r"^(SELECT|WITH)\b", query, flags=re.IGNORECASE):
                results.append((query, "Only read-only SELECT queries are allowed."))
                continue
            try:
                df = pd.read_sql_query(query, conn)
                results.append((query, df))
            except Exception as exc:
                results.append((query, f"{type(exc).__name__}: {exc}"))

    return results


# -----------------------------
# Text to SQL (Gemini)
# -----------------------------
def text_to_sql(user_query: str) -> str:
    schema = """
    Table: sales_data
    Columns:
    ORDERNUMBER, QUANTITYORDERED, PRICEEACH, ORDERLINENUMBER,
    SALES, ORDERDATE, STATUS, QTR_ID, MONTH_ID, YEAR_ID,
    PRODUCTLINE, MSRP, PRODUCTCODE, CUSTOMERNAME, PHONE,
    ADDRESSLINE1, ADDRESSLINE2, CITY, STATE, POSTALCODE,
    COUNTRY, TERRITORY, CONTACTLASTNAME, CONTACTFIRSTNAME,
    DEALSIZE
    """

    prompt = f"""
You are a careful SQLite business intelligence analyst.
Convert the user's question into valid SQLite SQL.

Rules:
- Use only the table sales_data and the listed columns.
- Return only SQL, without Markdown fences or explanations.
- Generate read-only SELECT statements only. CTEs beginning with WITH are allowed.
- Never generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, PRAGMA, ATTACH,
  DETACH, or any other data-modifying or database-management statement.
- Prefer clear aliases for calculated columns.
- For top-N questions, use an appropriate ORDER BY and LIMIT.
- For date grouping, use SQLite-compatible date functions.
- Return one SQL statement unless multiple independent result sets are essential.

{schema}

Question:
{user_query}
"""
    return generate_text(prompt)


# -----------------------------
# Automatic chart selection
# -----------------------------
def auto_chart(df: pd.DataFrame):
    if len(df.columns) < 2 or df.empty:
        return None

    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    if not numeric_columns:
        return None

    x = df.columns[0]
    y = numeric_columns[0]
    x_name = str(x).lower()

    if any(word in x_name for word in ("year", "month", "date", "quarter")):
        return ("line", x, y)
    return ("bar", x, y)


# -----------------------------
# AI insights
# -----------------------------
def generate_insights(df: pd.DataFrame, question: str) -> str:
    summary = df.head(15).to_string(index=False)
    prompt = f"""
You are a concise business analyst.
The user's question: {question}

SQL result (up to 15 rows):
{summary}

Provide 2–3 concise, evidence-based business insights.
Do not invent values or claim trends that are not visible in the result.
If the result is empty, say that no matching records were found.
"""
    return generate_text(prompt)


# -----------------------------
# Chat memory
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


# -----------------------------
# Chat input and response
# -----------------------------
user_query = st.chat_input("Ask a business question...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.write(user_query)

    try:
        with st.spinner(f"Generating SQL with {MODEL_NAME}..."):
            sql_query = text_to_sql(user_query)

        with st.chat_message("assistant"):
            st.subheader("Generated SQL")
            st.code(sql_query, language="sql")

            results = run_multiple_sql(sql_query)
            assistant_summary = []

            for index, (query, result) in enumerate(results, start=1):
                st.subheader(f"Result {index}")
                if query:
                    st.code(query, language="sql")

                if isinstance(result, pd.DataFrame):
                    st.dataframe(result, use_container_width=True)
                    assistant_summary.append(
                        f"Result {index}: {len(result)} row(s) returned."
                    )

                    fig = None
                    chart = auto_chart(result)
                    if chart:
                        chart_type, x_col, y_col = chart
                        fig, ax = plt.subplots(figsize=(10, 5))
                        result.plot(
                            kind=chart_type,
                            x=x_col,
                            y=y_col,
                            ax=ax,
                            legend=False,
                        )
                        ax.set_title(f"{y_col} by {x_col}")
                        ax.set_xlabel(str(x_col))
                        ax.set_ylabel(str(y_col))
                        fig.tight_layout()
                        st.pyplot(fig)
                    else:
                        st.info("A chart is not available for this result.")

                    with st.spinner("Generating business insights..."):
                        insights = generate_insights(result, user_query)
                    st.subheader("AI Insights")
                    st.write(insights)

                    st.subheader("Download Report")
                    csv_data = result.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name=f"report_{index}.csv",
                        mime="text/csv",
                        key=f"csv_{len(st.session_state.messages)}_{index}",
                    )

                    if fig is not None:
                        image_bytes = None
                        from io import BytesIO
                        buffer = BytesIO()
                        fig.savefig(buffer, format="png", dpi=160, bbox_inches="tight")
                        image_bytes = buffer.getvalue()
                        st.download_button(
                            label="Download Chart",
                            data=image_bytes,
                            file_name=f"chart_{index}.png",
                            mime="image/png",
                            key=f"chart_{len(st.session_state.messages)}_{index}",
                        )
                        plt.close(fig)
                else:
                    st.error(result)
                    assistant_summary.append(f"Result {index}: {result}")

        st.session_state.messages.append(
            {"role": "assistant", "content": "\n".join(assistant_summary) or "Response generated."}
        )

    except Exception as exc:
        error_message = f"Unable to complete the request: {type(exc).__name__}: {exc}"
        st.error(error_message)
        st.session_state.messages.append(
            {"role": "assistant", "content": error_message}
        )
