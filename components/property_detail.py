# Module imports
from library.libraries import *

# Function imports
from function.functions import *


def get_property_info():

    # Set the title for the Streamlit app
    st.title("Property Detail Search 🔍")

    # Check if session states are initialized, if not, set them
    if "visibility" not in st.session_state:
        st.session_state.visibility = "visible"
        st.session_state.disabled = False
        st.session_state.placeholder = "Enter value"

    # Create a Streamlit container for user input
    with st.container():
        st.markdown("## 1. Enter a Unique Identifier 🏠")

        # Get zpid input from the user
        zpid = st.text_input(
            'Unique ID',
            label_visibility=st.session_state.visibility,
            disabled=st.session_state.disabled,
            placeholder='1234567'
        )

        # Offer an alternative input method for address
        st.text('or')

        # Get address input from the user
        address = st.text_input(
            'Full Address',
            label_visibility=st.session_state.visibility,
            disabled=st.session_state.disabled,
            placeholder='110 1st St, Jersey City, NJ 07302'
        )

    # Check if user has clicked the "Run" button
    if st.button("Run", type="secondary"):

        # Call function to get properties using provided inputs
        result = get_properties(zpid=zpid, address=address)

        # Check if the API call was successful
        if result.json()['is_success']:

            # Parse the JSON response to a DataFrame
            data = result.json()['data']
            df_prop = pd.json_normalize(data)
            for col in df_prop.columns:
                df_prop[col] = df_prop[col].apply(lambda x: str(
                    x) if isinstance(x, list) or isinstance(x, dict) else x)

            # Preprocess the obtained DataFrame
            df_prop = preprocess_dataframe(df_prop)

            # Save the data to the database and get relevant info
            data_for_mongo = {
                "description": "Property data for ObjectId generation"}
            object_id, filename = properties_save_to_db(data_for_mongo, zpid)

            # Connect to Google Cloud Storage
            storage_client = gcs_connect()

            # Upload the DataFrame as CSV to GCS
            df_prop.to_csv(filename, index=False)
            file_upload_to_gcs(filename, storage_client, prefix='properties')

            # Show success message to user
            st.markdown(
                f"""
                Successfully retrieved data! Go to the analytics tab to view results.

                Property ID: {zpid}
            """
            )
