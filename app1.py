import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="OLA Ride Insights",
    layout="wide",
    page_icon="🚖"
)

# ---------------- DATABASE FUNCTIONS ----------------
@st.cache_data
def load_full_data():
    """Load the full rides data from SQLite"""
    conn = sqlite3.connect("ola.db")
    df = pd.read_sql("SELECT * FROM rides", conn)
    conn.close()

    # Convert ride_datetime safely
    df['ride_datetime'] = pd.to_datetime(
        df['ride_datetime'],
        format="%d-%m-%Y %H:%M",
        errors='coerce'
    )
    df = df.dropna(subset=['ride_datetime'])
    return df


def get_data(query):
    """Fetch data from SQLite database"""
    conn = sqlite3.connect("ola.db")
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ---------------- LOAD DATA ----------------
base_df = load_full_data()
df = base_df.copy()

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.title("🎛️ Filters")

vehicle_filter = st.sidebar.multiselect(
    "Vehicle Type",
    options=sorted(df['vehicle_type'].dropna().unique()),
    default=sorted(df['vehicle_type'].dropna().unique())
)

status_filter = st.sidebar.multiselect(
    "Booking Status",
    options=sorted(df['booking_status'].dropna().unique()),
    default=sorted(df['booking_status'].dropna().unique())
)

df = df[
    (df['vehicle_type'].isin(vehicle_filter)) &
    (df['booking_status'].isin(status_filter))
]

min_date = df['ride_datetime'].min()
max_date = df['ride_datetime'].max()

date_range = st.sidebar.date_input(
    "Ride Date Range",
    [min_date.date(), max_date.date()]
)

df = df[
    (df['ride_datetime'] >= pd.to_datetime(date_range[0])) &
    (df['ride_datetime'] <= pd.to_datetime(date_range[1]))
]

# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs([
    "📊 Overview",
    "📈 SQL Insights",
    "📊 Power BI Dashboard"
])

# ================= TAB 1: OVERVIEW =================
with tab1:
    st.title("🚖 OLA Ride Insights")

    total_rides = get_data(
        "SELECT COUNT(DISTINCT booking_id) AS total FROM rides"
    )['total'][0]

    completed_rides = get_data(
        "SELECT COUNT(DISTINCT booking_id) AS total FROM rides WHERE booking_status='Success'"
    )['total'][0]

    completion_rate = round((completed_rides / total_rides) * 100, 2)

    revenue = get_data(
        "SELECT SUM(booking_value) AS revenue FROM rides"
    )['revenue'][0] or 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Rides", f"{total_rides:,}")
    col2.metric("Completed Rides", f"{completed_rides:,}")
    col3.metric("Completion Rate %", f"{completion_rate}%")
    col4.metric("Total Revenue", f"₹ {revenue/1e6:.2f} M")

    st.markdown("---")
    st.subheader("📄 Data Overview")

    col5, col6 = st.columns(2)
    col5.metric("Total Rows", total_rides)
    col6.metric("Total Columns", df.shape[1])

    st.dataframe(df.head(100), use_container_width=True)

# ================= TAB 2: SQL INSIGHTS =================
with tab2:
    st.title("📈 SQL Insights (Powered by SQLite Views)")
    st.markdown("---")

    # 1️⃣ Successful Bookings
    st.subheader("✅ Successful Bookings")
    st.dataframe(
        get_data("SELECT * FROM vw_successful_bookings LIMIT 200"),
        use_container_width=True
    )

    st.markdown("---")

    # 2️⃣ Avg Ride Distance
    st.subheader("🚗 Average Ride Distance by Vehicle Type")
    df_avg_distance = get_data("SELECT * FROM vw_avg_distance_by_vehicle")

    fig1 = px.bar(
        df_avg_distance,
        x="vehicle_type",
        y="avg_ride_distance",
        text="avg_ride_distance"
    )
    fig1.update_traces(textposition="outside")
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("---")

    # 3️⃣ Cancelled by Customer
    st.subheader("❌ Customer Cancellations")
    df_cancel_customer = get_data("SELECT * FROM vw_cancelled_by_customer")
    st.metric("Total Cancelled by Customer", int(df_cancel_customer.iloc[0, 0]))

    st.markdown("---")

    # 4️⃣ Top 5 Customers
    st.subheader("🏆 Top 5 Customers by Number of Rides")
    df_top_customers = get_data("SELECT * FROM vw_top_5_customers")

    fig2 = px.bar(
        df_top_customers,
        x="total_rides",
        y="customer_id",
        orientation="h"
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # 5️⃣ Driver Cancellations
    st.subheader("🚧 Driver Cancellations (Personal & Car Issues)")
    df_driver_cancel = get_data("SELECT * FROM vw_driver_cancel_personal_car")
    st.metric("Driver Cancelled (Personal & Car)", int(df_driver_cancel.iloc[0, 0]))

    st.markdown("---")

    # 6️⃣ Prime Sedan Ratings
    st.subheader("⭐ Prime Sedan Driver Ratings")
    st.dataframe(
        get_data("SELECT * FROM vw_prime_sedan_drivers_ratings"),
        use_container_width=True
    )

    st.markdown("---")

    # 7️⃣ UPI Payments
    st.subheader("💳 Rides Paid via UPI")
    st.dataframe(
        get_data("SELECT * FROM vw_upi_payments LIMIT 200"),
        use_container_width=True
    )

    st.markdown("---")

    # 8️⃣ Avg Customer Rating
    st.subheader("🙂 Average Customer Rating by Vehicle Type")
    df_avg_rating = get_data("SELECT * FROM vw_avg_customer_rating")

    fig3 = px.bar(
        df_avg_rating,
        x="vehicle_type",
        y="avg_customer_rating",
        text="avg_customer_rating"
    )
    fig3.update_traces(textposition="outside")
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    # 9️⃣ Total Booking Value
    st.subheader("💰 Total Booking Value (Successful Rides)")
    df_total_booking = get_data("SELECT * FROM vw_total_booking_value")
    st.metric(
        "Total Booking Value",
        f"₹ {int(df_total_booking.iloc[0, 0] or 0):,}"
    )

    st.markdown("---")

    # 🔟 Incomplete Rides
    st.subheader("⚠️ Incomplete Rides & Reasons")
    st.dataframe(
        get_data("SELECT * FROM vw_incomplete_rides LIMIT 300"),
        use_container_width=True
    )

# ================= TAB 3: POWER BI =================
with tab3:
    st.title("📊 Power BI Dashboard")

    power_bi_url = (
       "https://app.powerbi.com/reportEmbed?reportId=7cb17d2b-0ac8-4fa9-bc95-64ea4a9af888&autoAuth=true&ctid=7a34b5dd-01f5-4e32-984a-c4d852a0663d"
    )

    st.components.v1.iframe(
        src=power_bi_url,
        height=400,
        width=800,
        scrolling=True
    )
