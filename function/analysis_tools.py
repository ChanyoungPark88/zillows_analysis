from library.libraries import *
from function.functions import *

#####################################
#              METRICS              #
#####################################


def show_listing_metrics(df):
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
    st.markdown("## Property Metrics 🏙️")
    col1, col2, col3, col4 = st.columns(4)

    df['price'] = df['price'].astype(str).apply(clean_price)
    df = df.dropna(subset=['price'])

    col1.metric('Est Value', "${:,}".format(
        int(df['zestimate'].mean())).split(',')[0] + 'K')
    col2.metric('Est Rent Value', "${:,}".format(
        int(df['rentZestimate'].mean())).split(',')[0] + 'K')
    col3.metric('Est PBR', int(
        (df['zestimate'] / (df['rentZestimate'] * 12)).mean()))
    col4.metric('Est PPSQFT', "${:,.2f}".format(
        df['zestimate'].mean() / df['livingArea'].mean()))

#####################################
#              SUMMARY              #
#####################################


def show_property_summary(df):
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


def show_listing_charts(df):
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
    with st.expander('Charts', expanded=True):
        df['taxHistory'] = df['taxHistory'].apply(fix_json_string)
        df['taxHistory'] = df['taxHistory'].apply(json.loads)

        tax_hist_list = df['taxHistory'].iloc[0]
        tax_hist_df = pd.DataFrame(tax_hist_list)
        fig = px.line(tax_hist_df, x="time", y="taxPaid",
                      title="Historical Line Chart")
        st.plotly_chart(fig, use_container_width=True)
        st.write(tax_hist_df)

        df['priceHistory'] = df['priceHistory'].apply(fix_json_string)
        df['priceHistory'] = df['priceHistory'].apply(json.loads)

        price_hist_list = df['priceHistory'].iloc[0]
        price_hist_df = pd.DataFrame(price_hist_list)
        fig = px.line(price_hist_df, x="date", y="price",
                      title="Historical Price Line Chart")
        st.plotly_chart(fig, use_container_width=True)
        st.write(price_hist_df)


#####################################
#           COMPARABLES             #
#####################################
# def show_property_comps(df):
#     with st.expander('Charts', expanded=True):
#         df_c = pd.DataFrame(df["comps"].iloc[0])

#         # `taxPaid`와 `priceChangeRate` 열의 데이터 유형을 숫자로 변환
#         df_c['taxPaid'] = pd.to_numeric(df_c['taxPaid'], errors='coerce')
#         df_c['priceChangeRate'] = pd.to_numeric(
#             df_c['priceChangeRate'], errors='coerce')

#         st.write(df_c)


#####################################
#               DATA                #
#####################################

def show_map(df):
    with st.expander('Data', expanded=True):
        st.subheader("Map")
        st.map(df)


def show_data(df, selected_file):
    with st.expander('Data', expanded=True):
        st.subheader("Dataset")

        st.write(df.dtypes)
        df['zipcode'] = df['zipcode'].astype(int).apply(lambda x: f"{x}")
        df['zpid'] = df['zpid'].astype(int).apply(lambda x: f"{x}")
        inspect_object_columns(df)
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download 🔽",
            data=csv,
            file_name=f"{selected_file if not selected_file.endswith('.csv') else selected_file[:-4]}.csv",
            mime="text/csv"
        )
