"""
Data Analytics Module.

This module provides functionalities to analyze Zillow data.
It interfaces with Google Cloud Storage to fetch the data files and then uses the functions
from the `analysis_tools` to display metrics, charts, summaries, and maps.
"""

from library.libraries import st

from function.functions import gcs_connect, list_files_in_gcs, download_file_from_gcs
from function.analysis_tools import (
    show_listing_metrics, show_listing_charts,
    show_property_metrics, show_property_summary,
    show_property_charts, show_map_and_data
)


def data_analystic():
    """
    Display the Data Analytics section in the application UI.

    Parameters:
    - None

    Returns:
    - None

    The function provides a UI to let users choose between Listing and Property data.
    Based on the choice, relevant charts and metrics are displayed.
    """
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
        files = ["Select a file"] + files
        selected_file = st.selectbox('Choose a file', files)
        try:
            data_frame = download_file_from_gcs(
                selected_file, storage_client, prefix)
            if data_frame is None:
                st.success(
                    "Choose a file from the dropdown above to view data.")
                return

            if prefix == 'listings':
                st.title("Charts 📈")
                show_listing_metrics(data_frame)
                show_listing_charts(data_frame)
                show_map_and_data(data_frame, selected_file)
            else:
                show_property_metrics(data_frame)
                show_property_summary(data_frame)
                show_property_charts(data_frame)
                show_map_and_data(data_frame, selected_file)

        except (IOError, ValueError) as error_message:
            st.error(f"An error occurred: {str(error_message)}")
