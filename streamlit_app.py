"""
Zillow Analysis Tool Module.

This module provides a GUI interface for Zillow analysis, using Streamlit as the frontend.
Functions include listings search, property detail retrieval, and analytics.
"""
from library.libraries import st
from components.analystics import data_analystic
from components.listing_search import get_listing_info
from components.property_detail import get_property_info

st.set_page_config(
    page_title="Zillow Analysis Tool",
    page_icon="🏘️",
    layout="wide",
)


def main():
    """
    Display the main page of the Zillow Analysis Tool.

    This function provides an introduction and guidance to users for utilizing the tool.
    """
    st.title("Zillow Analysis Tool 🏘️")
    st.sidebar.success("Select a feature above.")

    st.markdown(
        """
        ### Light-weight no-code solution to retrieve listings and property details.

        #### **👈 Select a feature from the dropdown on the left**

        ### Features
        - **Listings Search** - *Obtain all properties from a search*
        - **Property Detail** - *Detail on a single property including property
        estimates, tax history, price history, search stats and more*
        - **Analystics** - *View previous searches, analyze trends & download results*
    """
    )


page_names_to_funcs = {
    "Home": main,
    "🏙️ Listings Search": get_listing_info,
    "🏠 Property Detail": get_property_info,
    "📊 Analystics": data_analystic,
}

feature_name = st.sidebar.selectbox(
    "Choose a feature", page_names_to_funcs.keys())
page_names_to_funcs[feature_name]()
