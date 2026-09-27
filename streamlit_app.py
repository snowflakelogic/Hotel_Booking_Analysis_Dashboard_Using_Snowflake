import streamlit as st
import altair as alt
import os

NAVY = "#001f3f"

st.set_page_config(page_title="Hotel Bookings Dashboard", layout="wide")

st.markdown(
    f"""
    <style>
    /* Title */
    h1 {{ color: {NAVY} !important; }}
    /* Subheaders (chart titles) */
    h3 {{ color: {NAVY} !important; }}
    /* KPI label */
    [data-testid="stMetricLabel"] p {{ color: {NAVY} !important; }}
    /* KPI value */
    [data-testid="stMetricValue"] {{ color: {NAVY} !important; }}
    /* KPI delta */
    [data-testid="stMetricDelta"] {{ color: {NAVY} !important; }}
    </style>
    """,
    unsafe_allow_html=True,
)

conn = st.connection("snowflake", ttl=os.getenv("SNOWFLAKE_CONNECTION_TTL"))


@st.cache_data(ttl=600)
def load_kpis():
    avg_val = conn.query("SELECT AVG(total_amount) AS avg_booking_value FROM HOTEL_DB.PUBLIC.GOLD_BOOKING_CLEAN")
    guests = conn.query("SELECT SUM(num_guests) AS total_guests FROM HOTEL_DB.PUBLIC.GOLD_BOOKING_CLEAN")
    bookings = conn.query("SELECT COUNT(*) AS total_bookings FROM HOTEL_DB.PUBLIC.GOLD_BOOKING_CLEAN")
    revenue = conn.query("SELECT SUM(total_amount) AS total_revenue FROM HOTEL_DB.PUBLIC.GOLD_BOOKING_CLEAN")
    return {
        "avg_booking_value": avg_val["AVG_BOOKING_VALUE"].iloc[0],
        "total_guests": guests["TOTAL_GUESTS"].iloc[0],
        "total_bookings": bookings["TOTAL_BOOKINGS"].iloc[0],
        "total_revenue": revenue["TOTAL_REVENUE"].iloc[0],
    }


@st.cache_data(ttl=600)
def load_daily_revenue():
    return conn.query("SELECT date, total_revenue FROM HOTEL_DB.PUBLIC.GOLD_AGG_DAILY_BOOKING ORDER BY date")


@st.cache_data(ttl=600)
def load_daily_bookings():
    return conn.query("SELECT date, total_booking FROM HOTEL_DB.PUBLIC.GOLD_AGG_DAILY_BOOKING ORDER BY date")


@st.cache_data(ttl=600)
def load_top_cities():
    return conn.query(
        "SELECT hotel_city, total_revenue FROM HOTEL_DB.PUBLIC.GOLD_AGG_HOTEL_CITY_SALES "
        "WHERE total_revenue IS NOT NULL ORDER BY total_revenue DESC LIMIT 5"
    )


@st.cache_data(ttl=600)
def load_bookings_by_status():
    return conn.query(
        "SELECT booking_status, COUNT(*) AS total FROM HOTEL_DB.PUBLIC.GOLD_BOOKING_CLEAN GROUP BY booking_status"
    )


@st.cache_data(ttl=600)
def load_bookings_by_room():
    return conn.query(
        "SELECT room_type, COUNT(*) AS total_bookings FROM HOTEL_DB.PUBLIC.GOLD_BOOKING_CLEAN "
        "GROUP BY room_type ORDER BY total_bookings DESC"
    )


st.title("Hotel Bookings Dashboard")

if st.button("Refresh data"):
    load_kpis.clear()
    load_daily_revenue.clear()
    load_daily_bookings.clear()
    load_top_cities.clear()
    load_bookings_by_status.clear()
    load_bookings_by_room.clear()
    st.rerun()

# --- KPIs ---
kpis = load_kpis()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Revenue", f"${kpis['total_revenue']:,.0f}", border=True)
k2.metric("Total Bookings", f"{kpis['total_bookings']:,}", border=True)
k3.metric("Total Guests", f"{kpis['total_guests']:,}", border=True)
k4.metric("Avg Booking Value", f"${kpis['avg_booking_value']:,.0f}", border=True)

# --- Line Charts ---
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("Monthly Revenue")
        rev_df = load_daily_revenue()
        area_rev = alt.Chart(rev_df).mark_area(color=NAVY, opacity=0.6, line={"color": NAVY, "strokeWidth": 2}).encode(
            x=alt.X("DATE:T", title=None),
            y=alt.Y("TOTAL_REVENUE:Q", title="Revenue"),
        )
        st.altair_chart(area_rev, use_container_width=True)

with col2:
    with st.container(border=True):
        st.subheader("Monthly Bookings")
        book_df = load_daily_bookings()
        area_book = alt.Chart(book_df).mark_area(color=NAVY, opacity=0.6, line={"color": NAVY, "strokeWidth": 2}).encode(
            x=alt.X("DATE:T", title=None),
            y=alt.Y("TOTAL_BOOKING:Q", title="Bookings"),
        )
        st.altair_chart(area_book, use_container_width=True)

# --- Bar Charts (horizontal, side by side) ---
b1, b2, b3 = st.columns(3)

with b1:
    with st.container(border=True):
        st.subheader("Top 5 Cities by Revenue")
        city_df = load_top_cities()
        chart_city = alt.Chart(city_df).mark_bar(color=NAVY).encode(
            x=alt.X("TOTAL_REVENUE:Q", title="Revenue"),
            y=alt.Y("HOTEL_CITY:N", sort="-x", title=None),
        ).properties(height=250)
        st.altair_chart(chart_city, use_container_width=True)

with b2:
    with st.container(border=True):
        st.subheader("Bookings by Status")
        status_df = load_bookings_by_status()
        chart_status = alt.Chart(status_df).mark_bar(color=NAVY).encode(
            x=alt.X("TOTAL:Q", title="Count"),
            y=alt.Y("BOOKING_STATUS:N", sort="-x", title=None),
        ).properties(height=250)
        st.altair_chart(chart_status, use_container_width=True)

with b3:
    with st.container(border=True):
        st.subheader("Bookings by Room Type")
        room_df = load_bookings_by_room()
        chart_room = alt.Chart(room_df).mark_bar(color=NAVY).encode(
            x=alt.X("TOTAL_BOOKINGS:Q", title="Bookings"),
            y=alt.Y("ROOM_TYPE:N", sort="-x", title=None),
        ).properties(height=250)
        st.altair_chart(chart_room, use_container_width=True)
