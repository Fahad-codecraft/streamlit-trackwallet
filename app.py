import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# Initialize session state
if "data" not in st.session_state:
    st.session_state.data = None

if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None


@st.cache_resource
def load_data(file_path):
    data = pd.read_csv(file_path)
    data['Date'] = pd.to_datetime(data['Date'], format='ISO8601')  # Ensure proper datetime format
    return data


# File uploader
uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])

# Load file if uploaded
if uploaded_file is not None:
    st.session_state.uploaded_file = uploaded_file  # Persist file in session state
    st.session_state.data = load_data(uploaded_file)

data = st.session_state.data

# Ensure the app does not reset unnecessarily
if data is None:
    st.write("Please upload a file to get started.")
    st.stop()

# Sidebar filters
st.sidebar.header("Filters")

# Get current date
today = date.today()

# Predefined date ranges
first_day_of_month = today.replace(day=1)
first_day_of_year = today.replace(month=1, day=1)

date_filter = st.sidebar.selectbox(
    "Select Date Range",
    ["Custom Range", "This Month", "This Year"],
)

if date_filter == "This Month":
    start_date = first_day_of_month
    end_date = today
elif date_filter == "This Year":
    start_date = first_day_of_year
    end_date = today
else:
    # Custom range selection with unique keys
    start_date = st.sidebar.date_input("Start date", value=first_day_of_month, key="start_date")
    end_date = st.sidebar.date_input("End date", value=today, key="end_date")
filtered_data = data[(data['Date'] >= pd.Timestamp(start_date)) & (data['Date'] <= pd.Timestamp(end_date))]

# Transaction type filter
transaction_type = st.sidebar.multiselect(
    "Transaction Type", options=["Expense", "Income"], default=["Expense", "Income"]
)
filtered_data = filtered_data[filtered_data['Transaction'].isin(transaction_type)]

#Account type filter
account_type = st.sidebar.multiselect(
    "Account Type", options=data['Account'].unique(), default=data['Account'].unique()
)
if account_type:
    filtered_data = filtered_data[filtered_data['Account'].isin(account_type)]

# Dynamically update categories based on selected transaction types
available_categories = filtered_data['Category'].unique()
category = st.sidebar.multiselect(
    "Category", options=available_categories
)
if category:  # Check if any category is selected
    filtered_data = filtered_data[filtered_data['Category'].isin(category)]

# Chart type selector
chart_type = st.sidebar.selectbox("Select chart type", ["Bar", "Line"])

# Main app
st.title("Expense Tracker Dashboard")

# Show filtered data
data_view = st.checkbox("Show raw data")
if data_view:
    st.write(filtered_data)

# Summary metrics
st.header("Summary")
st.write(f"Period: {start_date} to {end_date}")
total_income = filtered_data[filtered_data['Transaction'] == 'Income']['Amount_INR'].sum()
total_expense = filtered_data[filtered_data['Transaction'] == 'Expense']['Amount_INR'].sum()
col1, col2 = st.columns(2)
col1.metric(label="Total Income (INR)", value=f"{total_income}")
col2.metric(label="Total Expense (INR)", value=f"{total_expense}")

# Visualization
st.header("Visualizations")
if chart_type == "Bar":
    filtered_data['Amount_INR'] = filtered_data['Amount_INR'].abs()  # Convert to positive
    fig = px.bar(
        filtered_data,
        x="Date",
        y="Amount_INR",
        color="Transaction",
        title="Expenses and Income by Date",
        labels={"Amount_INR": "Amount (INR)"},
    )
elif chart_type == "Line":
    filtered_data['Amount_INR'] = filtered_data['Amount_INR'].abs()  # Convert to positive
    fig = px.line(
        filtered_data,
        x="Date",
        y="Amount_INR",
        color="Transaction",
        title="Expenses and Income Trends",
        labels={"Amount_INR": "Amount (INR)"},
        line_shape="spline"
    )
st.plotly_chart(fig)

# Pie Charts for Expense and Income Categories
st.header("Category Distribution")

# Expense Categories Pie Chart
expense_data = filtered_data[filtered_data['Transaction'] == 'Expense'].copy()
expense_data['Amount_INR'] = expense_data['Amount_INR'].abs()  # Convert to positive

if not expense_data.empty:
    fig_expense = px.pie(
        expense_data,
        names='Category',
        values='Amount_INR',
        title="Expense Category Distribution",
        color_discrete_sequence=px.colors.sequential.RdBu,
    )
    # st.plotly_chart(fig_expense)

# Income Categories Pie Chart
income_data = filtered_data[filtered_data['Transaction'] == 'Income']
if not income_data.empty:
    fig_income = px.pie(
        income_data,
        names='Category',
        values='Amount_INR',
        title="Income Category Distribution",
        color_discrete_sequence=px.colors.sequential.Viridis,
    )
    # st.plotly_chart(fig_income)

ch1, ch2 = st.columns(2)
ch1.plotly_chart(fig_expense)
ch2.plotly_chart(fig_income)