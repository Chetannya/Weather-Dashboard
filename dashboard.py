

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
                        }),
            html.Button("Solar Data", id='toggle-solar-cloud', n_clicks=0,
                        style={'width': '100%', 'padding': '10px', 'margin-top': '10px',
                               'background-color': '#20c997', 'color': 'white',
                               'border': 'none', 'border-radius': '5px',
                               'cursor': 'pointer', 'font-size': '16px', 'font-weight': 'bold'})
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
            ]),
            html.Div(id='solar-cloud-section', style={'display': 'none'}, children=[
                dcc.Tabs(id='solar-cloud-tabs', value='solar', children=[
                    dcc.Tab(label='Solar Energy', value='solar'),
                    dcc.Tab(label='Visibility (as Pseudo Cloudiness)', value='visibility')
                ]),
                html.Div(id='solar-cloud-content')
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

@app.callback(
    Output('solar-cloud-section', 'style'),
    [Input('toggle-solar-cloud', 'n_clicks')]
)
def toggle_solar_cloud_section(n_clicks):
    return {'display': 'block' if n_clicks % 2 == 1 else 'none'}

@app.callback(
    Output('solar-cloud-content', 'children'),
    [Input('solar-cloud-tabs', 'value'),
     Input('city-dropdown', 'value'),
     Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')]
)
def update_solar_cloud_tabs(tab, city, start_date, end_date):
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

    if tab == 'solar':
        return dcc.Graph(figure=px.line(filtered_data, x='datetime', y='solarenergy', title='Solar Energy'))
    elif tab == 'visibility':
        filtered_data['pseudo_cloudiness'] = 100 - filtered_data['visibility']
        return dcc.Graph(figure=px.area(filtered_data, x='datetime', y='pseudo_cloudiness', title='Pseudo Cloudiness (100 - Visibility)'))

if __name__ == '__main__':
    app.run(debug=True)
