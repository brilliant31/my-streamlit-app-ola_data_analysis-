import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px

st.set_page_config(
    page_title="OLA Ride Insights",
    layout="wide",
    page_icon="🚖"
)
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

base_df = load_full_data()
df = base_df.copy()
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


st.sidebar.title("🎛️ Filters")

vehicle_filter = st.sidebar.multiselect(
    "Vehicle Type",
    options=sorted(df['vehicle_type'].unique()),
    default=sorted(df['vehicle_type'].unique())
)

status_filter = st.sidebar.multiselect(
    "Booking Status",
    options=sorted(df['booking_status'].unique()),
    default=sorted(df['booking_status'].unique())
)

df = df[
    (df['vehicle_type'].isin(vehicle_filter)) &
    (df['booking_status'].isin(status_filter))
]
df['ride_datetime'] = pd.to_datetime(df['ride_datetime'])

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



tab1, tab2, tab3 = st.tabs([
    "📊 Overview",
    "📈 SQL Insights",
    "📊 Power BI Dashboard"
])
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
        "SELECT SUM(booking_value) AS revenue FROM rides WHERE booking_status='Success'"
    )['revenue'][0]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Rides", f"{total_rides:,}")
    col2.metric("Completed Rides", f"{completed_rides:,}")
    col3.metric("Completion Rate %", f"{completion_rate}%")
    col4.metric("Total Revenue", f"₹ {revenue/1e6:.2f} M")
    st.markdown("---")
    st.subheader("📄 Data Overview")

    col5, col6 = st.columns(2)
    col5.metric("Total Rows", df.shape[0])
    col6.metric("Total Columns", df.shape[1])

    st.dataframe(df.head(100), use_container_width=True)
with tab2:
    st.title("📈 SQL Insights (Powered by MySQL Views)")

    st.markdown(
        "This section displays insights directly derived from MySQL views, "
        "ensuring business logic is handled at the database level."
    )

    st.markdown("---")

    # 1️⃣ Successful Bookings
    st.subheader("✅ Successful Bookings")
    df_success = get_data("SELECT * FROM vw_successful_bookings LIMIT 200")
    st.dataframe(df_success, use_container_width=True)

    st.markdown("---")

    # 2️⃣ Average Ride Distance by Vehicle Type
    st.subheader("🚗 Average Ride Distance by Vehicle Type")
    df_avg_distance = get_data("SELECT * FROM vw_avg_distance_by_vehicle")

    fig1 = px.bar(
        df_avg_distance,
        x="vehicle_type",
        y="avg_ride_distance",
        text="avg_ride_distance",
        title="Average Ride Distance per Vehicle Type"
    )
    fig1.update_traces(textposition="outside")
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("---")

    # 3️⃣ Cancelled Rides by Customers (KPI)
    st.subheader("❌ Customer Cancellations")
    df_cancel_customer = get_data("SELECT * FROM vw_cancelled_by_customer")
    st.metric(
        label="Total Cancelled by Customer",
        value=int(df_cancel_customer.iloc[0, 0])
    )

    st.markdown("---")

    # 4️⃣ Top 5 Customers by Ride Count
    st.subheader("🏆 Top 5 Customers by Number of Rides")
    df_top_customers = get_data("SELECT * FROM vw_top_5_customers")

    fig2 = px.bar(
        df_top_customers,
        x="total_rides",
        y="customer_id",
        orientation="h",
        title="Top 5 Customers"
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # 5️⃣ Driver Cancellations (Personal & Car Issues)
    st.subheader("🚧 Driver Cancellations (Personal & Car Related Issues)")
    df_driver_cancel = get_data("SELECT * FROM vw_driver_cancel_personal_car")

    st.metric(
        label="Driver Cancelled (Personal & Car)",
        value=int(df_driver_cancel.iloc[0, 0])
    )

    st.markdown("---")

    # 6️⃣ Prime Sedan Driver Ratings
    st.subheader("⭐ Prime Sedan Driver Ratings")
    df_prime_rating = get_data("SELECT * FROM vw_prime_sedan_drivers_ratings")
    st.dataframe(df_prime_rating, use_container_width=True)

    st.markdown("---")

    # 7️⃣ UPI Payments
    st.subheader("💳 Rides Paid via UPI")
    df_upi = get_data("SELECT * FROM vw_upi_payments LIMIT 200")
    st.dataframe(df_upi, use_container_width=True)

    st.markdown("---")

    # 8️⃣ Average Customer Rating by Vehicle Type
    st.subheader("🙂 Average Customer Rating by Vehicle Type")
    df_avg_rating = get_data("SELECT * FROM vw_avg_customer_rating")

    fig3 = px.bar(
        df_avg_rating,
        x="vehicle_type",
        y="avg_customer_rating",
        text="avg_customer_rating",
        title="Average Customer Rating"
    )
    fig3.update_traces(textposition="outside")
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    # 9️⃣ Total Booking Value (Success Rides)
    st.subheader("💰 Total Booking Value (Successful Rides)")
    df_total_booking = get_data("SELECT * FROM vw_total_booking_value")

    st.metric(
        label="Total Booking Value",
        value=f"₹ {int(df_total_booking.iloc[0, 0]):,}"
    )

    st.markdown("---")

    # 🔟 Incomplete Rides with Reasons
    st.subheader("⚠️ Incomplete Rides & Reasons")
    df_incomplete = get_data("SELECT * FROM vw_incomplete_rides LIMIT 300")
    st.dataframe(df_incomplete, use_container_width=True)
with tab3:
    st.title("📊 Power BI Dashboard")

    st.markdown(
        "This dashboard is built in **Power BI** and embedded inside the Streamlit app."
    )

    power_bi_url = "https://app.powerbi.com/reportEmbed?reportId=7cb17d2b-0ac8-4fa9-bc95-64ea4a9af888&autoAuth=true&ctid=7a34b5dd-01f5-4e32-984a-c4d852a0663d"

    st.components.v1.iframe(
        src=power_bi_url,
        height=600,
        width="100%",
        scrolling=True
    )
