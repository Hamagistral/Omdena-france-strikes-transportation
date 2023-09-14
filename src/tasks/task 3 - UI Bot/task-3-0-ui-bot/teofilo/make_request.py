from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import numpy as np
import requests
from googletrans import Translator
import folium
import ast
import os

load_dotenv()

@st.cache_resource
def get_directions(start_loc, dest_loc, trp_mean):
    """
    This function gets the directions from a starting and destination position in (longitude, latitude) format and the profile (trip mean like car, bike etc)
    and return a json response containing the coordinates of the directions to take, trip length in meters, trip duration in seconds etc...
    """

    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8', 
    }

    api_key = os.getenv('ORS_API_KEY')
    res = requests.get(f'https://api.openrouteservice.org/v2/directions/{trp_mean}?api_key={api_key}&start={start_loc}&end={dest_loc}', headers=headers)

    return res


def create_route_map(response, map, start_name, station_name, station_type):
    """
    This function get the coordinates of the route to take, adds them together in a pandas dataframe and then plots the route line into the map
    """

    res_coordinates = response.json()['features'][0]['geometry']['coordinates']
    points = [(i[1], i[0]) for i in res_coordinates]

    # add marker for the start and ending points
    for i, point in enumerate([points[0], points[-1]]):
        if i == 0:
            folium.Marker(point, icon=folium.Icon(color='blue'), tooltip=f"📍 Current Location: {start_name}").add_to(map)  # Blue marker for starting point
        else:
            folium.Marker(point, icon=folium.Icon(color='green'), tooltip=f"🚉 {station_type} Station: {station_name}").add_to(map)  # Green marker for destination point

    # add the lines
    folium.PolyLine(points, weight=5, opacity=1).add_to(map)

    # create optimal zoom
    df = pd.DataFrame(res_coordinates).rename(columns={0: 'Lon', 1: 'Lat'})[['Lat', 'Lon']]
    sw = df[['Lat', 'Lon']].min().values.tolist()
    ne = df[['Lat', 'Lon']].max().values.tolist()

    map.fit_bounds([sw, ne])

    return map


@st.cache_resource
def get_area_name(loc):
    """
    This function gets the address of a (latitude, longitude) position and returns the name of the area
    """

    geolocator = Nominatim(user_agent="geoapiExercises") 
    location = geolocator.reverse(loc) 

    location_address = location.raw['address']
    
    area_road = location_address.get('road', '')
    area_neighbourhood = location_address.get('neighbourhood', '')
    area_suburb = location_address.get('suburb', '')
    area_postcode = location_address.get('postcode', '')
    
    area_name = ""

    if area_road:
        area_name += area_road + ", "

    if area_neighbourhood:
        area_name += area_neighbourhood + ", "

    if area_suburb:
        area_name += area_suburb + ", "

    if area_postcode:
        area_name += area_postcode

    return area_name


def chatbot_response(response, trp_mean, station_name, station_info):
    """
    This function shoud get the response the get_directions_response() function and output to the user informations about the route he should take, like trip duration and distance
    """

    trip_distance = round(response.json()['features'][0]['properties']['segments'][0]['distance'] / 1000, 2)
    trip_duration = round(response.json()['features'][0]['properties']['segments'][0]['duration'] / 60, 2)

    if trp_mean == "Bike":
        emoji_trp = "🚴‍♂️"
    elif trp_mean == "Car":
        emoji_trp = "🚗"
    elif trp_mean == "Walking":
        emoji_trp = "🚶"
    else:
        emoji_trp = "👨‍🦽"

    if station_info in ['RER', 'TRAIN', 'METRO', 'TRAMWAY', 'VAL']:
        res = st.success(f"""🛣️ The route suggested is about **{trip_distance} km** long and it will take you **{trip_duration} minutes** to arrive to your destination in a {emoji_trp} **{trp_mean}**.
                        The alternative transportation is **{station_name}** a **{station_info}** station.""")
    else:
        res = st.success(f"""🛣️ The route suggested is about **{trip_distance} km** long and it will take you **{trip_duration} minutes** to arrive to your destination in a {emoji_trp} **{trp_mean}**.
                        There's **{station_info} bikes** left in the **{station_name}** **Velib** station.""")
        
    return res


def generate_response(prompt):
    """
    Generates a response message for the strike situation in Paris and offers assistance in finding alternative transportation.
    """

    response = f"""🚧 It seems like there's a strike currently in Paris, people are protesting against the government's retirement policies. Public transport may be disturbed in your way to {prompt}.

            🗺️ We will give you alternative transportation. Please enter your current location and destination! We will help you find the nearest alternative transportation."""
    
    return response


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculates the distance between two sets of latitude and longitude coordinates.
    """

    return geodesic((lat1, lon1), (lat2, lon2)).kilometers

@st.cache_resource
def find_nearest_velib_station(start_lat, start_long):
    """
    Finds the nearest Velib station to the given GPS coordinates with num_bikes_available > 1.
    """
    
    # URL JSON files
    url_station_status = "https://velib-metropole-opendata.smoove.pro/opendata/Velib_Metropole/station_status.json"
    url_station_information = "https://velib-metropole-opendata.smoove.pro/opendata/Velib_Metropole/station_information.json"

    # Get station information
    response_info = requests.get(url_station_information)
    data_info = response_info.json()

    # Create DataFrame from JSON
    station_information = pd.DataFrame(data_info["data"]["stations"])

    # Get station status
    response_status = requests.get(url_station_status)
    data_status = response_status.json()

    # Create DataFrame from JSON
    station_status = pd.DataFrame(data_status["data"]["stations"])

    # Create a column with the distance between each station and the input GPS coordinates
    station_information['distance_from_input'] = station_information.apply(
        lambda row: calculate_distance(start_lat, start_long, row['lat'], row['lon']),
        axis=1
    )

    # Merge station information and status based on station_id
    merged_station_data = pd.merge(station_information, station_status, on='station_id')

    # Filter stations with num_bikes_available > 1
    filtered_stations = merged_station_data[merged_station_data['num_bikes_available'] > 1]

    if filtered_stations.empty:
        return None

    # Sort stations by distance in ascending order
    sorted_stations = filtered_stations.sort_values(by='distance_from_input')

    # Retrieve the nearest station coordinates, name, and num_bikes_available
    nearest_station_coords = (sorted_stations.iloc[0]['lat'], sorted_stations.iloc[0]['lon'])
    nearest_station_name = sorted_stations.iloc[0]['name']
    nearest_station_bikes_available = sorted_stations.iloc[0]['num_bikes_available']

    # Return the nearest station coordinates, name, and num_bikes_available
    return nearest_station_coords, nearest_station_name, nearest_station_bikes_available

@st.cache_resource
def find_nearest_train_rer_station(start_lat, start_long, station_type):
    """
    Finds the nearest station with a type RER, TRAIN, METRO, TRAMWAY or VAL to the given GPS coordinates
    """

    # Get station information
    stations = pd.read_csv("data/transport_stations_paris.csv")
    
    # Converts the station_coordinates from type object to type list
    stations['station_coordinates'] = stations['station_coordinates'].apply(ast.literal_eval)

    # Create a column with the distance between each station and the input GPS coordinates
    stations['distance_from_input'] = stations.apply(
        lambda row: calculate_distance(start_lat, start_long, row['station_coordinates'][0], row['station_coordinates'][1]),
        axis=1
    )

    # Filter stations with station_type 
    filtered_stations = stations[stations['station_type'] == station_type]

    if filtered_stations.empty:
        return "No station found."

    # Sort stations by distance in ascending order
    sorted_stations = filtered_stations.sort_values(by='distance_from_input')

    # Retrieve the nearest station coordinates, name, and type
    nearest_station_coords = (sorted_stations.iloc[0]['station_coordinates'][0], sorted_stations.iloc[0]['station_coordinates'][1])
    nearest_station_name = sorted_stations.iloc[0]['station_name']
    nearest_station_type = sorted_stations.iloc[0]['station_type']

    # Return the nearest station coordinates, name, and type (train, metro, tramway etc...)
    return nearest_station_coords, nearest_station_name, nearest_station_type

# Translation service
def translate_code(text, language_code):
    """Translate text from one language to another"""
    translator = Translator(service_urls=['translate.google.com'])
    translation = translator.translate(text, dest=language_code)
    return translation.text

# Language options
def language_options():
    options = {
        "English": "en",
        "French": "fr",
        "Spanish": "es"
    }
    return options