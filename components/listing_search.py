# Module imports
from library.libraries import *

# Function imports
from function.functions import *


def get_listing_info():
    # Display the title for the web app
    st.title("Listings Search 🔍")

    # Initialize session state variables if not present
    if "visibility" not in st.session_state:
        st.session_state.visibility = "visible"
        st.session_state.disabled = False
        st.session_state.placeholder = "Enter value"

    # Container for entering the web link
    with st.container():
        st.markdown("## Enter Web Link 🌐")
        listing_url = st.text_input(
            'url',
            label_visibility=st.session_state.visibility,
            disabled=st.session_state.disabled,
            placeholder='https://www.zillow.com/...'
        )

    # If Run button is pressed
    if st.button("Run", type="secondary"):
        # Get listings data from external source/API
        result = get_listings(listing_url=listing_url)

        # If API request is successful
        if result.json()['is_success']:
            num_of_properties = result.json(
            )['data']['categoryTotals']['cat1']['totalResultCount']

            # Convert the JSON result to a DataFrame
            df_sale_listings = pd.json_normalize(
                result.json()['data']['cat1']['searchResults']['mapResults'])

            # Rename the columns for better readability
            df_sale_listings.columns = [col.replace(
                'hdpData.homeInfo.', '') for col in df_sale_listings.columns]

            # Define the list of columns needed for the analysis
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

            # Filter the dataframe to only include the required columns
            existing_columns = [
                col for col in required_columns if col in df_sale_listings.columns]
            df_merged = df_sale_listings[existing_columns]
            df_filtered = df_merged.loc[:, ~df_merged.columns.duplicated()]

            # 1. Data Processing: Column additions and manipulations
            df_filtered.loc[:, 'streetName'] = df_filtered['streetAddress']
            df_filtered.loc[:, 'homeDetailUrl'] = "https://www.zillow.com" + \
                df_filtered['detailUrl']

            # conditionally and the 'is_FSBA' column based on its presence in the original data
            if 'listing_sub_type.is_FSBA' in df_sale_listings.columns:
                df_filtered.loc[:,
                                'is_FSBA'] = df_sale_listings['listing_sub_type.is_FSBA']
            else:
                df_filtered.loc[:, 'is_FSBA'] = np.nan  # NaN 값으로 설정

            # Data type conversion and assertions
            # $ 제거
            df_filtered['price'] = df_filtered['price'].str.replace('$', '')

            # , 제거
            df_filtered['price'] = df_filtered['price'].str.replace(',', '')

            # float로 변환
            try:
                df_filtered['price'] = df_filtered['price'].astype(float)
            except ValueError as e:
                # 에러가 발생한 경우 문제가 되는 값을 출력
                problematic_value = df_filtered['price'][~df_filtered['price'].str.isnumeric(
                )]
                print("Problematic values:", problematic_value)
                raise e  # 에러를 다시 발생시켜 확인

            assert df_filtered['price'].dtype == 'float64'
            assert df_filtered['priceChange'].dtype == 'float64'
            assert df_filtered['rentZestimate'].dtype == 'float64'

            # Calculate the price_to_rent_ratio using masks (conditions)
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

            # Handle NaN values for the 'price_to_rent_ratio' column
            df_filtered['price_to_rent_ratio'].fillna(np.nan, inplace=True)

            # 2. Reorder columns for better presentation
            df_filtered = df_filtered[required_columns]

            # Prepare data for database saving and get a unique identifier
            data_for_mongo = {
                "description": "Listing data for ObjectId generation"}
            object_id, filename = listings_save_to_db(data_for_mongo)

            # Connect to Google Cloud Storage (GCS)
            storage_client = gcs_connect()

            # Save the processed data to GCS
            df_filtered.to_csv(filename, index=False)
            file_upload_to_gcs(filename, storage_client, prefix='listings')

            # Display a success message with the results
            st.markdown(
                f"""
                Successfully retrieved data! Go to the analytics tab to view results.

                Search ID: {object_id}

                Number of properties matching search: {num_of_properties}
            """
            )
