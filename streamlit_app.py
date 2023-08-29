import streamlit as st
import pandas as pd
import pydeck as pdk
import time
import numpy as np
import altair as alt
import requests
import os
import io
import json
import base64

from datetime import datetime
from pymongo import MongoClient
from google.cloud import storage
from urllib.error import URLError

#####################################
#            FUNCTIONS              #
#####################################


def gcs_connect():
    # KEY Loading & Decoding
    key_content_encoded = os.environ.get('GOOGLE_CLOUD_KEY_CONTENTS')
    if not key_content_encoded:
        st.write("Key content is missing from environment variables.")
        return

    key_content = base64.b64decode(key_content_encoded).decode()
    key_data = json.loads(key_content)

    # Uncomment this line for debugging but avoid exposing sensitive info in a public environment.
    # st.write(key_data)

    try:
        # GCS 연결
        storage_client = storage.Client.from_service_account_info(key_data)
        return storage_client

    except URLError as e:
        st.write(e)
        return


def get_listings(listing_url, api_key):
    url = "https://app.scrapeak.com/v1/scrapers/zillow/listing"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)"}

    querystring = {
        "api_key": api_key,
        "url": listing_url
    }

    return requests.request("GET", url, params=querystring, headers=headers)


def get_properties(api_key, zpid=None, address=None):
    url = "https://app.scrapeak.com/v1/scrapers/zillow/property"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)"}

    querystring = {
        "api_key": api_key,
        "zpid": zpid,
        "address": address
    }

    if zpid is not None:
        querystring['zpid'] = zpid
    if address is not None:
        querystring['address'] = address

    return requests.request("GET", url, params=querystring, headers=headers)


def listings_save_to_db(data):
    MONGO_URL = os.environ.get('MONGO_URL')
    DB_NAME = os.environ.get('DB_NAME')
    COLLECTION_NAME = os.environ.get('LISTING_COLLECTION')

    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    result = collection.insert_one(data)
    object_id = result.inserted_id

    today = datetime.today().strftime('%Y-%m-%d')
    filename = f"{today}-{object_id}.csv"
    data['file'] = filename

    collection.update_one({'_id': object_id}, {'$set': {'file': filename}})

    client.close()

    return object_id, filename


def properties_save_to_db(data, zpid):
    MONGO_URL = os.environ.get('MONGO_URL')
    DB_NAME = os.environ.get('DB_NAME')
    COLLECTION_NAME = os.environ.get('PROPERTY_COLLECTION')

    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    today = datetime.today().strftime('%Y-%m-%d')
    filename = f"{today}_{zpid}.csv"
    data['file'] = filename

    existing_document = collection.find_one({'file': filename})

    if existing_document:
        object_id = existing_document['_id']
        collection.update_one({'_id': object_id}, {'$set': data})
    else:
        result = collection.insert_one(data)
        object_id = result.inserted_id

    client.close()

    return object_id, filename


def file_upload_to_gcs(filename, storage_client, prefix, bucket_name='my_project_storage'):
    # Get the bucket name
    bucket = storage_client.get_bucket(bucket_name)

    # Create a blob object for the file, it's like a pointer to handle the file upload
    blob_name = f"{prefix}/{filename}"
    blob = bucket.blob(blob_name)

    # Upload the file to GCS
    with open(filename, "rb") as f:
        blob.upload_from_file(f)

    return f"Uploaded {filename} to {bucket_name}/{prefix}."


def download_file_from_gcs(filename, storage_client, prefix, bucket_name='my_project_storage'):
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(f"{prefix}/{filename}")

    if not blob.exists():
        return None

    content = blob.download_as_text()

    df = pd.read_csv(io.StringIO(content))
    return df


def list_files_in_gcs(storage_client, prefix, bucket_name='my_project_storage'):
    bucket = storage_client.get_bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=prefix)
    return [blob.name.replace(f"{prefix}/", "") for blob in blobs]


#####################################
#              PAGES                #
#####################################


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


def get_listing_info():

    st.title("Listings Search 🔍")
    if "visibility" not in st.session_state:
        st.session_state.visibility = "visible"
        st.session_state.disabled = False
        st.session_state.placeholder = "Enter value"

    with st.container():
        st.markdown("## 1. Enter Web Link 🌐")
        listing_url = st.text_input(
            'url',
            # label_visibility=st.session_state.visibility,
            # disabled=st.session_state.disabled,
            # placeholder='https://www.zillow.com/...'
            "https://www.zillow.com/jersey-city-nj/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22usersSearchTerm%22%3A%22Jersey%20City%2C%20NJ%22%2C%22mapBounds%22%3A%7B%22west%22%3A-74.16915290551758%2C%22east%22%3A-73.96830909448242%2C%22south%22%3A40.657145494633546%2C%22north%22%3A40.77333599994227%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A25320%2C%22regionType%22%3A6%7D%5D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22ah%22%3A%7B%22value%22%3Atrue%7D%2C%22con%22%3A%7B%22value%22%3Afalse%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%2C%22tow%22%3A%7B%22value%22%3Afalse%7D%2C%22apa%22%3A%7B%22value%22%3Afalse%7D%2C%22apco%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A13%7D"
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

    if st.button("Run", type="secondary"):
        result = get_listings(listing_url=listing_url, api_key=api_key)
        if result.json()['is_success']:
            num_of_properties = result.json(
            )['data']['categoryTotals']['cat1']['totalResultCount']

            df_sale_listings = pd.json_normalize(
                result.json()['data']['cat1']['searchResults']['mapResults'])

            df_sale_listings.columns = [col.replace(
                'hdpData.homeInfo.', '') for col in df_sale_listings.columns]

            required_columns = [
                "zpid", "imgSrc", "detailUrl", "streetAddress", "zipcode", "city",
                "state", "latitude", "longitude", "price", "bathrooms", "bedrooms",
                "homeType", "homeStatus", "daysOnZillow", "isFeatured", "shouldHighlight",
                "is_FSBA", "isUnmappable", "isPreforeclosureAuction", "homeStatusForHDP",
                "priceForHDP", "isNonOwnerOccupied", "isPremierBuilder", "isZillowOwned",
                "currency", "country", "lotAreaValue", "lotAreaUnit", "isShowcaseListing",
                "taxAssessedValue", "rentZestimate", "zestimate", "datePriceChanged",
                "livingArea", "priceReduction", "priceChange", "streetName", "homeDetailUrl",
                "price_to_rent_ratio"
            ]
            existing_columns = [
                col for col in required_columns if col in df_sale_listings.columns]
            df_merged = df_sale_listings[existing_columns]
            df_filtered = df_merged.loc[:, ~df_merged.columns.duplicated()]
            # 1. 예외 처리 및 컬럼 추가
            # streetName 추가
            df_filtered['streetName'] = df_filtered['streetAddress']

            # homeDetailUrl 추가
            df_filtered['homeDetailUrl'] = "https://www.zillow.com" + \
                df_filtered['detailUrl']

            # is_FSBA 추가
            if 'listing_sub_type.is_FSBA' in df_sale_listings.columns:
                df_filtered['is_FSBA'] = df_sale_listings['listing_sub_type.is_FSBA']
            else:
                df_filtered['is_FSBA'] = None  # NaN 값으로 설정

            # price_to_rent_ratio 추가 (NaN으로 설정, 필요한 경우 계산하여 적용)
            df_filtered['price_to_rent_ratio'] = None  # NaN 값으로 설정

            data_for_mongo = {
                "description": "Listing data for ObjectId generation"}
            object_id, filename = listings_save_to_db(data_for_mongo)

            # GCS connect
            storage_client = gcs_connect()

            # GCS Blob Storage에 파일을 저장
            df_filtered.to_csv(filename, index=False)
            file_upload_to_gcs(filename, storage_client, prefix='listings')

            st.markdown(
                f"""
                Successfully retrieved data! Go to the analytics tab to view results.

                Search ID: {object_id}

                Number of properties matching search: {num_of_properties}
            """
            )


def get_property_info():

    st.title("Property Detail Search 🔍")
    if "visibility" not in st.session_state:
        st.session_state.visibility = "visible"
        st.session_state.disabled = False
        st.session_state.placeholder = "Enter value"

    with st.container():
        st.markdown("## 1. Enter a Unique Identifier 🏠")
        zpid = st.text_input(
            'Unique ID',
            # label_visibility=st.session_state.visibility,
            # disabled=st.session_state.disabled,
            # placeholder='1234567'
            '2078133107'
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

    if st.button("Run", type="secondary"):
        result = get_properties(api_key=api_key, zpid=zpid, address=address)

        if result.json()['is_success']:
            data = result.json()['data']
            df_prop = pd.json_normalize(data)
            for col in df_prop.columns:
                df_prop[col] = df_prop[col].apply(lambda x: str(
                    x) if isinstance(x, list) or isinstance(x, dict) else x)

            data_for_mongo = {
                "description": "Property data for ObjectId generation"}
            object_id, filename = properties_save_to_db(data_for_mongo, zpid)

            # GCS connect
            storage_client = gcs_connect()

            # GCS Blob Storage에 파일을 저장
            df_prop.to_csv(filename, index=False)
            file_upload_to_gcs(filename, storage_client, prefix='properties')

            st.markdown(
                f"""
                Successfully retrieved data! Go to the analytics tab to view results.

                Property ID: {zpid}
            """
            )


def data_analystic():
    st.title("Data Analystics 📈")

    if "visibility" not in st.session_state:
        st.session_state.visibility = "visible"
        st.session_state.disabled = False
        st.session_state.placeholder = "Enter value"

    option = st.selectbox(
        'Search Type (select below 👇)',
        ('Listings', 'Property Detail'))

    if option == 'Listings':
        prefix = 'listings'
    else:
        prefix = 'properties'

    storage_client = gcs_connect()
    files = list_files_in_gcs(storage_client, prefix)

    if files:
        selected_file = st.selectbox('Choose a file', files)

    load_button_clicked = st.button("Load File", type="secondary")

    if load_button_clicked and files:
        try:
            df = download_file_from_gcs(
                selected_file, storage_client, prefix)
            if df is None:
                st.warning(
                    f"The file {selected_file} does not exist in the storage!")
                return
            st.write(df)
        except Exception as e:
            st.error(f"An error occured: {str(e)}")


page_names_to_funcs = {
    "Home": main,
    "🏙️ Listings Search": get_listing_info,
    "🏠 Property Detail": get_property_info,
    "📊 Analystics": data_analystic,
}

feature_name = st.sidebar.selectbox(
    "Choose a feature", page_names_to_funcs.keys())
page_names_to_funcs[feature_name]()
