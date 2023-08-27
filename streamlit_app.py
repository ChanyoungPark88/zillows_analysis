import streamlit as st
import pandas as pd
import pydeck as pdk
import time
import numpy as np
import altair as alt

from urllib.error import URLError


def main():
    st.title("# Zillow Analysis Tool")
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


def get_parameters():
    if "visibility" not in st.session_state:
        st.session_state.visibility = "visible"
        st.session_state.disabled = False

    col1, col2, col3 = st.columns(3)

    st.title("# Listings Search")

    with col1:
        st.markdown("## 1. Enter Web Link")
        listing_url = st.text_input(
            'url',
            label_visibility=st.session_state.visibility,
            disabled=st.session_state.disabled,
            placeholder=st.session_state.placeholder,
        )

    with col2:
        st.markdown("## 2. Enter your API Key")
        api_key = st.text_input(
            'API Key',
            label_visibility=st.session_state.visibility,
            disabled=st.session_state.disabled,
            placeholder=st.session_state.placeholder,
        )

    with col3:
        st.markdown("## 3. Enter your E-Mail")
        email = st.text_input(
            'Email',
            label_visibility=st.session_state.visibility,
            disabled=st.session_state.disabled,
            placeholder=st.session_state.placeholder,
        )


def mapping_demo():
    pass


def data_frame_demo():
    pass


page_names_to_funcs = {
    "Home": main,
    "Listings Search": get_parameters,
    "Mapping Demo": mapping_demo,
    "DataFrame Demo": data_frame_demo
}

feature_name = st.sidebar.selectbox(
    "Choose a feature", page_names_to_funcs.keys())
page_names_to_funcs[feature_name]()
