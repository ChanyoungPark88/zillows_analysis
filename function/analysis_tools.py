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

    col1.metric('Total', len(df))
    col2.metric('Avg Price', "${:,}".format(
        int(df['price'].mean())).split(',')[0] + 'K')
    col3.metric('Avg DOM', int(df['daysOnZillow'].mean()))
    col4.metric('Avg PPSQFT', "${:,}".format(
        int(df['lotAreaValue'].mean())))

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
        fig = px.histogram(df, x="daysOnZillow",
                           title="Days on Market Histogram Chart")
        st.plotly_chart(fig, use_container_width=True)
        fig = px.box(df, x="price", title="Price Box Plot Chart")
        st.plotly_chart(fig, use_container_width=True)
        fig = px.histogram(df, x="lotAreaValue",
                           title="Price per SQFT Histogram Chart")
        st.plotly_chart(fig, use_container_width=True)

#####################################
#               DATA                #
#####################################


def show_data(df, selected_file):
    with st.expander('Data', expanded=True):
        st.map(df)
        st.dataframe(df)
        csv = df.to_csv(index=False)

        st.download_button(
            label="Download 🔽",
            data=csv,
            file_name=f"{selected_file if not selected_file.endswith('.csv') else selected_file[:-4]}.csv",
            mime="text/csv"
        )
