# Module imports
from library.libraries import *

# Function imports
from function.functions import *


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
            df_filtered.loc[:, 'streetName'] = df_filtered['streetAddress']

            # homeDetailUrl 추가
            df_filtered.loc[:, 'homeDetailUrl'] = "https://www.zillow.com" + \
                df_filtered['detailUrl']

            # is_FSBA 추가
            if 'listing_sub_type.is_FSBA' in df_sale_listings.columns:
                df_filtered.loc[:,
                                'is_FSBA'] = df_sale_listings['listing_sub_type.is_FSBA']
            else:
                df_filtered.loc[:, 'is_FSBA'] = np.nan  # NaN 값으로 설정

            #  데이터 타입 변환 및 확인
            df_filtered['price'] = df_filtered['price'].str.replace(
                '[^\d.]', '', regex=True).astype(float)

            df_filtered['price'] = df_filtered['price'].astype(float)
            assert df_filtered['price'].dtype == 'float64'
            assert df_filtered['priceChange'].dtype == 'float64'
            assert df_filtered['rentZestimate'].dtype == 'float64'

            # mask를 사용하여 price_to_rent_ratio 계산
            mask1 = (
                df_filtered['price'].notnull() &
                df_filtered['rentZestimate'].notnull()
            )
            df_filtered.loc[mask1, 'price_to_rent_ratio'] = df_filtered.loc[mask1,
                                                                            'price'].values / df_filtered.loc[mask1, 'rentZestimate'].values

            mask2 = (
                df_filtered['price'].notnull() &
                df_filtered['priceChange'].notnull() &
                df_filtered['rentZestimate'].notnull()
            )
            df_filtered.loc[mask2, 'price_to_rent_ratio'] = (
                df_filtered.loc[mask2, 'price'].values +
                df_filtered.loc[mask2, 'priceChange'].values
            ) / df_filtered.loc[mask2, 'rentZestimate'].values

            # price_to_rent_ratio의 나머지 NaN 값 설정 (이 부분은 사실 필요 없을 수 있습니다.
            # 왜냐하면 새로운 컬럼을 추가할 때 pandas는 자동으로 NaN 값을 할당하기 때문입니다.)
            df_filtered['price_to_rent_ratio'].fillna(np.nan, inplace=True)

            # 2. 컬럼 순서 변경
            df_filtered = df_filtered[required_columns]

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
