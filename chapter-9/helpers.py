import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from ridgeplot import ridgeplot

def load_price_data():
    return pd.read_parquet("./data/wales.parquet")

#################################
# functions to get dropdown info
#################################

def get_counties(df):
    return sorted(df["county"].unique())

def get_towns(df, county, null_value):
    if (not county) or (county == null_value):
        return []
        
    return (
        [null_value]
        + sorted(
            df.loc[df["county"] == county, "town_city"]
            .unique()
        )
    )

def get_streets(df, county, town, null_value):
    if (not (county and town)) or (town == null_value):
        return []
        
    return (
        [null_value] +
        sorted(
            df.loc[(df["county"] == county)
                   & (df["town_city"] == town),
            "street"]
            .unique()
        )
    )

#########
# charts
#########

def transactions_per_year(df):
    fig, axis = plt.subplots()

    (
        df
        .set_index("sale_date")
        .resample("YS")
        .size()
        .plot(ax=axis, color="gray", marker="x")
    )
    
    axis.set(
        ylabel="# of transactions"
    )

    return fig

def distribution_of_property_type(df):    
    fig, axis = plt.subplots()
    
    (
        df["property_type"]
        .value_counts()
        .sort_values()
        .plot
        .barh(ax=axis, color="gray")
    )
    
    axis.set(
        xlabel="# of transactions"
    )

    return fig

def median_price_by_property_type(df):
    fig, axis = plt.subplots()
    
    (
        df
        .groupby("property_type")
        ["sale_price"]
        .median()
        .sort_values()
        .plot
        .barh(ax=axis, color="gray")
    )
    
    axis.set(
        xlabel="Median price (£)",
        ylabel=None
    )

    return fig

def get_county_ridgeplot_data(df, counties):
    sales_by_county = []
    
    for county in counties:
        prices = (
            df
            .loc[(df["county"] == county)
                 & (df["sale_price"] < 500_000)
                 & (df["year"] == 2023),
            "sale_price"]
        )
        sales_by_county.append([prices])

    return sales_by_county

def county_ridgeplot(sales_by_county, counties):
    fig = ridgeplot(sales_by_county,
                    labels=counties,
                    colorscale="gray",
                    coloralpha=0.9,
                    colormode="mean-minmax",
                    spacing=0.7)

    fig.update_layout(
        title="Distribution of house sale prices in Wales in 2023, by county",
        height=650,
        width=950,
        font_size=12,
        plot_bgcolor="rgb(245, 245, 245)",
        xaxis_gridcolor="white",
        yaxis_gridcolor="white",
        xaxis_gridwidth=2,
        yaxis_title="County",
        xaxis_title="Sale price (£)",
        showlegend=False
    )

    return fig