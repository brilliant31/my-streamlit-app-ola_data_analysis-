# ===================== IMPORTS =====================
import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="OLA Ride Insights",
    layout="wide",
    page_icon="🚖"
)

# ===================== DATABASE FUNCTIONS =====================
@st.cache_data
def load_full_data():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="ola"
    )
    df = pd.read_sql("SELECT * FROM rides", conn)
    conn.close()
    return df


def get_data(query):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="ola"
    )
    df = pd.read_sql(query, conn)
    conn.close()
    return df


# ===================== LOAD DATA =====================
base_df = load_full_data()
df = base_df.copy()
df['ride_datetime'] = pd.to_datetime(df['ride_datetime'])

# ===================== SIDEBAR FILTERS =====================
st.sidebar.title("🎛️ Filters")

vehicle_filter = st.sidebar.multiselect(
    "Vehicle Type",
    sorted(df['vehicle_type'].unique()),
    default=sorted(df['vehicle_type'].unique())
)

status_filter = st.sidebar.multiselect(
    "Booking Status",
    sorted(df['booking_status'].unique()),
    default=sorted(df['booking_status'].unique())
)

min_date = df['ride_datetime'].min().date()
max_date = df['ride_datetime'].max().date()

date_range = st.sidebar.date_input(
    "Ride Date Range",
    [min_date, max_date]
)

# ===================== APPLY FILTERS (ONLY TO df) =====================
df = df[
    (df['vehicle_type'].isin(vehicle_filter)) &
    (df['booking_status'].isin(status_filter)) &
    (df['ride_datetime'].dt.date >= date_range[0]) &
    (df['ride_datetime'].dt.date <= date_range[1])
]

# ===================== SIDEBAR NAVIGATION =====================
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "📌 Navigate",
    ["Overview", "SQL Insights", "Power BI Dashboard", "About"]
)

# ===================== PAGE 1 : OVERVIEW =====================
if page == "Overview":
    st.title("🚖 OLA Ride Insights")

    total_rides = get_data(
        "SELECT COUNT(DISTINCT booking_id) AS total FROM rides"
    )['total'][0]

    completed_rides = get_data(
        "SELECT COUNT(DISTINCT booking_id) AS total FROM rides WHERE booking_status='Success'"
    )['total'][0]

    completion_rate = round((completed_rides / total_rides) * 100, 2)

    revenue = get_data(
        "SELECT SUM(booking_value) AS revenue FROM rides WHERE booking_status='Success'"
    )['revenue'][0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Rides", f"{total_rides:,}")
    col2.metric("Completed Rides", f"{completed_rides:,}")
    col3.metric("Completion Rate", f"{completion_rate}%")
    col4.metric("Total Revenue", f"₹ {revenue/1e6:.2f} M")

    st.subheader("📄 Filtered Data Preview")
    st.dataframe(df.head(100), use_container_width=True)

# ===================== PAGE 2 : SQL INSIGHTS =====================
elif page == "SQL Insights":
    st.title("📈 SQL Insights (MySQL Views)")

    st.subheader("Top 5 Customers by Rides")
    st.dataframe(
        get_data("SELECT * FROM vw_top_5_customers"),
        use_container_width=True
    )

    st.subheader("Average Ride Distance by Vehicle Type")
    avg_dist = get_data("SELECT * FROM vw_avg_distance_by_vehicle")
    st.plotly_chart(
        px.bar(avg_dist, x="vehicle_type", y="avg_ride_distance", text="avg_ride_distance"),
        use_container_width=True
    )

    st.subheader("Customer Cancellations")
    st.metric(
        "Cancelled by Customers",
        int(get_data("SELECT * FROM vw_cancelled_by_customer").iloc[0, 0])
    )

    st.subheader("Incomplete Rides")
    st.dataframe(
        get_data("SELECT * FROM vw_incomplete_rides LIMIT 200"),
        use_container_width=True
    )

# ===================== PAGE 3 : POWER BI =====================
elif page == "Power BI Dashboard":
    st.title("📊 Power BI Dashboard")

    power_bi_url = "https://app.powerbi.com/reportEmbed?reportId=7cb17d2b-0ac8-4fa9-bc95-64ea4a9af888&autoAuth=true&ctid=7a34b5dd-01f5-4e32-984a-c4d852a0663d"

    st.components.v1.iframe(
        src=power_bi_url,
        height=750,
        width="100%"
    )

# ===================== PAGE 4 : ABOUT =====================
else:
    st.title("ℹ️ About Project")

    st.markdown("""
    **OLA Ride Insights** is an end-to-end analytics project built using:

    - **MySQL** for data storage & SQL views  
    - **Python & Streamlit** for analytics app  
    - **Power BI** for executive dashboards  

    🔹 KPIs are calculated at **database level**  
    🔹 Filters affect visuals, not KPIs  
    🔹 Power BI is embedded via service
    """)
