"""
Module for retrieving and processing property listing information.

This module fetches property listing details from a given URL,
processes the data, and uploads it to Google Cloud Storage.
"""
from library.libraries import st, pd, np
from function.functions import get_listings, listings_save_to_db, gcs_connect, file_upload_to_gcs


def get_listing_info():
    """
    Retrieve property listings from a given URL, process the data,
    and upload to Google Cloud Storage.

    Parameters:
    - None

    Returns:
    - None
    """
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
            df_filtered = df_filtered.copy()
            df_filtered.loc[:, 'streetName'] = df_filtered['streetAddress']
            if 'homeDetailUrl' in df_filtered.columns:
                df_filtered.loc[:, 'homeDetailUrl'] = "https://www.zillow.com" + \
                    df_filtered['homeDetailUrl']
            else:
                print("'homeDetailUrl' column not found in df_filtered.")

            if 'listing_sub_type.is_FSBA' in df_sale_listings.columns:
                df_filtered['is_FSBA'] = df_sale_listings['listing_sub_type.is_FSBA']
            else:
                df_filtered['is_FSBA'] = np.nan

            df_filtered = df_filtered[~df_filtered['price'].str.contains(
                'From', na=False)]
            df_filtered['price'] = df_filtered['price'].str.replace(
                r'\$|,', '', regex=True)

            df_filtered['original_price'] = df_filtered['price']

            try:
                df_filtered['price'] = df_filtered['price'].str.replace(
                    '[^0-9]', '', regex=True).astype(int)

            except ValueError as error_message:
                raise error_message

            assert df_filtered['price'].dtype == 'int64'

            mask1_price = df_filtered['price'].notnull()
            mask1_rent = (
                'rentZestimate' in df_filtered.columns
                and df_filtered['rentZestimate'].notnull()
            )

            if mask1_rent.any():
                mask1 = mask1_price & mask1_rent
                df_filtered.loc[mask1, 'price_to_rent_ratio'] = (
                    df_filtered.loc[mask1, 'price'] /
                    df_filtered.loc[mask1, 'rentZestimate']
                )

            else:
                # 'rentZestimate' 열이 없을 때의 처리. 필요하다면 경고 메시지를 출력하거나 다른 처리를 할 수 있습니다.
                print("'rentZestimate' column not found in df_filtered.")

            mask2_price = df_filtered['price'].notnull()
            mask2_price_change = False
            if 'priceChange' in df_filtered.columns:
                mask2_price_change = df_filtered['priceChange'].notnull()

            mask2_rent = (
                'rentZestimate' in df_filtered.columns and
                df_filtered['rentZestimate'].notnull()
            )

            if mask2_rent.any():
                mask2 = mask2_price & mask2_price_change & mask2_rent
                df_filtered.loc[mask2, 'price_to_rent_ratio'] = (
                    df_filtered.loc[mask2, 'price'] +
                    df_filtered.loc[mask2, 'priceChange']
                ) / df_filtered.loc[mask2, 'rentZestimate']

            else:
                # 'rentZestimate' 열이 없을 때의 처리. 필요하다면 경고 메시지를 출력하거나 다른 처리를 할 수 있습니다.
                print("'rentZestimate' column not found in df_filtered.")

            if 'price_to_rent_ratio' in df_filtered.columns:
                df_filtered['price_to_rent_ratio'].fillna(np.nan, inplace=True)
            else:
                df_filtered['price_to_rent_ratio'] = np.nan

            df_filtered['zipcode'] = df_filtered['zipcode'].astype(str)
            df_filtered['zpid'] = df_filtered['zpid'].astype(str)

            existing_required_columns = [
                col for col in required_columns if col in df_filtered.columns]
            df_filtered = df_filtered[existing_required_columns]

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
            # st.write(e)
            st.markdown(
                f"""
                Successfully retrieved data! Go to the analytics tab to view results.

                Search ID: {object_id}

                Number of properties matching search: {num_of_properties}
            """
            )
