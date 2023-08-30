from library.libraries import *
from function.functions import *

#####################################
#              METRICS              #
#####################################


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


def show_listing_metrics(df):
    st.markdown("## Property Metrics 🏙️")
    col1, col2, col3, col4 = st.columns(4)

    df['price'] = df['price'].astype(str).apply(clean_price)
    df = df.dropna(subset=['price'])

    col1.metric('Total', len(df))
    col2.metric('Avg Sale Price', "${:,}".format(
        int(df['zestimage'].mean())).split(',')[0] + 'K')
    col3.metric('Avg Est Value', "${:,}".format(
        int(df['zestimate'].mean())).split(',')[0] + 'K')
    col4.metric('Avg Est Rent', "${:,}".format(
        int(df['rentZestimate'].mean())).split(',')[0] + 'K')
#####################################
#             CHARTS                #
#####################################


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
#             FEATURES              #
#####################################


def show_property_features(df):
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


def show_property_tables(df):
    pass
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
