"""
This module provides functionalities related to data processing and handling for
specific use cases involving Google Cloud Storage, MongoDB, and property data management.
"""
from library.libraries import (
    os, base64, json, storage, URLError, re, np, st, datetime,
    MongoClient, requests, pd, io, timedelta
)

API_KEY = os.environ.get('API_KEY')
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko)"
    )
}

BUCKET_NAME = os.environ.get('BUCKET_NAME')


def gcs_connect():
    """Connect to Google Cloud Storage using the provided environment variable."""
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


def preprocess_dataframe(data_frame):
    """Preprocess the DataFrame by selecting the required columns."""
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
    """Clean the price value by removing unwanted characters and handling special cases."""
    if not isinstance(value, str):
        return value
    if "From" in value:
        return None
    value = re.sub(r'[^0-9]', '', value)  # 숫자 외의 모든 문자 제거
    return float(value) if value else None


def fix_json_string(string):
    """Fix the JSON string by replacing single quotes with double quotes
    and handling special formatting."""
    string = string.replace("'", '"')
    string = re.sub(r'(?<=[{,:])\s*(\w+)\s*(?=[,:}\]])', r'"\1"', string)
    return string


def inspect_object_columns(data_frame):
    """Inspect columns with object data type and display their unique values."""
    for column in data_frame.columns:
        if data_frame[column].dtype == 'object':
            unique_values = data_frame[column].unique()
            st.write(f"Column Name: {column}")
            st.write(f"Unique Values: {unique_values}")


def process_object_columns(data_frame):
    """Process columns with object data type to handle 'None' values
    and convert strings containing numbers."""
    for column in data_frame.columns:
        if data_frame[column].dtype == 'object':
            # 'None'을 NaN으로 변환
            data_frame[column] = data_frame[column].replace('None', np.nan)
            # 문자열이 숫자만 포함하고 있는지 확인
            if data_frame[column].str.isnumeric().all():
                data_frame[column] = data_frame[column].astype(float)


def get_listings(listing_url):
    """Retrieve listing data from the API using the provided URL."""
    url = "https://app.scrapeak.com/v1/scrapers/zillow/listing"
    querystring = {
        "api_key": API_KEY,
        "url": listing_url
    }
    return requests.request("GET", url, params=querystring, headers=HEADERS)


def get_properties(zpid=None, address=None):
    """Retrieve property data from the API using the provided ZPID or address."""
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
    return requests.request("GET", url, params=querystring, headers=HEADERS)


def listings_save_to_db(data):
    """Save the Listing Metadata to MongoDB."""
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
    """Save the Property Metadata to MongoDB."""
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


# File Upload to GCS bucket
def file_upload_to_gcs(filename, storage_client, prefix, bucket_name=BUCKET_NAME):
    """Upload a file to a Google Cloud Storage bucket."""
    # Get the bucket name
    bucket = storage_client.get_bucket(bucket_name)

    # Create a blob object for the file, it's like a pointer to handle the file upload
    blob_name = f"{prefix}/{filename}"
    blob = bucket.blob(blob_name)

    # Upload the file to GCS
    with open(filename, "rb") as file:
        blob.upload_from_file(file)

    return f"Uploaded {filename} to {bucket_name}/{prefix}."


# File Download from GCS bucket
def download_file_from_gcs(filename, storage_client, prefix, bucket_name=BUCKET_NAME):
    """Download a file from a Google Cloud Storage bucket."""
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(f"{prefix}/{filename}")

    if not blob.exists():
        return None

    content = blob.download_as_text()

    data_frame = pd.read_csv(io.StringIO(content))
    return data_frame


# Retrieve File List from GCS bucket
def list_files_in_gcs(storage_client, prefix, bucket_name=BUCKET_NAME):
    """List all files in a specific prefix of a Google Cloud Storage bucket."""
    bucket = storage_client.get_bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=prefix)
    return [blob.name.replace(f"{prefix}/", "") for blob in blobs]
