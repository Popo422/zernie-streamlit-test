import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine

# Load CSS
st.set_page_config(layout="wide")

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
st.markdown(
    """
    <style>
    body {
        background-color: #f4f4f9; /* Light grey background */
        font-family: 'Arial', sans-serif; /* Font style */
        color: #333; /* Text color */
    }
    div.block-container {
        padding-top: 1rem;
        padding-left: 2rem; /* Adjust left padding */
        padding-right: 2rem; /* Adjust right padding */
    }
    /* Add more styles for specific elements if needed */
    </style>
    """,
    unsafe_allow_html=True,
)
# Create a connection to a database
username = st.secrets["username"]
password = st.secrets["password"]
host = st.secrets["host"]
port = st.secrets["port"]
database = st.secrets["database"]
booking_table = st.secrets["booking_table"]
users_table = st.secrets["users_table"]

# Create the connection URL
connection_url = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
# Create an engine instance
engine = create_engine(connection_url)

bookingTable = st.secrets["booking_table"]
usersTable = st.secrets["users_table"]

BookingAndUsersDf = pd.read_sql(
    f"""SELECT 
    a.status AS booking_status,  
    a.persons,
    a.created,
    a.price,
    b.email,
    b.firstName,
    b.lastName,
    a.customerId,
    b.status AS user_status
FROM 
    {bookingTable} a
INNER JOIN 
    {usersTable} b ON b.id = a.customerId; """,
    con=engine,
)


BookingDf = pd.read_sql(f"""SELECT * FROM {bookingTable}""", con=engine)
image = Image.open("axs.png")

dividerElement = """
    <span class="divider"></span>
"""
col1, col2,col3 = st.columns([0.1,0.1, 0.8])
with col2:
    st.image(image, width=100)
with col3:
    html_title = "<h3 class='title'>Booking Analytics</h3>"
    st.markdown(html_title, unsafe_allow_html=True)

choice = st.sidebar.selectbox("Dashboard", ("View bookings"))

(
    _,
    appproved_appointments,
    divider1,
    pending_appointments,
    divider2,
    cancelled_appointments,
    divider3,
    revenue,
) = st.columns([0.1, 0.2, 0.02, 0.2, 0.02, 0.2, 0.02, 0.2])
today = pd.Timestamp.now().normalize()
current_period = BookingDf[BookingDf["created"] >= pd.Timestamp.now().normalize()]  # Today
previous_period = BookingDf[BookingDf["created"] < pd.Timestamp.now().normalize()]

# Before today
total_approved = BookingDf[BookingDf["status"] == "approved"].shape[0]
previous_approved = BookingDf[
    (BookingDf["status"] == "approved") & (BookingDf["created"] < today)
].shape[0]
# Delta is the difference between the total and the previous period
delta_approved = total_approved - previous_approved

total_pending = BookingDf[BookingDf["status"] == "pending"].shape[0]
previous_pending = BookingDf[
    (BookingDf["status"] == "pending") & (BookingDf["created"] < today)
].shape[0]
delta_pending = total_pending - previous_pending


total_cancelled = BookingDf[BookingDf["status"] == "cancelled"].shape[0]
previous_cancelled = BookingDf[
    (BookingDf["status"] == "cancelled") & (BookingDf["created"] < today)
].shape[0]
delta_cancelled = total_cancelled - previous_cancelled

with appproved_appointments:
   st.metric("Approved Appointments",total_approved, delta=delta_approved)
# with divider1:
    # st.markdown(dividerElement, unsafe_allow_html=True,)
with pending_appointments:
     st.metric("Pending Appointments", total_pending, delta=delta_pending)
# with divider2:
#     st.markdown(dividerElement, unsafe_allow_html=True)
with cancelled_appointments:
    st.metric("Cancelled Appointments", total_cancelled, delta=delta_cancelled)
# with divider3:
#     st.markdown(dividerElement, unsafe_allow_html=True)
with revenue:
    st.metric("Total Appointments", BookingDf.shape[0],current_period.shape[0])

_, view1 = st.columns([0.1, 0.9])
with view1:
    table = st.dataframe(
        data=BookingAndUsersDf[
            ["booking_status", "created", "email", "persons", "firstName", "lastName"]
        ],
        use_container_width=True,
    )
    st.divider()

_, revenueTitle, userBookingTitle = st.columns([0.1, 0.45, 0.45])
with revenueTitle:
    st.markdown("<h3 class='stSubheader'>Revenue by Email</h3>", unsafe_allow_html=True)
with userBookingTitle:
    st.markdown(
        "<h3 class='stSubheader'>Number of Bookings by Email</h3>",
        unsafe_allow_html=True,
    )

_, col4, col5 = st.columns([0.1, 0.45, 0.45])
with col4:
    fig = px.bar(
        BookingAndUsersDf[["email", "price"]]
        .groupby(by="email")["price"]
        .sum()
        .reset_index(),
        x="email",
        y="price",
        labels={"Total Sales": "Total Sales {$}"},
        hover_data=["price"],
        template="gridon",
        height=500,
    )
    st.plotly_chart(fig, use_container_width=True)
with col5:
    pie_chart = px.pie(
        BookingAndUsersDf.groupby("email")["persons"].count().reset_index(),
        names="email",
        values="persons",
        template="gridon",
        height=500,
    )
    st.plotly_chart(pie_chart, use_container_width=True)
