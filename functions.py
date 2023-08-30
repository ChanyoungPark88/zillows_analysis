from mylibs import *

# Google Cloud Storage 연결


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

# Dataframe 전처리


def preprocess_dataframe(df):
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

    df = df[required_columns]
    return df

# Price 전처리


def clean_price(value):
    # '$' 제거, 'From'이 포함된 값을 NaN으로 바꿈
    if not isinstance(value, str):
        return value
    if "From" in value:
        return None
    value = re.sub(r'[^0-9]', '', value)  # 숫자 외의 모든 문자 제거
    return float(value) if value else None


def additional_bedroom_opportunity(x):
    try:
        # 2bd >= 1300 can usually fit an additional bd
        # 3bd >= 1950 can usually fit an additional bd
        # 4bd >= 2600 can usually fit an additional bd
        if (x['ratio_sqft_bd'] >= 650) and (x['ratio_sqft_bd'] is not None) and (x['BEDS'] > 1) and (x['PROPERTY TYPE'] == 'Single Family Residential'):
            return True
        else:
            return False

    except:
        return False


def adu_potential(x):
    try:
        if (x['ratio_lot_sqft'] >= 5) and (x['ratio_lot_sqft'] is not None) and (x['HOA/MONTH'] is not None) and (x['PROPERTY TYPE'] == 'Single Family Residential'):
            return True
        else:
            return False
    except:
        return False


def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

# Retrieve Listing Data using API


def get_listings(listing_url, api_key):
    url = "https://app.scrapeak.com/v1/scrapers/zillow/listing"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)"}

    querystring = {
        "api_key": api_key,
        "url": listing_url
    }

    return requests.request("GET", url, params=querystring, headers=headers)

# Retrieve Property Data using API


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

# Save the Listing Metadata to MongoDB


def listings_save_to_db(data):
    MONGO_URL = os.environ.get('MONGO_URL')
    DB_NAME = os.environ.get('DB_NAME')
    COLLECTION_NAME = os.environ.get('LISTING_COLLECTION')

    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

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

# Save the Property Metadata to MongoDB


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

# File Download from GCS bucket


def download_file_from_gcs(filename, storage_client, prefix, bucket_name='my_project_storage'):
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(f"{prefix}/{filename}")

    if not blob.exists():
        return None

    content = blob.download_as_text()

    df = pd.read_csv(io.StringIO(content))
    return df

# Retrieve File List from GCS bucket


def list_files_in_gcs(storage_client, prefix, bucket_name='my_project_storage'):
    bucket = storage_client.get_bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=prefix)
    return [blob.name.replace(f"{prefix}/", "") for blob in blobs]
