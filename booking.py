import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine


# create a connection to a database
username = st.secrets["database"]["username"]
password = st.secrets["database"]["password"]
host = st.secrets["database"]["host"]
port = st.secrets["database"]["port"]
database = st.secrets["database"]["database"]
booking_table = st.secrets["database"]["booking_table"]
users_table = st.secrets["database"]["users_table"]
print(username)
try:
    # Create the connection URL
    connection_url = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
    # Create an engine instance
    engine = create_engine(connection_url)
    # Query the table and load into a DataFrame

except Exception as e:
    print(f"Error: {e}")


bookingTable = st.secrets["database"]["booking_table"]
usersTable = st.secrets["database"]["users_table"]

BookingAndUsersDf = pd.read_sql(
    f"""SELECT 
    a.status AS booking_status,  
    b.email,
    a.persons,
    a.created,
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
st.set_page_config(layout="wide")
BookingDf = pd.read_sql(f"""SELECT * FROM {bookingTable}""", con=engine)
image = Image.open("axs.png")
dividerElement = """
        <style>
    .divider {
    border-left-style: solid;
    border-left-color: gray;
    padding-left: 25px;
    }
    </style>
  <center>
    <span class="divider"></span>
 <center>
    """
col1, col2 = st.columns([0.1, 0.9])
with col1:
    st.image(image, width=100)
    html_title = """
    <style>
    .title {
    font-size: 25px;
    font-weight: bold;
    text-align: center;
    # padding-top: 30px;
    border-radius: 6px;
    }
    </style>
  <center>
    <h1 class="title">Booking Analytics</h1>
 <center>
    """
with col2:
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
    revenue
) = st.columns([0.1, 0.2, 0.02, 0.2, 0.02, 0.2, 0.02, 0.2])
with appproved_appointments:
    st.write("Approved Appointments")
    st.write(BookingDf[BookingDf["status"] == "approved"].shape[0])
with divider1:
    st.markdown(dividerElement, unsafe_allow_html=True)
with pending_appointments:
    with st.container():
        st.write("Pending Appointments")
        st.write(BookingDf[BookingDf["status"] == "pending"].shape[0])
with divider2:
    st.markdown(dividerElement, unsafe_allow_html=True)
with cancelled_appointments:
    st.write("Cancelled Appointments")
    st.write(BookingDf[BookingDf["status"] == "cancelled"].shape[0])
with divider3:
    st.markdown(dividerElement, unsafe_allow_html=True)
with revenue:
    st.write("Revenue")
    st.write(BookingDf["price"].sum())
_, view1 = st.columns([0.1, 0.9])
with view1:

    table = st.dataframe(
        data=BookingAndUsersDf[["booking_status","created", "email" , "persons",  "firstName","lastName" ]],
        width=None,
        height=None,
        use_container_width=True,
        hide_index=None,
        column_order=None,
        column_config=None,
        key=None,
        on_select="ignore",
        selection_mode="multi-row",
    )
