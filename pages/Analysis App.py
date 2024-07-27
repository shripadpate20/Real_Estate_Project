import streamlit as st
import pandas as pd
import plotly.express as px
import pickle
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns

# Configure Streamlit page settings
st.set_page_config(page_title="Plotting Demo")

# App title
st.title('Analytics')

# Load data
new_df = pd.read_csv('data_viz1.csv')

# Load feature text
feature_text = pickle.load(open('feature_text.pkl', 'rb'))

# Convert relevant columns to numeric, coercing errors
new_df['price'] = pd.to_numeric(new_df['price'], errors='coerce')
new_df['price_per_sqft'] = pd.to_numeric(new_df['price_per_sqft'], errors='coerce')
new_df['built_up_area'] = pd.to_numeric(new_df['built_up_area'], errors='coerce')
new_df['latitude'] = pd.to_numeric(new_df['latitude'], errors='coerce')
new_df['longitude'] = pd.to_numeric(new_df['longitude'], errors='coerce')

# Group data by sector and calculate means for numeric columns
group_df = new_df.groupby('sector', as_index=False).mean(numeric_only=True)[
    ['sector', 'price', 'price_per_sqft', 'built_up_area', 'latitude', 'longitude']
]

# Plot Sector Price per Sqft Geomap
st.header('Sector Price per Sqft Geomap')
fig = px.scatter_mapbox(
    group_df,
    lat="latitude",
    lon="longitude",
    color="price_per_sqft",
    size='built_up_area',
    color_continuous_scale=px.colors.cyclical.IceFire,
    zoom=10,
    mapbox_style="open-street-map",
    width=1200,
    height=700,
    hover_name='sector'  # Use 'sector' as hover name since we grouped by it
)
st.plotly_chart(fig, use_container_width=True)

# Plot Features Wordcloud
st.header('Features Wordcloud')

# Ensure feature_text is not empty
if isinstance(feature_text, str) and feature_text.strip():
    wordcloud = WordCloud(
        width=800,
        height=800,
        background_color='black',
        stopwords=set(['s']),  # Any stopwords you'd like to exclude
        min_font_size=10
    ).generate(feature_text)

    # Create a matplotlib figure
    plt.figure(figsize=(8, 8), facecolor=None)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.tight_layout(pad=0)
    st.pyplot(plt.gcf())  # Pass the current figure to st.pyplot
else:
    st.error("Feature text is empty or not valid.")

# Plot Area Vs Price scatter plot
st.header('Area Vs Price')

property_type = st.selectbox('Select Property Type', ['flat', 'house'])

# Create scatter plot based on selected property type
if property_type == 'house':
    fig1 = px.scatter(
        new_df[new_df['property_type'] == 'house'],
        x="built_up_area",
        y="price",
        color="bedRoom",
        title="Area Vs Price (House)"
    )
else:
    fig1 = px.scatter(
        new_df[new_df['property_type'] == 'flat'],
        x="built_up_area",
        y="price",
        color="bedRoom",
        title="Area Vs Price (Flat)"
    )

st.plotly_chart(fig1, use_container_width=True)

# Plot BHK Pie Chart
st.header('BHK Pie Chart')

sector_options = new_df['sector'].unique().tolist()
sector_options.insert(0, 'overall')

selected_sector = st.selectbox('Select Sector', sector_options)

# Create pie chart based on selected sector
if selected_sector == 'overall':
    fig2 = px.pie(new_df, names='bedRoom', title='Overall BHK Distribution')
else:
    fig2 = px.pie(new_df[new_df['sector'] == selected_sector], names='bedRoom',
                  title=f'BHK Distribution in Sector {selected_sector}')

st.plotly_chart(fig2, use_container_width=True)

# Plot Side by Side BHK price comparison
st.header('Side by Side BHK Price Comparison')

fig3 = px.box(new_df[new_df['bedRoom'] <= 4], x='bedRoom', y='price', title='BHK Price Range Comparison')
st.plotly_chart(fig3, use_container_width=True)

# Plot Side by Side Distplot for property type
st.header('Side by Side Distplot for Property Type')

# Create the matplotlib figure for the distribution plot
fig4 = plt.figure(figsize=(10, 4))
sns.histplot(new_df[new_df['property_type'] == 'house']['price'], kde=True, label='house', color='blue')
sns.histplot(new_df[new_df['property_type'] == 'flat']['price'], kde=True, label='flat', color='orange')
plt.legend()
st.pyplot(fig4)
