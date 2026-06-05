import streamlit as st
import pandas as pd 
import plotly.express as px

# Set Streamlit page configuration
st.set_page_config(layout="wide", page_icon="🌍", initial_sidebar_state="collapsed")

# Define the HTML file path for the map
html_file = 'Datas/Maps/page1_map.html'

# Render the map visualization
st.title("**Credit Card Data Map**")

# Provide a detailed explanation with proper formatting
st.markdown(""" **spend_all:**  The 'spend_all' column likely represents the amount of credit/debit card spending in the specified county for the given date. 
            "It reflects the total spending or sales figures for that particular region and may be expressed in currency (e.g., dollars). "
            "The 'spend_all' column provides information on economic activity related to credit/debit card transactions within the county.""")

HtmlFile = open(html_file, 'r', encoding='utf-8')
source_code = HtmlFile.read()
st.components.v1.html(source_code, height=600)
st.write('---')  # Add a separator

# Read Chart Data, Show as time-series chart. 
data = pd.read_csv("Datas/Chart Datas/spend_df_chart.csv")
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