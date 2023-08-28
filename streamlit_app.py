import streamlit as st
import pandas as pd
import pydeck as pdk
import time
import numpy as np
import altair as alt
import requests
import os

from pymongo import MongoClient
from urllib.error import URLError


def main():
    st.title("Zillow Analysis Tool 🏘️")
    st.sidebar.success("Select a feature above.")

    st.markdown(
        """
        ### Light-weight no-code solution to retrieve listings and property details.

        #### **👈 Select a feature from the dropdown on the left**

        ### Features
        - **Sign Up** - *Start here*
        - **About** - *Info on how to use the tool*
        - **Listings Search** - *Obtain all properties from a search*
        - **Property Detail** - *Detail on a single property including property estimates, tax history,  price history, search stats and more*
        - **Analystics** - *View previous searches, analyze trends & download results*
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


def save_to_db(fname, lname, email):
    MONGO_URL = os.environ.get('MONGO_URL')
    DB_NAME = os.environ.get('DB_NAME')
    COLLECTION_NAME = os.environ.get('COLLECTION_NAME')

    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    data = {
        "fname": fname,
        "lname": lname,
        "email": email
    }
    collection.insert_one(data)


def get_signup_parameters():
    st.title("Sign Up 🔍")
    st.markdown(
        """
        ### One-time sign up to use the tool

        ### 1. Sign Up for a free API Key 🔑
        [Scrapeak|Real Estate APIs|Zillow Scrapper](http://bit.ly/3YVU3Ga)

        ### 2. Sign up for the tool 🏠
    """
    )
    if "visibility" not in st.session_state:
        st.session_state.visibility = "visible"
        st.session_state.disabled = False

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            fname = st.text_input('First Name', label_visibility=st.session_state.visibility,
                                  disabled=st.session_state.disabled)
        with col2:
            lname = st.text_input('Last Name', label_visibility=st.session_state.visibility,
                                  disabled=st.session_state.disabled)
    with st.container():
        email = st.text_input('Email', label_visibility=st.session_state.visibility,
                              disabled=st.session_state.disabled)

    if st.button("Sign Up", type="secondary"):
        save_to_db(fname=fname, lname=lname, email=email)
        st.success("You are already signed up! Start searching 👈")


def get_listing_parameters():

    st.title("Listings Search 🔍")
    if "visibility" not in st.session_state:
        st.session_state.visibility = "visible"
        st.session_state.disabled = False
        st.session_state.placeholder = "Enter value"

    with st.container():
        st.markdown("## 1. Enter Web Link 🌐")
        listing_url = st.text_input(
            'url',
            label_visibility=st.session_state.visibility,
            disabled=st.session_state.disabled,
            placeholder='https://www.zillow.com/...'
        )

    with st.container():
        st.markdown("## 2. Enter your API Key 👇")
        api_key = st.text_input(
            'API Key',
            label_visibility=st.session_state.visibility,
            disabled=st.session_state.disabled,
            placeholder='1234567890',
            type="password"
        )

    with st.container():
        st.markdown("## 3. Enter your E-Mail ✉️")
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

    st.title("Property Detail Search 🔍")
    if "visibility" not in st.session_state:
        st.session_state.visibility = "visible"
        st.session_state.disabled = False
        st.session_state.placeholder = "Enter value"

    with st.container():
        st.markdown("## 1. Enter a Unique Identifier 🏠")
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
        st.markdown("## 2. Enter your API Key 👇")
        api_key = st.text_input(
            'API Key',
            label_visibility=st.session_state.visibility,
            disabled=st.session_state.disabled,
            placeholder='1234567890',
            type="password"
        )

    with st.container():
        st.markdown("## 3. Enter your E-Mail ✉️")
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


def data_analystic():
    with st.form("my_form"):
        st.text("Inside the form")
        st.title("Data Analystics 📈")
        if "visibility" not in st.session_state:
            st.session_state.visibility = "visible"
            st.session_state.disabled = False
            st.session_state.placeholder = "Enter value"

        st.markdown("## Enter your E-Mail")
        email = st.text_input(
            'Email',
            label_visibility=st.session_state.visibility,
            disabled=st.session_state.disabled,
            placeholder='demo@demo.com')

        option = st.selectbox(
            'Search Type (select below 👇)',
            ('Listings', 'Property Detail'))

        if st.form_submit_button("Go", type="secondary"):
            if option == 'Listings':
                st.markdown('### Search Selection ')
            else:
                pass


page_names_to_funcs = {
    "Home": main,
    "📥 Sign Up": get_signup_parameters,
    "🏙️ Listings Search": get_listing_parameters,
    "🏠 Property Detail": get_property_parameters,
    "📊 Analystics": data_analystic
}

feature_name = st.sidebar.selectbox(
    "Choose a feature", page_names_to_funcs.keys())
page_names_to_funcs[feature_name]()
