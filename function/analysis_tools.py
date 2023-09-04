"""
This module provides functions and utilities for displaying property metrics,
charts, summaries, and associated data using Streamlit. The module makes use
of external libraries for data manipulation and visualization, and utility
functions for data cleaning and processing.
"""
from library.libraries import st, px, pd, json
from function.functions import clean_price, fix_json_string, safe_int_conversion

#####################################
#              METRICS              #
#####################################


def show_listing_metrics(data_frame):
    """
    Display metrics related to property listings.

    Parameters:
    - data_frame (DataFrame): The data containing property listings.

    Returns:
    None
    """
    data_frame = data_frame.copy()
    st.markdown("## Property Metrics 🏙️")
    col1, col2, col3, col4 = st.columns(4)

    data_frame['price'] = data_frame['price'].astype(str).apply(clean_price)
    data_frame = data_frame.dropna(subset=['price'])

    col1.metric('Total', len(data_frame))
    col2.metric('Avg Sale Price',
                f"${int(data_frame['price'].mean()):,}".split(',')[0] + 'K')

    if 'zestimate' in data_frame.columns:
        col3.metric('Avg Est Value',
                    f"${int(data_frame['zestimate'].mean()):,}".split(',')[0] + 'K')
    else:
        col3.metric('Avg Est Value', 'N/A')

    if 'rentZestimate' in data_frame.columns:
        col4.metric('Avg Est Rent',
                    f"${int(data_frame['rentZestimate'].mean()):,}".split(',')[0] + 'K')
    else:
        col4.metric('Avg Est Rent', 'N/A')


def show_property_metrics(data_frame):
    """
    Display metrics related to individual properties.

    Parameters:
    - data_frame (DataFrame): The data containing individual properties.

    Returns:
    None
    """
    data_frame = data_frame.copy()
    st.markdown("## Property Metrics 🏙️")
    col1, col2, col3, col4 = st.columns(4)

    # 가격을 숫자로 변환
    data_frame['price'] = data_frame['price'].astype(
        str).apply(clean_price).astype(float)

    # NaN 값 처리 (예: 평균으로 NaN 값을 채움)
    data_frame['price'].fillna(data_frame['price'].mean(), inplace=True)

    col1.metric(
        'Est Value', f"${int(data_frame['zestimate'].mean()):,}".split(',')[0] + 'K')
    col2.metric('Est Rent Value',
                f"${int(data_frame['rentZestimate'].mean()):,}".split(',')[0] + 'K')

    # 0으로 나누는 경우를 방지
    rent_estimate = data_frame['rentZestimate'].mean() * 12
    if rent_estimate != 0:
        col3.metric('Est PBR', int(
            data_frame['zestimate'].mean() / rent_estimate))
    else:
        col3.metric('Est PBR', 'N/A')

    living_area_mean = data_frame['livingArea'].mean()
    if living_area_mean != 0:
        col4.metric(
            'Est PPSQFT', f"${data_frame['zestimate'].mean() / living_area_mean:,.2f}")

    else:
        col4.metric('Est PPSQFT', 'N/A')


#####################################
#              SUMMARY              #
#####################################


def show_property_summary(data_frame):
    """
    Display a summary of a selected property.

    Parameters:
    - data_frame (DataFrame): The data containing properties.

    Returns:
    None
    """
    data_frame = data_frame.copy()
    with st.expander('Summary', expanded=True):
        street_name = data_frame['streetAddress'].iloc[0]
        st.subheader(street_name)

        col1, col2 = st.columns(2)
        # Display the photo in col1
        photo_url = data_frame['hiResImageLink'].iloc[0]
        col1.image(photo_url, use_column_width=True)

        col2.markdown(f"**Bedrooms:** {data_frame['bedrooms'].iloc[0]}")
        col2.markdown(f"**Bathrooms:** {data_frame['bathrooms'].iloc[0]}")
        col2.markdown(f"**Sqft:** {data_frame['livingArea'].iloc[0]}")
        col2.markdown(f"**Lot Size:** {data_frame['lotAreaValue'].iloc[0]}")
        col2.markdown(f"**Year Built:** {data_frame['yearBuilt'].iloc[0]}")
        col2.markdown(f"**Home Type:** {data_frame['homeType'].iloc[0]}")

        description_content = data_frame['description'].iloc[0]
        formatted_description = description_content.replace('. ', '.\n\n')
        st.markdown(f"**Description:**\n\n{formatted_description}")


#####################################
#             CHARTS                #
#####################################

def show_listing_charts(data_frame):
    """
    Display charts related to property listings.

    Parameters:
    - data_frame (DataFrame): The data containing property listings.

    Returns:
    None
    """
    data_frame = data_frame.copy()
    with st.expander('Charts', expanded=True):

        if 'price' in data_frame.columns:
            fig = px.box(data_frame, x="price", title="Sales Price Box Chart")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Column 'price' missing. Cannot display "
                       "Sales Price Box Chart.")

        if 'zestimate' in data_frame.columns:
            fig = px.histogram(data_frame, x="zestimate",
                               title="Estimate Value Histogram Chart")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Column 'zestimate' missing. Cannot display "
                       "Estimate Value Histogram Chart.")

        if 'rentZestimate' in data_frame.columns:
            fig = px.histogram(data_frame, x="rentZestimate",
                               title="Rent Estimate Value Histogram Chart")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Column 'rentZestimate' missing. Cannot display "
                       "Rent Estimate Value Histogram Chart.")

        if 'price_to_rent_ratio' in data_frame.columns:
            fig = px.box(data_frame, x="price_to_rent_ratio",
                         title="Price to Rent Ratio Box Chart")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Column 'price_to_rent_ratio' missing. Cannot display "
                       "Price to Rent Ratio Box Chart.")


def show_property_charts(data_frame):
    """
    Display charts related to individual properties.

    Parameters:
    - data_frame (DataFrame): The data containing individual properties.

    Returns:
    None
    """
    data_frame = data_frame.copy()
    with st.expander('Charts', expanded=True):
        data_frame['taxHistory'] = data_frame['taxHistory'].apply(
            fix_json_string)
        data_frame['taxHistory'] = data_frame['taxHistory'].apply(json.loads)

        tax_hist_list = data_frame['taxHistory'].iloc[0]
        if tax_hist_list:  # 값이 있으면 실행
            tax_hist_data_frame = pd.DataFrame(tax_hist_list)
            if 'time' in tax_hist_data_frame.columns:  # 'time' 열이 있는지 확인
                fig = px.line(tax_hist_data_frame, x="time", y="taxPaid",
                              title="Historical Line Chart")
                st.plotly_chart(fig, use_container_width=True)
                st.write(tax_hist_data_frame)
            else:
                st.warning(
                    "'time' column not found in 'tax_hist_data_frame'. Cannot display chart.")
        else:
            st.warning("'taxHistory' is empty. No data to display.")

        data_frame['priceHistory'] = data_frame['priceHistory'].apply(
            fix_json_string)
        data_frame['priceHistory'] = data_frame['priceHistory'].apply(
            json.loads)

        price_hist_list = data_frame['priceHistory'].iloc[0]
        if price_hist_list:  # 값이 있으면 실행
            price_hist_data_frame = pd.DataFrame(price_hist_list)
            if 'date' in price_hist_data_frame.columns:  # 'date' 열이 있는지 확인
                fig = px.line(price_hist_data_frame, x="date", y="price",
                              title="Historical Price Line Chart")
                st.plotly_chart(fig, use_container_width=True)
                st.write(price_hist_data_frame)
            else:
                st.warning(
                    "'date' column not found in 'price_hist_data_frame'. Cannot display chart.")
        else:
            st.warning("'priceHistory' is empty. No data to display.")


#####################################
#               DATA                #
#####################################

def show_map_and_data(data_frame, selected_file):
    """
    Display map and data table of the given dataset.

    Parameters:
    - data_frame (DataFrame): The dataset containing properties.
    - selected_file (str): Name of the selected file for downloading.

    Returns:
    None
    """
    data_frame = data_frame.copy()

    with st.expander('Data', expanded=True):
        # Map
        st.subheader("Map")
        st.map(data_frame)

        # Dataset
        st.subheader("Dataset")

        # st.write(data_frame.dtypes)
        data_frame['zipcode'] = data_frame['zipcode'].apply(
            safe_int_conversion).apply(lambda x: f"{x}")
        data_frame['zpid'] = data_frame['zpid'].apply(
            safe_int_conversion).apply(lambda x: f"{x}")

        st.write(data_frame)

        csv = data_frame.to_csv(index=False)
        st.download_button(
            label="Download 🔽",
            data=csv,
            file_name=(
                f"{selected_file if not selected_file.endswith('.csv') else selected_file[:-4]}.csv"
            ),
            mime="text/csv"
        )
