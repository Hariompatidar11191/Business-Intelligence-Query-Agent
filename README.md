# Business-Intelligence-Query-Agent

# AI Business Intelligence Query Agent

An AI-powered business analytics tool that converts natural language queries into SQL, executes them on a sales database, and displays results as tables and charts.

## Features
- Natural language to SQL using Gemini API
- Automatic data retrieval from SQLite database
- Interactive charts and tables
- Streamlit web interface

## Example Queries
- Total sales
- Sales by country
- Top customers by sales
- Monthly sales in 2004
- Average price by productline

## Tech Stack
- Python
- Streamlit
- SQLite
- Gemini API
- Pandas
- Matplotlib

## Run Locally
Install dependencies:


AI Business Intelligence Query Agent

An AI-powered analytics tool that converts natural language questions into SQL queries using the Google Gemini API, executes them on a sales database, and displays results as interactive tables and charts.

This project demonstrates how large language models can be used to build intelligent business analytics systems without manually writing SQL.

Project Overview

Traditional business intelligence tools require users to:

Know SQL

Understand database schemas

Manually build queries

This project solves that problem by:

Accepting a question in plain English

Using Gemini AI to convert it into SQL

Running the SQL on a sales database

Displaying the results as a table and chart

BI_Query_Agent
│
├── csv_to_sql.ipynb      # Converts CSV data into SQLite database
├── sales.db              # Generated SQLite database
├── app.py                # Main Streamlit AI agent
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation


#How the System Works

User enters a question:  "Show total sales by country" 
Gemini receives:

The user’s question

The database schema

Gemini generates SQL:  SELECT COUNTRY, SUM(SALES)
FROM sales_data
GROUP BY COUNTRY;

The app:

Executes the SQL query

Retrieves results from the database

Displays them as:

Table

Chart

Natural language → SQL query



