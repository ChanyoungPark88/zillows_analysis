import streamlit as st
import pandas as pd
import pydeck as pdk
import time
import numpy as np
import altair as alt
import requests

from urllib.error import URLError


def main():
    st.title("Zillow Analysis Tool")
    st.sidebar.success("Select a feature above.")

    st.markdown(
        """
        Light-weight no-code solution to retrieve listings and property details.

        **👈 Select a feature from the dropdown on the left**

        ### Features

        - Listings Search
        - Property Detail
        - Analystics
    """
    )


def get_listings(listing_url, api_key, email):
    url = "https://app.scrapeak.com/v1/scrapers/zillow/listing"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)"}

    querystring = {
        "api_key": api_key,
        "url": listing_url,
        "email": email
    }

    return requests.request("GET", url, params=querystring, headers=headers)


def get_properties(api_key, email, zpid=None, address=None):
    url = "https://app.scrapeak.com/v1/scrapers/zillow/property"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)"}

    querystring = {
        "api_key": api_key,
        "email": email,
        "zpid": zpid,
        "address": address
    }
    if zpid is not None:
        querystring['zpid'] = zpid
    if address is not None:
        querystring['address'] = address

    response = requests.request(
        "GET", url, params=querystring, headers=headers)
    return response.json()


def get_listing_parameters():

    st.title("Listings Search")
    if "visibility" not in st.session_state:
        st.session_state.visibility = "visible"
        st.session_state.disabled = False
        st.session_state.placeholder = "Enter value"

    # col1, col2, col3 = st.columns(3)

    with st.container():
        st.markdown("## 1. Enter Web Link")
        listing_url = st.text_input(
            'url',
            label_visibility=st.session_state.visibility,
            disabled=st.session_state.disabled,
            placeholder='https://www.zillow.com/...'
        )

    with st.container():
        st.markdown("## 2. Enter your API Key")
        api_key = st.text_input(
            'API Key',
            label_visibility=st.session_state.visibility,
            disabled=st.session_state.disabled,
            placeholder='1234567890',
            type="password"
        )

    with st.container():
        st.markdown("## 3. Enter your E-Mail")
        email = st.text_input(
            'Email',
            label_visibility=st.session_state.visibility,
            disabled=st.session_state.disabled,
            placeholder='demo@demo.com',
        )

    if st.button("Run", type="secondary"):
        result = get_listings(listing_url=listing_url,
                              api_key=api_key, email=email)
        if result.json()['is_success']:
            num_of_properties = result.json(
            )['data']['categoryTotals']['cat1']['totalResultCount']
            st.markdown(
                f"""
                Successfully retrieved data! Go to the analytics tab to view results.

                Number of properties matching search: {num_of_properties}
            """
            )
            df_sale_listings = pd.json_normalize(
                result.json()['data']['cat1']['searchResults']['mapResults'])
            st.write(df_sale_listings)


def get_property_parameters():

    st.title("Property Detail Search")
    if "visibility" not in st.session_state:
        st.session_state.visibility = "visible"
        st.session_state.disabled = False
        st.session_state.placeholder = "Enter value"

    # col1, col2, col3 = st.columns(3)

    with st.container():
        st.markdown("## 1. Enter a Unique Identifier")
        zpid = st.text_input(
            'Unique ID',
            label_visibility=st.session_state.visibility,
            disabled=st.session_state.disabled,
            placeholder='1234567'
        )
        st.text('or')
        address = st.text_input(
            'Full Address',
            label_visibility=st.session_state.visibility,
            disabled=st.session_state.disabled,
            placeholder='110 1st St, Jersey City, NJ 07302'
        )
    with st.container():
        st.markdown("## 2. Enter your API Key")
        api_key = st.text_input(
            'API Key',
            label_visibility=st.session_state.visibility,
            disabled=st.session_state.disabled,
            placeholder='1234567890',
            type="password"
        )

    with st.container():
        st.markdown("## 3. Enter your E-Mail")
        email = st.text_input(
            'Email',
            label_visibility=st.session_state.visibility,
            disabled=st.session_state.disabled,
            placeholder='demo@demo.com',
        )

    if st.button("Run", type="secondary"):
        result = get_properties(
            api_key=api_key, email=email, zpid=zpid, address=address)
        if result.json()['is_success']:
            df_prop = pd.json_normalize(
                result.json()['data'])
            st.write(df_prop)


def data_frame_demo():
    pass


page_names_to_funcs = {
    "Home": main,
    "Listings Search": get_listing_parameters,
    "Property Detail": get_property_parameters,
    "DataFrame Demo": data_frame_demo
}

feature_name = st.sidebar.selectbox(
    "Choose a feature", page_names_to_funcs.keys())
page_names_to_funcs[feature_name]()
