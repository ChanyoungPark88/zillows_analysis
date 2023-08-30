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
        df['taxHistory'] = df['taxHistory'].apply(
            lambda x: json.loads(x.replace("'", '"')))

        # 여기서부터는 taxHistory 열을 DataFrame으로 변환하거나 그래프를 그리는 등의 작업을 계속하면 됩니다.
        tax_hist_list = df["taxHistory"].iloc[0]
        st.write(tax_hist_list)


#####################################
#               DATA                #
#####################################


def show_data(df, selected_file):
    with st.expander('Data', expanded=True):
        st.subheader("Map")
        st.map(df)
        st.subheader("Dataset")
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
