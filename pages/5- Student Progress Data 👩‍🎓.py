import streamlit as st
import pandas as pd 
import plotly.express as px

# Set Streamlit page configuration
st.set_page_config(layout="wide", page_icon="🌍", initial_sidebar_state="collapsed")

# Define the HTML file path for the map
html_file = 'Datas/Maps/page5_map.html'

# Render the map visualization
st.title("**Student Progress Data Map**")

# Provide a detailed explanation with proper formatting
st.markdown("""
- **engagement:** Average level of students using the platform relative to January 6 to February 21, 2020.

- **badges:** Average level of student achievements earned (badges) on the platform relative to January 6 to February 21, 2020.

- **break_engagement:** This appears to be a variant of the 'engagement' feature. It might specifically capture student engagement levels during school breaks or holidays when student behavior on the platform could differ.

- **break_badges:** Similar to 'break_engagement,' 'break_badges' might capture student achievements in the form of badges, specifically during school breaks.

- **imputed_from_cz:** This feature is a binary indicator (e.g., 0 or 1) that suggests whether certain county-level values have been replaced or imputed with data from commuting zones for privacy or data quality reasons.
""")


HtmlFile = open(html_file, 'r', encoding='utf-8')
source_code = HtmlFile.read()
st.components.v1.html(source_code, height=600)
st.write('---')  # Add a separator

# Read Chart Data, Show as time-series chart. 

data = pd.read_csv("Datas/Chart Datas/zearn_df_chart.csv")
# Apply groupby over name sort by date_index 
data = data.groupby(['name']).apply(lambda x: x.sort_values(['date_index'], ascending = True)).reset_index(drop=True)
data.set_index('date_index',inplace=True)

# Sidebar widget to select a county name
selected_county = st.sidebar.selectbox("Select a County Name", data['name'].unique())

# Filter the data based on the selected county name
selected_county_data = data[data['name'] == selected_county]

col_list = list(selected_county_data.columns)
# clean name and date_index from col_list

# Clean 'name' from col_list:
col_list.remove('name')

# Allow the user to select a column for the time series chart
selected_column = st.sidebar.selectbox("Select a Column", col_list)

fig = px.line(selected_county_data, x= selected_county_data.index, y=selected_column, title=f'{(selected_column.title())} for {selected_county}')
#fig = px.line(selected_county_data, x='date_index', y=selected_column, title=f'{(selected_column.title())} for {selected_county}')    
st.plotly_chart(fig, use_container_width=True, theme="streamlit")