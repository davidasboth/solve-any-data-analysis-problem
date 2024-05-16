import streamlit as st
import pandas as pd

# specific calculations and functions for the app
import helpers

###########
# app code
###########

st.set_page_config(layout="wide")

@st.cache_data
def get_price_data():
    # wrap this in a function to use Streamlit's caching
    return helpers.load_price_data()

wales = get_price_data()

@st.cache_data
def get_counties(wales):
    # wrap this in a function to use Streamlit's caching
    return helpers.get_counties(wales)

counties = get_counties(wales)

@st.cache_data
def get_county_data(wales, counties):
    # wrap this in a function to use Streamlit's caching
    return helpers.get_county_ridgeplot_data(wales, counties)

sales_by_county = get_county_data(wales, counties)

# set up initial commentary and first plot
st.title("House price explorer - Wales")
st.markdown("""This tool lets you explore historic house price data in Wales.

You can drill down as far as the _individual street level_.

The chart below shows the distribution of house prices in different counties in 2023. The dropdowns below it let you drill down to a county, town, and street level.""")

st.plotly_chart(helpers.county_ridgeplot(sales_by_county, counties))

st.header("Explore house prices at different levels")

# set up dropdowns at the top
select_col1, select_col2, select_col3 = st.columns(3)

with select_col1:
    county_select = st.selectbox(
        'Select a county:',
        helpers.get_counties(wales),
        index=None,
        placeholder="-- Select a county --"
    )

TOWN_NULL_VALUE = "-- No town selected --"

with select_col2:
    town_select = st.selectbox(
        'Select a town:',
        helpers.get_towns(
            wales,
            county_select,
            null_value=TOWN_NULL_VALUE),
        index=None,
        placeholder=TOWN_NULL_VALUE
    )

STREET_NULL_VALUE = "-- No street selected --"

with select_col3:
    street_select = st.selectbox(
        'Select a street:',
        helpers.get_streets(
            wales,
            county_select,
            town_select,
            null_value=STREET_NULL_VALUE),
        index=None,
        placeholder=STREET_NULL_VALUE
    )

house_filter_query = "county == @county_select"
filter_message = f"Results for {county_select}"

if town_select and town_select != TOWN_NULL_VALUE:
    house_filter_query += " and town_city == @town_select"
    filter_message += f", {town_select}"

if street_select and street_select != STREET_NULL_VALUE:
    house_filter_query += " and street == @street_select"
    filter_message += f", {street_select}"

selected_data = wales.query(house_filter_query)

# calculations based on filtered data
median_price = selected_data["sale_price"].median()

# selecting a county is enough to trigger the widgets
if county_select:
    st.header(filter_message)

    metric_col1, metric_col2 = st.columns(2)
    metric_col1.metric("Number of records", f"{len(selected_data):,.0f}")
    metric_col2.metric("Median sale price", f"£{median_price:,.0f}")

    chart_col1, chart_col2, chart_col3 = st.columns(3)
    
    with chart_col1:
        st.subheader("Transactions over time")
        st.pyplot(helpers.transactions_per_year(selected_data))

    with chart_col2:
        st.subheader("Distribution of property type")
        st.pyplot(helpers.distribution_of_property_type(selected_data))
    
    with chart_col3:
        st.subheader("Median sale price by property type")
        st.pyplot(helpers.median_price_by_property_type(selected_data))

    st.header("Raw data")
    st.write(selected_data)