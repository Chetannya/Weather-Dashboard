import os
import pandas as pd
import csv
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
