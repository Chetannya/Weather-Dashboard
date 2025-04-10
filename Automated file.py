import os
import weather_module  # Importing the weather data module


API_KEY = "XXXXXXXXXXXXXXXXXX"
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
