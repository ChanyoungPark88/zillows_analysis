import matplotlib.pyplot as plt
import seaborn as sns
from library.libraries import *
from function.functions import *

#####################################
#              METRICS              #
#####################################


def show_listing_metrics(df):
    df = df.copy()
    st.markdown("## Property Metrics 🏙️")
    col1, col2, col3, col4 = st.columns(4)

    df['price'] = df['price'].astype(str).apply(clean_price)
    df = df.dropna(subset=['price'])

    col1.metric('Total', len(df))
    col2.metric('Avg Sale Price', "${:,}".format(
        int(df['price'].mean())).split(',')[0] + 'K')
    col3.metric('Avg Est Value', "${:,}".format(
        int(df['zestimate'].mean())).split(',')[0] + 'K')
    col4.metric('Avg Est Rent', "${:,}".format(
        int(df['rentZestimate'].mean())).split(',')[0] + 'K')


def show_property_metrics(df):
    df = df.copy()
    st.markdown("## Property Metrics 🏙️")
    col1, col2, col3, col4 = st.columns(4)

    # 가격을 숫자로 변환
    df['price'] = df['price'].astype(str).apply(clean_price).astype(float)
    df['priceChangeRate'] = df['priceChangeRate'].apply(clean_price)

    # NaN 값 처리 (예: 평균으로 NaN 값을 채움)
    df['price'].fillna(df['price'].mean(), inplace=True)

    col1.metric('Est Value', "${:,}".format(
        int(df['zestimate'].mean())).split(',')[0] + 'K')
    col2.metric('Est Rent Value', "${:,}".format(
        int(df['rentZestimate'].mean())).split(',')[0] + 'K')

    # 0으로 나누는 경우를 방지
    rent_estimate = df['rentZestimate'].mean() * 12
    if rent_estimate != 0:
        col3.metric('Est PBR', int(df['zestimate'].mean() / rent_estimate))
    else:
        col3.metric('Est PBR', 'N/A')

    living_area_mean = df['livingArea'].mean()
    if living_area_mean != 0:
        col4.metric('Est PPSQFT', "${:,.2f}".format(
            df['zestimate'].mean() / living_area_mean))
    else:
        col4.metric('Est PPSQFT', 'N/A')


#####################################
#              SUMMARY              #
#####################################


def show_property_summary(df):
    df = df.copy()
    with st.expander('Summary', expanded=True):
        street_name = df['streetAddress'].iloc[0]
        st.subheader(street_name)

        col1, col2 = st.columns(2)
        # Display the photo in col1
        photo_url = df['hiResImageLink'].iloc[0]
        col1.image(photo_url, use_column_width=True)

        col2.markdown(f"**Bedrooms:** {df['bedrooms'].iloc[0]}")
        col2.markdown(f"**Bathrooms:** {df['bathrooms'].iloc[0]}")
        col2.markdown(f"**Sqft:** {df['livingArea'].iloc[0]}")
        col2.markdown(f"**Lot Size:** {df['lotAreaValue'].iloc[0]}")
        col2.markdown(f"**Year Built:** {df['yearBuilt'].iloc[0]}")
        col2.markdown(f"**Home Type:** {df['homeType'].iloc[0]}")

        description_content = df['description'].iloc[0]
        formatted_description = description_content.replace('. ', '.\n\n')
        st.markdown(f"**Description:**\n\n{formatted_description}")


#####################################
#             CHARTS                #
#####################################

# Plotly Express Version
def show_listing_charts(df):
    df = df.copy()
    with st.expander('Charts', expanded=True):
        fig = px.box(df, x="price", title="Sales Price Box Chart")
        st.plotly_chart(fig, use_container_width=True)
        fig = px.histogram(df, x="zestimate",
                           title="Estimate Value Histogram Chart")
        st.plotly_chart(fig, use_container_width=True)
        fig = px.histogram(df, x="rentZestimate",
                           title="Rent Estimate Value Histogram Chart")
        st.plotly_chart(fig, use_container_width=True)
        fig = px.box(df, x="price_to_rent_ratio",
                           title="Price to Rent Ratio Box Chart")
        st.plotly_chart(fig, use_container_width=True)


def show_property_charts(df):
    df = df.copy()
    with st.expander('Charts', expanded=True):
        df['taxHistory'] = df['taxHistory'].apply(fix_json_string)
        df['taxHistory'] = df['taxHistory'].apply(json.loads)

        tax_hist_list = df['taxHistory'].iloc[0]
        if tax_hist_list:  # 값이 있으면 실행
            tax_hist_df = pd.DataFrame(tax_hist_list)
            if 'time' in tax_hist_df.columns:  # 'time' 열이 있는지 확인
                fig = px.line(tax_hist_df, x="time", y="taxPaid",
                              title="Historical Line Chart")
                st.plotly_chart(fig, use_container_width=True)
                st.write(tax_hist_df)
            else:
                st.warning(
                    "'time' column not found in 'tax_hist_df'. Cannot display chart.")
        else:
            st.warning("'taxHistory' is empty. No data to display.")

        df['priceHistory'] = df['priceHistory'].apply(fix_json_string)
        df['priceHistory'] = df['priceHistory'].apply(json.loads)

        price_hist_list = df['priceHistory'].iloc[0]
        if price_hist_list:  # 값이 있으면 실행
            price_hist_df = pd.DataFrame(price_hist_list)
            if 'date' in price_hist_df.columns:  # 'date' 열이 있는지 확인
                fig = px.line(price_hist_df, x="date", y="price",
                              title="Historical Price Line Chart")
                st.plotly_chart(fig, use_container_width=True)
                st.write(price_hist_df)
            else:
                st.warning(
                    "'date' column not found in 'price_hist_df'. Cannot display chart.")
        else:
            st.warning("'priceHistory' is empty. No data to display.")


#####################################
#               DATA                #
#####################################

def show_map_and_data(df, selected_file):
    df = df.copy()

    with st.expander('Data', expanded=True):
        # Map
        st.subheader("Map")
        st.map(df)

        # Dataset
        st.subheader("Dataset")

        # st.write(df.dtypes)
        df['zipcode'] = df['zipcode'].astype(int).apply(lambda x: f"{x}")
        df['zpid'] = df['zpid'].astype(int).apply(lambda x: f"{x}")

        st.write(df)

        csv = df.to_csv(index=False)
        st.download_button(
            label="Download 🔽",
            data=csv,
            file_name=f"{selected_file if not selected_file.endswith('.csv') else selected_file[:-4]}.csv",
            mime="text/csv"
        )
