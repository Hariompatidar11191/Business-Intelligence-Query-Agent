import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import google.generativeai as genai
import os

# -----------------------------
# Gemini setup
# -----------------------------

# Read API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-3-flash-preview")
# -----------------------------
# Streamlit config
# -----------------------------
st.set_page_config(page_title="AI BI Agent", layout="wide")
st.title("AI Business Intelligence Chat Agent")

# -----------------------------
# Database connection
# -----------------------------
conn = sqlite3.connect("sales.db")

# -----------------------------
# Run multiple SQL statements
# -----------------------------
def run_multiple_sql(sql_text):
    queries = [q.strip() for q in sql_text.split(";") if q.strip()]
    results = []

    for q in queries:
        try:
            df = pd.read_sql(q, conn)
            results.append((q, df))
        except Exception as e:
            results.append((q, str(e)))

    return results

# -----------------------------
# Text to SQL (Gemini)
# -----------------------------
def text_to_sql(user_query):
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
    Convert the following question into valid SQLite SQL.

    Rules:
    - Use only table: sales_data
    - Use only provided columns
    - You may return one or more SQL statements
    - Separate multiple queries using semicolons
    - Do not explain anything

    {schema}

    Question:
    {user_query}
    """

    response = model.generate_content(prompt)
    return response.text.strip()

# -----------------------------
# Auto chart selection
# -----------------------------
def auto_chart(df):
    if len(df.columns) < 2:
        return None

    x = df.columns[0]
    y = df.columns[1]

    if "year" in x.lower() or "month" in x.lower():
        return ("line", x, y)

    return ("bar", x, y)

# -----------------------------
# AI Insights
# -----------------------------
def generate_insights(df, question):
    summary = df.head(10).to_string()

    prompt = f"""
    You are a business analyst.

    The user asked:
    {question}

    Here is the result data:
    {summary}

    Provide 2–3 short business insights.
    """

    response = model.generate_content(prompt)
    return response.text

# -----------------------------
# Chat memory
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# -----------------------------
# Chat input
# -----------------------------
user_query = st.chat_input("Ask a business question...")

if user_query:
    # Show user message
    st.session_state.messages.append(
        {"role": "user", "content": user_query}
    )
    with st.chat_message("user"):
        st.write(user_query)

    # Generate SQL
    with st.spinner("Generating SQL..."):
        sql_query = text_to_sql(user_query)

    with st.chat_message("assistant"):
        st.subheader("Generated SQL")
        st.code(sql_query, language="sql")

        # Run SQL
        results = run_multiple_sql(sql_query)

        for i, (query, result) in enumerate(results, 1):
            st.subheader(f"Result {i}")
            st.code(query, language="sql")

            if isinstance(result, pd.DataFrame):
                st.dataframe(result, use_container_width=True)

                # -----------------------------
                # Auto chart
                # -----------------------------
                chart = auto_chart(result)
                fig = None

                if chart:
                    chart_type, x, y = chart
                    fig, ax = plt.subplots()

                    if chart_type == "line":
                        result.plot(kind="line", x=x, y=y, ax=ax)
                    else:
                        result.plot(kind="bar", x=x, y=y, ax=ax)

                    st.pyplot(fig)

                # -----------------------------
                # AI Insights
                # -----------------------------
                with st.spinner("Generating insights..."):
                    insights = generate_insights(result, user_query)

                st.subheader("AI Insights")
                st.write(insights)

                # -----------------------------
                # Export options
                # -----------------------------
                st.subheader("Download Report")

                # CSV download
                csv = result.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"report_{i}.csv",
                    mime="text/csv"
                )

                # Chart download
                if fig:
                    chart_path = f"chart_{i}.png"
                    fig.savefig(chart_path)

                    with open(chart_path, "rb") as file:
                        st.download_button(
                            label="Download Chart",
                            data=file,
                            file_name=f"chart_{i}.png",
                            mime="image/png"
                        )

            else:
                st.error(result)

    # Save assistant response
    st.session_state.messages.append(
        {"role": "assistant", "content": "Response generated"}
    )

conn.close()
