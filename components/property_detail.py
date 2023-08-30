# Module imports
from library.libraries import *

# Function imports
from function.functions import *


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

            df_prop = preprocess_dataframe(df_prop)

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
