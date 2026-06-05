import os
import pandas as pd
import folium
from folium.plugins import HeatMap
import streamlit as st

def read_data():
    data_folder = "Datas/Raw Datas"
    zearn_df = pd.read_csv(os.path.join(data_folder, 'Zearn - County - Weekly.csv'))
    unemep_df = pd.read_csv(os.path.join(data_folder, 'UI Claims - County - Weekly.csv'))
    job_df = pd.read_csv(os.path.join(data_folder, 'Job Postings - County - Weekly.csv'))
    emp_df = pd.read_csv(os.path.join(data_folder, 'Employment - County - Weekly.csv'))
    spend_df = pd.read_csv(os.path.join(data_folder, 'Affinity - County - Daily.csv'))
    
    loc = pd.read_csv('Datas/us_county_latlng.csv')
    loc = loc.rename(columns={'fips_code':'countyfips'})
    # return all of the dataframes.
    return zearn_df, unemep_df, job_df, emp_df, spend_df, loc


def add_tile_layers(m):
    # Add tile layers
    folium.TileLayer('Stamen Water Color').add_to(m)
    folium.TileLayer('openstreetmap').add_to(m)
    folium.TileLayer('Stamen Terrain').add_to(m)
    folium.TileLayer('Stamen Toner').add_to(m)
    folium.TileLayer('cartodbpositron').add_to(m)
    folium.TileLayer('cartodbdark_matter').add_to(m)
    return m

def prepare_for_map(df, colnames_to_cast, loc, drop_cols=[]):
    # df groupby countyfips last
    qf = df.groupby('countyfips').last()
    
    empty_columns = qf.columns[qf.eq('.').all()]
    empty_columns = list(empty_columns)
    empty_columns.extend(drop_cols)
    # drop col names in drop_cols list.
    qf = qf.drop(empty_columns, axis=1)

    for col in colnames_to_cast:
        qf[col] = qf[col].replace('.', '0').astype(float)

    qf = qf.reset_index()

    if 'initclaims_count_regular' in qf:
        qf['initclaims_count_regular'] = qf['initclaims_count_regular'].str.replace('.','0')
        qf['initclaims_count_regular'] = pd.to_numeric(qf['initclaims_count_regular'], errors='coerce')
    
    qf = pd.merge(qf, loc, on='countyfips')

    return qf

def create_heatmap(map_data, heatmap_columns, loc, drop_cols = []):
    
    map_data = prepare_for_map(map_data, heatmap_columns, loc, drop_cols)

    # Create a map
    m = folium.Map(location=[map_data['lat'].mean(), map_data['lng'].mean()], zoom_start=6)

    # Create a FeatureGroup for the red circles layer
    red_circles = folium.FeatureGroup(name='County Centers')

    # Create a dictionary to store the column data for each county
    county_data = {}
    for column in heatmap_columns:
        county_data[column] = []

    # Add red circles for each data point and store heatmap data
    for index, row in map_data.iterrows():
        tooltip_text = f"County: {row['name']}<br>"
        
        for column in heatmap_columns:
            tooltip_text += f"{column}: {row[column]}<br>"

        tooltip = folium.Tooltip(tooltip_text, sticky=True)

        folium.CircleMarker(
            location=[row['lat'], row['lng']],
            radius=2,
            fill=True,
            fill_color='red',
            color='red',
            fill_opacity=1,
            tooltip=tooltip
        ).add_to(red_circles)

        # Store heatmap data
        for column in heatmap_columns:
            county_data[column].append((row['lat'], row['lng'], row[column]))

    # Add the red circles layer to the map
    m.add_child(red_circles)

    # Create HeatMap layers for each selected column, initially only the first layer is added to the map
    first_layer = None
    for i, column in enumerate(heatmap_columns):
        heatmap = HeatMap(county_data[column], name=f'{column} Heatmap', show=i == 0)

        
        heatmap.add_to(m)  # Set show=False to hide layers by default

    m = add_tile_layers(m)
    # Add layer control to toggle layers
    folium.LayerControl(collapsed=True).add_to(m)
    
    return m

def save_maps(map_list):
    # Create a folder named Datas/ with os.
    if not os.path.exists('Datas/Maps'):
        os.makedirs('Datas/Maps')
    
    for i, map in enumerate(map_list, 1):
        map.save(f"Datas/Maps/page{i}_map.html")

def create_date_index(df):
    # Rename the 'day' column to 'day_endofweek'
    df = df.rename(columns={'day_endofweek': 'day'})
    
    # Create a new datetime column by combining 'year', 'month', and 'day_endofweek'
    df['date_index'] = pd.to_datetime(df[['year', 'month', 'day']])

    # Set the 'date_index' column as the index
    df.set_index('date_index', inplace=True)
    
    # drop index column
    df = df.drop(['index'], axis=1)
    
    return df

def prepare_for_chart(df, colnames_to_cast, loc, drop_cols=[]):
    empty_columns = df.columns[df.eq('.').all()]
    empty_columns = list(empty_columns)
    empty_columns.extend(drop_cols)

    for col in colnames_to_cast:
        if col != 'name' and col in df.columns:
            if df[col].dtype != int:
                # Check if the column is of numeric type (float)
                if df[col].dtype == float:
                    df[col] = df[col].replace('.', '0').astype(float)
                elif df[col].dtype == object:
                    df[col] = df[col].str.replace('.', '0')
                    df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.reset_index()
    df = pd.merge(df, loc, on='countyfips')

    df = create_date_index(df)

    # Only keep 'name' once in the resulting DataFrame
    if 'name' in colnames_to_cast:
        colnames_to_cast.remove('name')

    df = df[['name'] + colnames_to_cast]
    
    return df

def generate_and_save_heatmaps(zearn_df,unemep_df, job_df, emp_df, spend_df, loc):    

    map_5 = create_heatmap(zearn_df,  ['engagement', 'badges', 'break_engagement', 'break_badges'],loc,['imputed_from_cz'])
    map_4 = create_heatmap(unemep_df, ['initclaims_rate_regular'],loc)
    map_3 = create_heatmap(job_df, ['bg_posts', 'bg_posts_jzgrp12'], loc,['bg_posts_jzgrp345'])
    map_2 = create_heatmap(emp_df, ['emp_incq1','emp', 'emp_incq2', 'emp_incq3', 'emp_incmiddle', 'emp_incbelowmed'],loc)
    map_1 = create_heatmap(spend_df, ['spend_all'], loc, ['provisional'])

    map_list = [map_1, map_2, map_3, map_4, map_5]

    save_maps(map_list)

    st.write("Heatmaps generated and saved successfully!")

def prepare_and_save_chart_data(zearn_df,unemep_df, job_df, emp_df, spend_df,loc):
    # Prepare data for charts
    zearn_df_chart = prepare_for_chart(zearn_df, ['name', 'engagement', 'badges', 'break_engagement', 'break_badges'],loc)
    unemep_df_chart = prepare_for_chart(unemep_df, ['name', 'initclaims_rate_regular'],loc)
    job_df_chart = prepare_for_chart(job_df, ['name', 'bg_posts', 'bg_posts_jzgrp12', 'bg_posts_jzgrp345'],loc)
    emp_df_chart = prepare_for_chart(emp_df, ['name', 'emp_incq1', 'emp', 'emp_incq2', 'emp_incq3', 'emp_incmiddle', 'emp_incbelowmed'],loc)
    spend_df_chart = prepare_for_chart(spend_df, ['name', 'spend_all'],loc)

    # Create a folder to save chart data if it doesn't exist
    if not os.path.exists('Datas/Chart Datas'):
        os.makedirs('Datas/Chart Datas')

    # Save the prepared data to CSV files
    zearn_df_chart.to_csv("Datas/Chart Datas/zearn_df_chart.csv")
    unemep_df_chart.to_csv("Datas/Chart Datas/unemep_df_chart.csv")
    job_df_chart.to_csv("Datas/Chart Datas/job_df_chart.csv")
    emp_df_chart.to_csv("Datas/Chart Datas/emp_df_chart.csv")
    spend_df_chart.to_csv("Datas/Chart Datas/spend_df_chart.csv")

    # Print information to the Streamlit app
    st.write("Chart data prepared and saved successfully!")

if __name__ == '__main__':
    loc = pd.read_csv('Datas/us_county_latlng.csv')
    loc = loc.rename(columns={'fips_code':'countyfips'})