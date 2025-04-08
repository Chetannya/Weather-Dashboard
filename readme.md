# 🌦️ Weather Data Dashboard & Collector

An end-to-end project to automatically collect, update, and visualize daily weather data using the Visual Crossing Weather API. Ideal for analyzing trends over time, city-wise.

---

## 📂 Project Structure
<pre>   
  ├── Weather_Data/   
     └── ... City_Name/   
     └── ... City_Name_YYYY-MM.csv ← Month-wise weather data 
  ├── weather_module.py ← Handles fetching & updating data 
  ├── Automated file.py ← Automates update for all cities 
  ├── Dashboard.py ← Dash dashboard for visualization 
</pre>



---

##  How It Works

###  1. Data Collection (`weather_module.py`)
- Connects to Visual Crossing API.
- Checks last date in each city's CSV.
- Downloads missing weather data from that date till yesterday.
- Saves it in a city-wise, month-wise format.

  '''
  ###Modules to import
  import os
import requests
import pandas as pd
import csv
import numpy as np
import urllib.request
import sys
import codecs
from datetime import datetime, timedelta

# Function to fetch and process data
def fetch_weather_data(city, start_date, end_date, api_key):
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}/{start_date}/{end_date}?unitGroup=metric&include=hours&key={api_key}&contentType=csv"
    
    try:
        ResultBytes = urllib.request.urlopen(url)
        CSVText = csv.reader(codecs.iterdecode(ResultBytes, 'utf-8'))
        data = list(CSVText)
    except urllib.error.HTTPError as e:
        print(f"Error fetching data: {e.code}", e.read().decode())
        sys.exit()
    except urllib.error.URLError as e:
        print(f"Network error: {e.reason}")
        sys.exit()
    
    # Extract headers and rows
    headers = data[0]
    rows = data[1:]
    
    # Convert to DataFrame
    print("Headers:", headers)
    print("Sample Row:", rows[0] if rows else "No Data")

    df = pd.DataFrame(rows, columns=headers)
    
    # Select required columns
    df = df[['datetime', 'temp', 'feelslike', 'precip', 'humidity', 'sealevelpressure', 'dew', 'uvindex', 'solarenergy', 'visibility', 'windspeed', 'winddir', 'conditions', 'icon']]
    
    # Convert datetime to proper format and filter 3-hour intervals
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df[df['datetime'].dt.hour % 3 == 0]  # Keep only 3-hour interval data
    
    return df

# Function to check last recorded date and fetch missing data
def update_existing_data(city, api_key):
    city_folder = f"Weather_Data/{city.replace(' ', '_')}"
    today = datetime.today()
    current_date = (today - timedelta(days=1)).strftime('%Y-%m-%d')  # yesterday
    month = today.strftime('%Y-%m')
    filename = f"{city_folder}/{city}_{month}.csv"
    
    if not os.path.exists(city_folder):
        os.makedirs(city_folder)
        start_date = f"{month}-01"
        new_data = fetch_weather_data(city, start_date, current_date, api_key)
        new_data.to_csv(filename, index=False)
        print(f"New city folder and data file created: {filename}")
    else:
        if os.path.exists(filename):
            existing_df = pd.read_csv(filename)
            existing_df['datetime'] = pd.to_datetime(existing_df['datetime'])
            last_recorded_date = existing_df['datetime'].max().strftime('%Y-%m-%d')
            
            if last_recorded_date < current_date:
                new_data = fetch_weather_data(city, last_recorded_date, current_date, api_key)
                updated_df = pd.concat([existing_df, new_data])
                updated_df['datetime'] = pd.to_datetime(updated_df['datetime'])
                updated_df = updated_df.drop_duplicates(subset='datetime').reset_index(drop=True)
                updated_df.to_csv(filename, index=False)
                print(f"Data updated: {filename}")
            else:
                print("No new data to update.")
        else:
            start_date = f"{month}-01"
            new_data = fetch_weather_data(city, start_date, current_date, api_key)
            new_data.to_csv(filename, index=False)
            print(f"New data file created: {filename}")


# Main execution
if __name__ == "__main__":
    API_KEY = "9EEDESZ5UR6AYN6RQ3MDNXTHW"  # Updated API key
    CITY = "Puttaparthi"
    update_existing_data(CITY, API_KEY)

  '''

###  2. Automation Script (`Automated file.py`)
- Detects all folders (cities) inside `Weather_Data/`.
- Automatically updates weather data for each city.
- Run it daily to keep your dataset current.

  '''
  import os
import weather_module  # Importing the weather data module
from datetime import datetime

API_KEY = "9EEDESZ5UR6AYN6RQ3MDNXTHW"
CITIES_FOLDER = r"C:\Users\AVITA\Documents\Chetannya\SEM 2 @ WA\Weather_Data"

# Function to get cities from existing folders
def get_cities_from_folders():
    if not os.path.exists(CITIES_FOLDER):
        os.makedirs(CITIES_FOLDER)  # Create the folder if it doesn't exist
        return []
    
    return [folder.replace('_', ' ') for folder in os.listdir(CITIES_FOLDER) if os.path.isdir(os.path.join(CITIES_FOLDER, folder))]

# Function to update weather data for all cities
def update_all_cities():
    cities = get_cities_from_folders()
    
    if not cities:
        print("No cities found. Add a city folder to start collecting data.")
        return
    
    print(f"Updating weather data for {len(cities)} cities...")
    for city in cities:
        print(f"Updating: {city}")
        weather_module.update_existing_data(city, API_KEY)
    
    print("All cities updated successfully.")

if __name__ == "__main__":
    update_all_cities()

  '''

###  3. Interactive Dashboard (`Dashboard.py`)
- Built with Plotly Dash.
- Visualizes temperature, humidity, pressure, and more.
- Allows:
  - Custom date selection
  - Trend viewing
  - Metric comparisons

'''

"""

"""

import dash
from dash import dcc, html, Input, Output
import pandas as pd
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Define data folder path
DATA_FOLDER = "Weather_Data"

# Initialize Dash app
app = dash.Dash(__name__)

# Get available cities
cities = [c for c in os.listdir(DATA_FOLDER) if os.path.isdir(os.path.join(DATA_FOLDER, c))]

# Layout with grid structure
app.layout = html.Div([
    html.Div([
        # Left Panel: City selection and summary
        html.Div([
            html.H1("Weather Dashboard"),
            html.Div([
                dcc.Dropdown(
                    id='city-dropdown',
                    options=[{'label': c, 'value': c} for c in cities],
                    placeholder="Select a city",
                    style={'width': '100%'}
                ),
                dcc.DatePickerRange(
                    id='date-picker',
                    start_date=datetime.today() - timedelta(days=7),
                    end_date=datetime.today(),
                    style={'width': '100%', 'margin-top': '10px'}
                ),
                dcc.Dropdown(
                    id='metric-dropdown',
                    options=[
                        {'label': 'Temperature', 'value': 'temp'},
                        {'label': 'Humidity', 'value': 'humidity'},
                        {'label': 'Wind Speed', 'value': 'windspeed'},
                        {'label': 'Pressure', 'value': 'sealevelpressure'}
                    ],
                    multi=True,
                    placeholder="Select metrics",
                    style={'width': '100%', 'margin-top': '10px'}
                )
            ], style={'width': '100%', 'padding': '10px', 'background': '#eef', 'border-radius': '100px'}),
            
            # Summary Stats Card
            html.Div(id='summary-card', style={'width': '73%',
                'background': '#f9f9f9', 'border-radius': '10px', 'box-shadow': '2px 2px 10px rgba(0,0,0,0.1)',
                'padding': '10px', 'margin-top': '15px', 'margin-left':'15px'
            }),
            # Toggle Button for Wind & Precipitation Section with Styling
            html.Button("Wind & Precipitation", id='toggle-wind-precip', n_clicks=0, 
                        style={
                            'width': '100%', 'padding': '10px', 'margin-top': '15px',
                            'background-color': '#007bff', 'color': 'white',
                            'border': 'none', 'border-radius': '5px', 
                            'cursor': 'pointer', 'font-size': '16px', 'font-weight': 'bold'
                        })
        ], style={'width': '25%', 'padding': '20px', 'background': '#eef', 'display': 'flex', 'flex-direction': 'column', 'align-items': 'center'}),

        # Right Panel: Graphs with collapsible sections
        html.Div([
            dcc.Graph(id='weather-graph'),
            html.Div(id='wind-precip-section', style={'display': 'none', 'margin-top': '15px'}, children=[
                dcc.Tabs(id='wind-precip-tabs', value='wind', children=[
                    dcc.Tab(label='Wind Speed', value= 'winds'),
                    dcc.Tab(label='Wind Direction', value='windd'),
                    dcc.Tab(label='Precipitation Data', value='precip')
                ]),
                html.Div(id='wind-precip-content')
            ])
        ], style={'width': '73%', 'padding': '20px'})
    ], style={'display': 'flex'})
])

@app.callback(
    [Output('weather-graph', 'figure'), Output('summary-card', 'children')],
    [Input('city-dropdown', 'value'),
     Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date'),
     Input('metric-dropdown', 'value')]
)
def update_graph(city, start_date, end_date, metrics):
    if not city or not metrics:
        return px.line(title="Select a city and at least one metric to display data"), ""
    
    city_folder = os.path.join(DATA_FOLDER, city) 
    all_files = [f for f in os.listdir(city_folder) if f.endswith(".csv")]
    df_list = []
    for file in all_files:
        file_path = os.path.join(city_folder, file)
        df = pd.read_csv(file_path)
        df['datetime'] = pd.to_datetime(df['datetime'])
        df_list.append(df)
    
    df = pd.concat(df_list, ignore_index=True)
    filtered_data = df[(df['datetime'] >= start_date) & (df['datetime'] <= end_date)]
    
    summary_stats = []
    for metric in metrics:
        if metric in df.columns:
            min_val, max_val, avg_val = filtered_data[metric].min(), filtered_data[metric].max(), filtered_data[metric].mean()
            summary_stats.append(html.Div([
                html.H4(metric.capitalize()),
                html.P(f"Min: {min_val:.2f}"),
                html.P(f"Max: {max_val:.2f}"),
                html.P(f"Avg: {avg_val:.2f}")
            ], style={'padding': '10px', 'background': '#fff', 'border-radius': '5px', 'box-shadow': '1px 1px 5px rgba(0,0,0,0.1)'}))
    
    fig = go.Figure()
    colors = ['red', 'blue', 'green', 'orange', 'purple']
    
    primary_metric = metrics[0]
    for i, metric in enumerate(metrics):
        if metric in df.columns:
            fig.add_trace(go.Scatter(
                x=filtered_data['datetime'], 
                y=filtered_data[metric],
                mode='lines+markers',
                line=dict(color=colors[i % len(colors)], width=2),
                marker=dict(size=6, symbol='circle'),
                name=metric.capitalize(),
                yaxis='y1' if metric == primary_metric else 'y2'
            ))
        else:
            fig.add_trace(go.Scatter(x=[], y=[], mode='lines', name=f"{metric} not available"))
    
    fig.update_layout(
        title=f"Weather Data for {city}",
        xaxis_title="Time",
        yaxis=dict(title=f"{primary_metric.capitalize()}", showgrid=True, gridwidth=1, gridcolor="lightgray"),
        yaxis2=dict(title="Other Metrics", overlaying='y', side='right', showgrid=False),
        plot_bgcolor="rgba(245, 245, 250, 0.9)",
        hovermode="x unified",
        legend=dict(x=0, y=1.1, orientation="h", bgcolor="rgba(255,255,255,0.5)")
    )
    
    return fig, summary_stats
@app.callback(
    Output('wind-precip-section', 'style'),
    [Input('toggle-wind-precip', 'n_clicks')]
)
def toggle_wind_precip_section(n_clicks):
    return {'display': 'block' if n_clicks % 2 == 1 else 'none'}

@app.callback(
    Output('wind-precip-content', 'children'),
    [Input('wind-precip-tabs', 'value'),
     Input('city-dropdown', 'value'),
     Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')]
)
def update_wind_precip_tabs(tab, city, start_date, end_date):
    if not city:
        return html.Div("Select a city to view data")
    
    city_folder = os.path.join(DATA_FOLDER, city) 
    all_files = [f for f in os.listdir(city_folder) if f.endswith(".csv")]
    df_list = []
    for file in all_files:
        file_path = os.path.join(city_folder, file)
        df = pd.read_csv(file_path)
        df['datetime'] = pd.to_datetime(df['datetime'])
        df_list.append(df)
    
    df = pd.concat(df_list, ignore_index=True)
    filtered_data = df[(df['datetime'] >= start_date) & (df['datetime'] <= end_date)]
    
    
    if tab == 'windd':
        return dcc.Graph(figure=px.scatter_polar(filtered_data, r='windspeed', theta='winddir', title='Wind Direction'))
    elif tab == 'precip':
        fig = px.bar(filtered_data, x='datetime', y='precip', title='Precipitation')
        if 'precipprob' in filtered_data.columns:
            fig.add_trace(go.Scatter(x=filtered_data['datetime'], y=filtered_data['precipprob'], mode='lines', name='Precip Prob'))
        return dcc.Graph(figure=fig)
    elif tab =='winds' :
       return dcc.Graph(figure=px.line(filtered_data, x='datetime', y='windspeed', title='Wind Speed Over Time'))
       
    
    return html.Div()

if __name__ == '__main__':
    app.run(debug=True)

'''
---

##  Author

**Chetannya** – Physics & Data Science Student 
Drop issues, improvements, or ideas via GitHub!
