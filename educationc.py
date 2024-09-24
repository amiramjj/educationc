import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Function to clean refArea names
def clean_refarea(area):
    return area.replace("https://dbpedia.org/page/", "").replace("_", " ")

# Set up the Streamlit app
st.set_page_config(page_title="Education Data Visualization", layout="wide")
st.title('Education in Lebanon - Data Visualization')

# Load the dataset
df = pd.read_csv('https://linked.aub.edu.lb/pkgcube/data/2166f86583f33e05dbfdf2364473a12f_20240908_112155.csv')

# Clean the 'refArea' column
df['refArea'] = df['refArea'].apply(clean_refarea)

# Checkbox to show/hide raw data
if st.checkbox('Show raw data'):
    st.subheader('Raw Data')
    st.dataframe(df, height=1200)

# Bar Chart: Comparison of Education Levels in Governorates
st.title("Bar Chart: Comparison of Education Levels in Governorates")
governorate_data = df[df['refArea'].str.contains('Governorate')].groupby('refArea').agg(
    {col: 'mean' for col in df.columns if 'PercentageofEducationlevelofresidents' in col}
).reset_index()

# Add a filter to select specific governorates
selected_governorates = st.multiselect(
    "Select Governorates",
    options=governorate_data["refArea"].unique(),
    default=governorate_data["refArea"].unique()
)

# Filter the data based on selected governorates
filtered_data = governorate_data[governorate_data["refArea"].isin(selected_governorates)]

# Add filters for education levels
education_levels = {level.split('-')[-1]: level for level in df.columns if 'PercentageofEducationlevelofresidents' in level}
selected_education_levels = st.multiselect(
    "Select Education Levels",
    options=list(education_levels.keys()),
    default=list(education_levels.keys())
)

# Filter columns based on selected education levels
selected_columns = [education_levels[level] for level in selected_education_levels]
filtered_data = filtered_data[['refArea'] + selected_columns] if selected_columns else filtered_data[['refArea']]

# Create a bar chart
fig = go.Figure()
for column in selected_columns:
    fig.add_trace(go.Bar(name=column.split('-')[-1], x=filtered_data['refArea'], y=filtered_data[column]))

# Customize the layout
fig.update_layout(
    title="Comparison of Education Levels in Selected Governorates",
    xaxis_title="Governorate",
    yaxis_title="Percentage of Residents",
    barmode='group'
)

# Display the chart in Streamlit
st.plotly_chart(fig)
st.write("Each governorate has a set of bars representing the mean percentage of residents with different education levels.")

# Bubble Plot: Correlation between Illiteracy and School Dropout Rates
st.title("Bubble Plot: Correlation between Illiteracy and School Dropout Rates")
bubble_size = st.slider('Select Bubble Size', min_value=5, max_value=20, value=8)
bubble_opacity = st.slider('Select Bubble Opacity', min_value=0.1, max_value=1.0, value=0.5)

# Create the bubble chart
fig = go.Figure(data=[go.Scatter(
    x=df['PercentageofEducationlevelofresidents-illeterate'],
    y=df['PercentageofSchooldropout'],
    mode='markers',
    marker=dict(size=bubble_size, opacity=bubble_opacity, color='red'),
    text=df['refArea']
)])

# Update layout
fig.update_layout(
    title="Bubble Chart: Correlation between Illiteracy and School Dropout Rates",
    xaxis_title="Percentage of Illiterate Residents",
    yaxis_title="Percentage of School Dropouts",
)

# Display the plot using Streamlit
st.plotly_chart(fig)
st.write("The bubble chart shows that the relationship between illiteracy and school dropout rates is not immediately apparent, suggesting that no clear correlation is evident from the data.")

# Pie Chart: Education Level Proportions Across Districts
st.title("Pie Chart: Education Level Proportions Across Districts")

# Filter and group the data for pie charts
district_data = df[df['refArea'].str.contains('District')].groupby('refArea').agg(
    {'PercentageofSchooldropout': 'mean',
     'PercentageofEducationlevelofresidents-illeterate': 'mean'}
).reset_index()

# Interactive Checkbox to filter certain districts
hide_districts = st.multiselect("Hide Districts", options=district_data['refArea'].unique(), default=[])

# Filter data based on districts to hide
filtered_data = district_data[~district_data['refArea'].isin(hide_districts)]

# Slider to filter based on School Dropout percentage
min_dropout, max_dropout = st.slider(
    "Filter Districts by School Dropout Percentage:",
    min_value=float(filtered_data['PercentageofSchooldropout'].min()),
    max_value=float(filtered_data['PercentageofSchooldropout'].max()),
    value=(float(filtered_data['PercentageofSchooldropout'].min()), float(filtered_data['PercentageofSchooldropout'].max()))
)

# Apply the filter
filtered_data = filtered_data[
    (filtered_data['PercentageofSchooldropout'] >= min_dropout) &
    (filtered_data['PercentageofSchooldropout'] <= max_dropout)
]

# Dropdown for selecting a district to highlight
selected_district = st.selectbox("Select a District to Highlight", options=filtered_data['refArea'].unique())

# Define custom explode values for each district
explode_values = [0.1 if x == selected_district else 0.0 for x in filtered_data['refArea']]

# Define custom colors
custom_colors = ['orange', 'cyan', 'brown', 'grey', 'indigo', 'beige']

# Filter the data to get the highlighted district's information
highlight_data = filtered_data[filtered_data['refArea'] == selected_district]

# Pie chart for school dropout rates
fig_dropout = go.Figure(data=[go.Pie(
    labels=filtered_data['refArea'],
    values=filtered_data['PercentageofSchooldropout'],
    title="School Dropout Rates Across Districts",
    pull=explode_values,  # This mimics the explode effect in Plotly
    marker=dict(
        colors=custom_colors,  # Custom colors
        line=dict(color='green', width=1)  # Wedge properties
    ),
    hoverinfo='label+percent+value',  # Display detailed hover info
    sort=True
)])

# Pie chart for illiteracy
fig_illeterate = go.Figure(data=[go.Pie(
    labels=filtered_data['refArea'],
    values=filtered_data['PercentageofEducationlevelofresidents-illeterate'],
    title="Proportion of Illiteracy Across Districts",
    pull=explode_values,  # Explode selected district
    marker=dict(
        colors=custom_colors,  # Custom colors
        line=dict(color='green', width=1)  # Wedge properties
    ),
    hoverinfo='label+percent+value',  # Display detailed hover info
    sort=False
)])

# Display the pie charts in Streamlit
st.subheader("School Dropout Rates")
st.plotly_chart(fig_dropout)

st.subheader("Illiteracy Proportion")
st.plotly_chart(fig_illeterate)

# Display additional information based on the selected district
st.write(f"You have selected: **{selected_district}**. The average dropout rate is **{highlight_data['PercentageofSchooldropout'].values[0]:.2f}%**, and the illiteracy rate is **{highlight_data['PercentageofEducationlevelofresidents-illeterate'].values[0]:.2f}%**.")
