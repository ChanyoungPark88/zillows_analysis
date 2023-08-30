# Module imports
from library.libraries import *

# Function imports
from function.functions import *


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
            st.write(df)

            # If prefix is properties, apply main functionalities from app.py
            if prefix == 'properties':
                #####################################
                #              METRICS              #
                #####################################
                st.markdown("## Property Metrics 🏙️")
                col1, col2, col3, col4 = st.columns(4)

                df['price'] = df['price'].astype(str).apply(clean_price)
                df = df.dropna(subset=['price'])

                col1.metric('Total', len(df))
                col2.metric('Avg Price', "${:,}".format(
                    int(df['price'].mean())).split(',')[0] + 'K')
                col3.metric('Avg DOM', int(df['daysOnZillow'].mean()))
                col4.metric('Avg PPSQFT', "${:,}".format(
                    int(df['lotAreaValue'].mean())))

                #####################################
                #             CHARTS                #
                #####################################
                with st.expander('Charts', expanded=True):
                    fig = px.histogram(df, x="daysOnZillow",
                                       title="Days on Market Histogram Chart")
                    st.plotly_chart(fig, use_container_width=True)
                    fig = px.box(df, x="price", title="Price Box Plot Chart")
                    st.plotly_chart(fig, use_container_width=True)
                    fig = px.histogram(df, x="lotAreaValue",
                                       title="Price per SQFT Histogram Chart")
                    st.plotly_chart(fig, use_container_width=True)

                #####################################
                #             FEATURES              #
                #####################################
                df_features = df.copy()
                df_features['ratio_sqft_bd'] = df_features['SQUARE FEET'] / \
                    df_features['BEDS']
                df_features['additional_bd_opp'] = df_features.apply(
                    lambda x: additional_bedroom_opportunity(x), axis=1)
                df_features['ratio_lot_sqft'] = df_features['LOT SIZE'] / \
                    df_features['SQUARE FEET']
                df_features['adu_potential'] = df_features.apply(
                    lambda x: adu_potential(x), axis=1)

                #####################################
                #              TABLES               #
                #####################################
                # with st.expander('Opportunities', expanded=True):
                #     df_add_bd = df_features.loc[df_features['additional_bd_opp'] == True]
                #     df_adu = df_features.loc[df_features['adu_potential'] == True]

                #     col1, col2 = st.columns(2)
                #     col1.metric('Total Add Bd', len(df_add_bd))
                #     col2.metric('Total ADU', len(df_adu))

                #     st.write(df_features)

                #     csv = df_features.to_csv(index=False)
                #     st.download_button(
                #         label="Download 🔽",
                #         data=csv,
                #         file_name=f"{selected_file}_features.csv",
                #         mime="text/csv"
                #     )

            csv = df.to_csv(index=False)
            st.download_button(
                label="Download 🔽",
                data=csv,
                file_name=f"{selected_file}.csv",
                mime="text/csv"
            )

        except Exception as e:
            st.error(f"An error occured: {str(e)}")
