# Module imports
from library.libraries import *

# Function imports
from function.functions import *
from function.analysis_tools import *


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
        files = [""] + files
        selected_file = st.selectbox('Choose a file', files)
        try:
            df = download_file_from_gcs(
                selected_file, storage_client, prefix)
            if df is None:
                st.success(
                    f"Choose a file from the dropdown above to view data.")
                return

            # If prefix is properties, apply main functionalities from app.py
            if prefix == 'listings':
                show_listing_metrics(df)
            else:
                show_property_metrics(df)
            df['zipcode'] = df['zipcode'].astype(int).apply(lambda x: f"{x}")
            df['zpid'] = df['zpid'].astype(int).apply(lambda x: f"{x}")

            st.dataframe(df)
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download 🔽",
                data=csv,
                file_name=f"{selected_file if not selected_file.endswith('.csv') else selected_file[:-4]}.csv",
                mime="text/csv"
            )

        except Exception as e:
            st.error(f"An error occured: {str(e)}")
