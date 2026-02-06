import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import google.generativeai as genai

# -----------------------------
# Gemini setup
# -----------------------------
GEMINI_API_KEY = "AIzaSyC1Uv1HfygRtOP9OlzDdMm5cFv7FiGJxF0"
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-3-flash-preview")

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="AI BI Agent", layout="wide")
st.title("AI Business Intelligence Query Agent")

# Connect database
conn = sqlite3.connect("sales.db")

def run_sql(sql):
    try:
        return pd.read_sql(sql, conn)
    except Exception as e:
        st.error(f"SQL Error: {e}")
        return None

# -----------------------------
# AI: Text → SQL using Gemini
# -----------------------------
def text_to_sql(user_query):
    schema = """
    Table: sales_data

    Columns:
    ORDERNUMBER
    QUANTITYORDERED
    PRICEEACH
    ORDERLINENUMBER
    SALES
    ORDERDATE
    STATUS
    QTR_ID
    MONTH_ID
    YEAR_ID
    PRODUCTLINE
    MSRP
    PRODUCTCODE
    CUSTOMERNAME
    PHONE
    ADDRESSLINE1
    ADDRESSLINE2
    CITY
    STATE
    POSTALCODE
    COUNTRY
    TERRITORY
    CONTACTLASTNAME
    CONTACTFIRSTNAME
    DEALSIZE
    """

    prompt = f"""
    You are an expert SQL generator.

    Convert the user question into a valid SQLite SQL query.

    Rules:
    - Use only table: sales_data
    - Use only the columns listed
    - Return ONLY the SQL query
    - No explanation
    - SQLite syntax only

    {schema}

    Question:
    {user_query}
    """

    response = model.generate_content(prompt)
    sql = response.text.strip()

    return sql

# -----------------------------
# User input
# -----------------------------
query = st.text_input("Ask any business question:")

if query:
    with st.spinner("Generating SQL using Gemini..."):
        sql_query = text_to_sql(query)

    st.subheader("Generated SQL")
    st.code(sql_query, language="sql")

    result = run_sql(sql_query)

    if result is not None:
        st.subheader("Results")
        st.dataframe(result, use_container_width=True)

        # Plot if suitable
        if len(result.columns) >= 2 and len(result) > 1:
            fig, ax = plt.subplots()
            result.plot(kind="bar", x=result.columns[0], y=result.columns[1], ax=ax)
            st.pyplot(fig)

conn.close()
