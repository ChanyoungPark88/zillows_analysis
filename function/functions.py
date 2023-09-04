"""
This module provides functionalities related to data processing and handling for
specific use cases involving Google Cloud Storage, MongoDB, and property data management.
"""
from library.libraries import (
    os, base64, json, storage, URLError, re, np, st, datetime,
    MongoClient, requests, pd, io, timedelta, urllib
)

API_KEY = os.environ.get('API_KEY')
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko)"
    )
}

BUCKET_NAME = os.environ.get('BUCKET_NAME')
BUCKET_NAME2 = os.environ.get('BUCKET_NAME2')


def gcs_connect():
    """
    Connect to Google Cloud Storage using the provided environment variable.

    Returns:
    storage_client(storage.Client): A Google Cloud Storage client object or None if an error occurs.
    """
    # KEY Loading & Decoding
    key_content_encoded = os.environ.get('GOOGLE_CLOUD_KEY_CONTENTS')
    if not key_content_encoded:
        st.write("Key content is missing from environment variables.")
        return None

    key_content = base64.b64decode(key_content_encoded).decode()
    key_data = json.loads(key_content)

    try:
        storage_client = storage.Client.from_service_account_info(key_data)
        return storage_client

    except URLError as error_message:
        st.write(error_message)
        return None


def safe_int_conversion(value):
    """
    Safely convert the value to an integer.

    Attempts to convert the provided value to an integer. If the value cannot be
    converted to an integer, it returns the original value to avoid ValueError.

    Parameters:
    - value (mixed): The value to convert.

    Returns:
    int or mixed: Converted integer or the original value if conversion fails.
    """
    try:
        return int(value)
    except ValueError:
        return value


def preprocess_dataframe(data_frame):
    """
    Preprocess the DataFrame by selecting the required columns.

    Parameters:
    - data_frame (DataFrame): The data containing property details.

    Returns:
    DataFrame: A DataFrame containing only the required columns.
    """
    required_columns = ['zpid', 'streetAddress', 'city', 'state', 'zipcode', 'country',
                        'latitude', 'longitude', 'homeStatus', 'homeType', 'price', 'currency',
                        'bedrooms', 'bathrooms', 'livingArea', 'yearBuilt', 'zestimate',
                        'rentZestimate', 'hdpUrl', 'nearbyCities', 'nearbyNeighborhoods',
                        'nearbyZipcodes', 'schools', 'nearbyHomes', 'taxHistory',
                        'priceHistory', 'comps', 'description', 'datePostedString',
                        'timeOnZillow', 'timeZone', 'pageViewCount', 'favoriteCount',
                        'daysOnZillow', 'brokerageName', 'monthlyHoaFee', 'propertyTaxRate',
                        'hiResImageLink', 'virtualTourUrl', 'photos', 'photoCount',
                        'lotAreaValue', 'lotAreaUnits', 'priceChange', 'priceChangeDate',
                        'priceChangeDateString', 'mlsid', 'parcelId', 'countyFIPS', 'cityId',
                        'stateId']
    data_frame = data_frame[required_columns]
    return data_frame


def clean_price(value):
    """
    Clean the price value by removing unwanted characters and handling special cases.

    Parameters:
    - value (str or int or float): The price value to be cleaned.

    Returns:
    float or None: The cleaned price value.
    """
    if not isinstance(value, str):
        return value
    if "From" in value:
        return None
    value = re.sub(r'[^0-9]', '', value)  # 숫자 외의 모든 문자 제거
    return float(value) if value else None


def fix_json_string(string):
    """
    Fix the JSON string by replacing single quotes with double quotes
    and handling special formatting.

    Parameters:
    - string (str): The JSON string to be fixed.

    Returns:
    str: The fixed JSON string.
    """
    string = string.replace("'", '"')
    string = re.sub(r'(?<=[{,:])\s*(\w+)\s*(?=[,:}\]])', r'"\1"', string)
    return string


def inspect_object_columns(data_frame):
    """
    Inspect columns with object data type and display their unique values.

    Parameters:
    - data_frame (DataFrame): The data containing property details.

    Returns:
    None
    """
    for column in data_frame.columns:
        if data_frame[column].dtype == 'object':
            unique_values = data_frame[column].unique()
            st.write(f"Column Name: {column}")
            st.write(f"Unique Values: {unique_values}")


def process_object_columns(data_frame):
    """
    Process columns with object data type to handle 'None' values
    and convert strings containing numbers.

    Parameters:
    - data_frame (DataFrame): The data containing property details.

    Returns:
    None
    """
    for column in data_frame.columns:
        if data_frame[column].dtype == 'object':
            # 'None'을 NaN으로 변환
            data_frame[column] = data_frame[column].replace('None', np.nan)
            # 문자열이 숫자만 포함하고 있는지 확인
            if data_frame[column].str.isnumeric().all():
                data_frame[column] = data_frame[column].astype(float)


def get_listings(listing_url):
    """
    Retrieve listing data from the API using the provided URL.

    Parameters:
    - listing_url (str): The URL of the property listing.

    Returns:
    Response: A Response object containing the retrieved data.
    """
    url = "https://app.scrapeak.com/v1/scrapers/zillow/listing"
    querystring = {
        "api_key": API_KEY,
        "url": listing_url
    }
    return requests.request("GET", url, params=querystring, headers=HEADERS, timeout=20)


def get_properties(zpid=None, address=None):
    """
    Retrieve property data from the API using the provided ZPID or address.

    Parameters:
    - zpid (str, optional): The ZPID of the property.
    - address (str, optional): The address of the property.

    Returns:
    Response: A Response object containing the retrieved data.
    """
    url = "https://app.scrapeak.com/v1/scrapers/zillow/property"
    querystring = {
        "api_key": API_KEY,
        "zpid": zpid,
        "address": address
    }
    if zpid is not None:
        querystring['zpid'] = zpid
    if address is not None:
        querystring['address'] = address
    return requests.request("GET", url, params=querystring, headers=HEADERS, timeout=20)


def listings_save_to_db(data):
    """
    Save the Listing Metadata to MongoDB.

    Parameters:
    - data (dict): The data containing listing metadata.

    Returns:
    tuple: A tuple containing the object ID and filename.
    """
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')
    collection_name = os.environ.get('LISTING_COLLECTION')

    client = MongoClient(mongo_url)
    db_client = client[db_name]
    collection = db_client[collection_name]

    data['createAt'] = datetime.now()
    data['expireAt'] = datetime.now() + timedelta(days=1)

    result = collection.insert_one(data)
    object_id = result.inserted_id

    today = datetime.today().strftime('%Y-%m-%d')
    filename = f"{today}-{object_id}.csv"

    data['file'] = filename
    collection.update_one({'_id': object_id}, {'$set': {'file': filename}})

    client.close()

    return object_id, filename


def properties_save_to_db(data, zpid):
    """
    Save the Property Metadata to MongoDB.

    Parameters:
    - data (dict): The data containing property metadata.
    - zpid (str): The ZPID of the property.

    Returns:
    tuple: A tuple containing the object ID and filename.
    """
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')
    collection_name = os.environ.get('PROPERTY_COLLECTION')

    client = MongoClient(mongo_url)
    db_client = client[db_name]
    collection = db_client[collection_name]

    today = datetime.today().strftime('%Y-%m-%d')
    filename = f"{today}_{zpid}.csv"
    data['file'] = filename

    data['createAt'] = datetime.now()
    data['expireAt'] = datetime.now() + timedelta(days=1)

    existing_document = collection.find_one({'file': filename})

    if existing_document:
        object_id = existing_document['_id']
        collection.update_one({'_id': object_id}, {'$set': data})
    else:
        result = collection.insert_one(data)
        object_id = result.inserted_id

    client.close()

    return object_id, filename


def file_upload_to_gcs(filename, storage_client, prefix, bucket_name=BUCKET_NAME):
    """
    Upload a file to a Google Cloud Storage bucket.

    Parameters:
    - filename (str): The name of the file to upload.
    - storage_client (storage.Client): The Google Cloud Storage client.
    - prefix (str): The folder prefix in the bucket.
    - bucket_name (str, optional): The name of the bucket. Defaults to BUCKET_NAME.

    Returns:
    str: A message indicating the status of the upload.
    """
    # Get the bucket name
    bucket = storage_client.get_bucket(bucket_name)

    # Create a blob object for the file, it's like a pointer to handle the file upload
    blob_name = f"{prefix}/{filename}"
    blob = bucket.blob(blob_name)

    # Upload the file to GCS
    with open(filename, "rb") as file:
        blob.upload_from_file(file)

    return f"Uploaded {filename} to {bucket_name}/{prefix}."


def download_file_from_gcs(filename, storage_client, prefix, bucket_name=BUCKET_NAME):
    """
    Download a file from a Google Cloud Storage bucket.

    Parameters:
    - filename (str): The name of the file to download.
    - storage_client (storage.Client): The Google Cloud Storage client.
    - prefix (str): The folder prefix in the bucket.
    - bucket_name (str, optional): The name of the bucket. Defaults to BUCKET_NAME.

    Returns:
    DataFrame or None: A DataFrame containing the downloaded data or None if the file doesn't exist.
    """
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(f"{prefix}/{filename}")

    if not blob.exists():
        return None

    content = blob.download_as_text()

    data_frame = pd.read_csv(io.StringIO(content))
    return data_frame


def download_location_file_from_gcs(filename, storage_client, bucket_name=BUCKET_NAME2):
    """
    Download a file from a Google Cloud Storage bucket.

    Parameters:
    - filename (str): The name of the file to download.
    - storage_client (storage.Client): The Google Cloud Storage client.
    - prefix (str): The folder prefix in the bucket.
    - bucket_name (str, optional): The name of the bucket. Defaults to BUCKET_NAME.

    Returns:
    DataFrame or None: A DataFrame containing the downloaded data or None if the file doesn't exist.
    """
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(filename)

    if not blob.exists():
        return None

    content = blob.download_as_text()
    data_frame = pd.read_csv(io.StringIO(content))
    return data_frame


def list_files_in_gcs(storage_client, prefix, bucket_name=BUCKET_NAME):
    """
    List all files in a specific prefix of a Google Cloud Storage bucket.

    Parameters:
    - storage_client (storage.Client): The Google Cloud Storage client.
    - prefix (str): The folder prefix in the bucket.
    - bucket_name (str, optional): The name of the bucket. Defaults to BUCKET_NAME.

    Returns:
    list: A list of filenames in the specified prefix.
    """
    bucket = storage_client.get_bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=prefix)
    return [blob.name.replace(f"{prefix}/", "") for blob in blobs]


def get_states_from_usa(data_frame):
    """
    Retrieve unique states from the provided DataFrame.

    Parameters:
    - data_frame (DataFrame): DataFrame containing the data of cities in the USA.

    Returns:
    List: A list of unique states.
    """
    return data_frame["state_name"].unique().tolist()


def get_provinces_from_canada(data_frame):
    """
    Retrieve unique provinces from the provided DataFrame.

    Parameters:
    - data_frame (DataFrame): DataFrame containing the data of cities in Canada.

    Returns:
    List: A list of unique provinces.
    """
    return data_frame["province_name"].unique().tolist()


def get_cities_from_state(data_frame, state_name):
    """
    Retrieve cities for the specified state.

    Parameters:
    - df (DataFrame): DataFrame containing the data of cities in the USA.
    - state_name (str): Name of the state to retrieve cities for.

    Returns:
    List: A list of cities for the specified state.
    """
    return data_frame[data_frame["state_name"] == state_name]["city"].tolist()


def get_cities_from_province(data_frame, province_name):
    """
    Retrieve cities for the specified province.

    Parameters:
    - df (DataFrame): DataFrame containing the data of cities in Canada.
    - province_name (str): Name of the province to retrieve cities for.

    Returns:
    List: A list of cities for the specified province.
    """
    return data_frame[data_frame["province_name"] == province_name]["city"].tolist()


def generate_zillow_url(city, state, lat, lng, region_id, region_type_value=6):
    """
    Generate a Zillow search URL based on the given parameters.

    Args:
    - city (str): Name of the city.
    - state (str): State abbreviation.
    - lat (float): Latitude of the desired location.
    - lng (float): Longitude of the desired location.
    - region_id (int): Zillow's region ID for the desired location.
    - region_type_value (int, optional): Zillow's region type value. Default is 6 for city.

    Returns:
    - str: A Zillow search URL based on the given parameters.
    """
    import urllib.parse

    base_url = "https://www.zillow.com"
    formatted_city = city.replace(" ", "-").lower()
    formatted_state = state.lower()

    search_query_state = {
        "pagination": {},
        "usersSearchTerm": f"{city} {state}",
        "mapBounds": {
            "north": lat + 0.5,
            "east": lng + 0.5,
            "south": lat - 0.5,
            "west": lng - 0.5
        },
        "regionSelection": [{
            "regionId": region_id,
            "regionType": region_type_value
        }],
        "isMapVisible": True,
        "filterState": {
            "ah": {"value": True},
            "sort": {"value": "globalrelevanceex"},
            "tow": {"value": False},
            "mf": {"value": False},
            "con": {"value": False},
            "land": {"value": False},
            "apa": {"value": False},
            "manu": {"value": False},
            "apco": {"value": False}
        },
        "isListVisible": True,
        "mapZoom": 9
    }

    encoded_query = urllib.parse.quote(
        str(search_query_state).replace("'", "\""))
    url = f"{base_url}/{formatted_city}-{formatted_state}/houses/?searchQueryState={encoded_query}"

    return url
