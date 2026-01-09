import streamlit as st
import mysql.connector
import plotly.express as px
from datetime import date
from decimal import Decimal
st.set_page_config(
    page_title="OLA Ride Insights",
    layout="wide",
    page_icon="🚖"
)

# ---------------- DB CONNECTION ----------------
def get_connection():
    return mysql.connector.connect(
        host="localhost",      # change to secrets in cloud
        user="root",
        password="root",
        database="ola"
    )

def fetch_all(query):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def fetch_one(query):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    value = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return value

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.title("🎛️ Filters")

vehicle_types = [v["vehicle_type"] for v in fetch_all(
    "SELECT DISTINCT vehicle_type FROM rides"
)]

booking_statuses = [s["booking_status"] for s in fetch_all(
    "SELECT DISTINCT booking_status FROM rides"
)]

vehicle_filter = st.sidebar.multiselect(
    "Vehicle Type",
    options=vehicle_types,
    default=vehicle_types
)

status_filter = st.sidebar.multiselect(
    "Booking Status",
    options=booking_statuses,
    default=booking_statuses
)

# Date range
min_date = fetch_one("SELECT DATE(MIN(ride_datetime)) FROM rides")
max_date = fetch_one("SELECT DATE(MAX(ride_datetime)) FROM rides")

date_range = st.sidebar.date_input(
    "Ride Date Range",
    [min_date, max_date]
)

# SQL WHERE clause builder
def build_where():
    return f"""
        WHERE vehicle_type IN ({','.join([f"'{v}'" for v in vehicle_filter])})
        AND booking_status IN ({','.join([f"'{s}'" for s in status_filter])})
        AND DATE(ride_datetime) BETWEEN '{date_range[0]}' AND '{date_range[1]}'
    """

# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs([
    "📊 Overview",
    "📈 SQL Insights",
    "📊 Power BI Dashboard"
])

# ================= TAB 1 =================
with tab1:
    st.title("🚖 OLA Ride Insights")

    total_rides = fetch_one(
        "SELECT COUNT(DISTINCT booking_id) FROM rides"
    )

    completed_rides = fetch_one(
        "SELECT COUNT(DISTINCT booking_id) FROM rides WHERE booking_status='Success'"
    )

    revenue = fetch_one(
        "SELECT SUM(booking_value) FROM rides WHERE booking_status='Success'"
    )

    completion_rate = round((completed_rides / total_rides) * 100, 2)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Rides", f"{total_rides:,}")
    col2.metric("Completed Rides", f"{completed_rides:,}")
    col3.metric("Completion Rate %", f"{completion_rate}%")
    col4.metric("Total Revenue", f"₹ {revenue/1e6:.2f} M")

    st.markdown("---")
    st.subheader("📄 Data Overview")

    data = fetch_all(f"SELECT * FROM rides {build_where()} LIMIT 100")
    st.metric("Total Rows", len(data))
    st.metric("Total Columns", len(data[0]) if data else 0)

    st.dataframe(data, use_container_width=True)

# ================= TAB 2 =================
with tab2:
    st.title("📈 SQL Insights (Powered by MySQL Views)")

    st.subheader("✅ Successful Bookings")
    st.dataframe(fetch_all("SELECT * FROM vw_successful_bookings LIMIT 200"),
                 use_container_width=True)

    st.markdown("---")

    st.subheader("🚗 Average Ride Distance by Vehicle Type")
    avg_distance = fetch_all("SELECT * FROM vw_avg_distance_by_vehicle")

    fig1 = px.bar(
        avg_distance,
        x="vehicle_type",
        y="avg_ride_distance",
        text="avg_ride_distance"
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("---")

    st.subheader("❌ Customer Cancellations")
    st.metric(
        "Total Cancelled by Customer",
        fetch_one("SELECT * FROM vw_cancelled_by_customer")
    )

    st.markdown("---")

    st.subheader("🏆 Top 5 Customers by Number of Rides")
    top_customers = fetch_all("SELECT * FROM vw_top_5_customers")

    fig2 = px.bar(
        top_customers,
        x="total_rides",
        y="customer_id",
        orientation="h"
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    st.subheader("🚧 Driver Cancellations (Personal & Car Issues)")
    st.metric(
        "Driver Cancelled",
        fetch_one("SELECT * FROM vw_driver_cancel_personal_car")
    )

    st.markdown("---")

    st.subheader("⭐ Prime Sedan Driver Ratings")
    st.dataframe(fetch_all("SELECT * FROM vw_prime_sedan_drivers_ratings"),
                 use_container_width=True)

    st.markdown("---")

    st.subheader("💳 Rides Paid via UPI")
    st.dataframe(fetch_all("SELECT * FROM vw_upi_payments LIMIT 200"),
                 use_container_width=True)

    st.markdown("---")

    st.subheader("🙂 Average Customer Rating by Vehicle Type")
    avg_rating = fetch_all("SELECT * FROM vw_avg_customer_rating")

    fig3 = px.bar(
        avg_rating,
        x="vehicle_type",
        y="avg_customer_rating",
        text="avg_customer_rating"
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    st.subheader("💰 Total Booking Value (Successful Rides)")
    st.metric(
        "Total Booking Value",
        f"₹ {fetch_one('SELECT * FROM vw_total_booking_value'):,}"
    )

    st.markdown("---")

    st.subheader("⚠️ Incomplete Rides & Reasons")
    st.dataframe(fetch_all("SELECT * FROM vw_incomplete_rides LIMIT 300"),
                 use_container_width=True)

# ================= TAB 3 =================
with tab3:
    st.title("📊 Power BI Dashboard")

    power_bi_url = "https://app.powerbi.com/reportEmbed?reportId=7cb17d2b-0ac8-4fa9-bc95-64ea4a9af888"
    st.components.v1.iframe(power_bi_url, height=600, scrolling=True)
