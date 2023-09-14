from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from googletrans import Translator
from dotenv import load_dotenv

import streamlit as st
import pandas as pd
import numpy as np
import requests
import folium
import random
import boto3
import time
import ast
import os

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')

translator = Translator()

# Helper functions
def convert(seconds):
    """
    Converts duration in seconds to Hour:Minute:Seconds format
    """
    return time.strftime("%H:%M:%S", time.gmtime(seconds))

@st.cache_resource(show_spinner=False)
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

@st.cache_data(show_spinner=False)
def load_station_status_data():
    s3 = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    bucket = s3.Bucket(AWS_BUCKET_NAME)
    obj = bucket.Object('ratp_stations_traffic_status.csv')
    body = obj.get()['Body']
    df = pd.read_csv(body)

    return df

def create_route_map(response, map, start_name, station_name, station_type, color):
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
            folium.Marker(point, icon=folium.Icon(color='green'), tooltip=f"{station_type} Station: {station_name}").add_to(map)  # Green marker for destination point

    # add the lines
    folium.PolyLine(points, weight=5, color=color, opacity=0.8).add_to(map)

    # create optimal zoom
    df = pd.DataFrame(res_coordinates).rename(columns={0: 'Lon', 1: 'Lat'})[['Lat', 'Lon']]
    sw = df[['Lat', 'Lon']].min().values.tolist()
    ne = df[['Lat', 'Lon']].max().values.tolist()

    map.fit_bounds([sw, ne])

    return map


def route_station_dest_station(response, map, color):
    """
    This function get the coordinates of the route to take, adds them together in a pandas dataframe and then plots the route line into the map
    """

    res_coordinates = response.json()['features'][0]['geometry']['coordinates']
    points = [(i[1], i[0]) for i in res_coordinates]

    # add the lines
    folium.PolyLine(points, weight=5, color=color, opacity=0.8).add_to(map)

    # create optimal zoom
    df = pd.DataFrame(res_coordinates).rename(columns={0: 'Lon', 1: 'Lat'})[['Lat', 'Lon']]
    sw = df[['Lat', 'Lon']].min().values.tolist()
    ne = df[['Lat', 'Lon']].max().values.tolist()

    map.fit_bounds([sw, ne])

    return map


@st.cache_resource(show_spinner=False)
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



def chatbot_response(response, trp_mean, station_name, station_info, transport_type, transport_type_status):
    """
    This function shoud get the response the get_directions_response() function and output to the user informations about the route he should take, like trip duration and distance
    """

    trip_distance = round(response.json()['features'][0]['properties']['segments'][0]['distance'] / 1000, 2)
    trip_duration = convert(response.json()['features'][0]['properties']['segments'][0]['duration'])

    time_components = trip_duration.split(':')
    hours = int(time_components[0])
    minutes = int(time_components[1])
    seconds = int(time_components[2])

    if hours == 0:
        if minutes == 0:
            trip_duration = f"{seconds} seconds"
        else:
            trip_duration = f"{minutes} minutes"
    else:
        trip_duration = trip_duration

    if station_info in ['RER', 'TRAIN', 'METRO', 'TRAMWAY']:
        res = st.success(f"""
                        🛣️ The route suggested is about **{trip_distance} km** long and it will take you about **{trip_duration}** to arrive to the nearest station with **{trp_mean}**.  
                        
                         
                        🚉 The nearest alternative transportation is the **{station_info}** station **{station_name}**.  
                        🚏 You should take the **{transport_type}** line. 🚦 The traffic status is **{translator.translate(transport_type_status, src='fr', dest='en').text}.**""")
    elif station_info == 'BUS':
        res = st.success(f"""
                        🛣️ The route suggested is about **{trip_distance} km** long and it will take you about **{trip_duration}** to arrive to your destination with **{trp_mean}**.  

                        🚍 The nearest alternative transportation is the **{station_info}** station in **{station_name}**.""")
    else:
        res = st.success(f"""
                        🛣️ The route suggested is about **{trip_distance} km** long and it will take you about **{trip_duration}** to arrive to your destination with **{trp_mean}**.  

                        🚲 There's **{station_info} bikes** left in the **{station_name}** **Velib** station.""")
        
    return res

def generate_response(prompt):
    """
    Generates a response message for the strike situation in Paris and offers assistance in finding alternative transportation.
    """

    chatbot_response = random.choice([f"""🚧 It seems like there's a strikes currently in Paris. Public transport may be disturbed in your way to {prompt}. 
    🗺️ We will give you alternative transportation. Please enter your current location and destination! We will help you find the nearest alternative transportation.""",
    f"""⚠️ Attention! There are disruptions in the public transportation system that could impact your journey to {prompt}.  
    🤖 Don't worry, we're here to help. Please provide your current location and destination, and we'll suggest alternative routes for you.""", f"""🚦 Traffic congestion is high around {prompt}, making it difficult to rely on private transportation. Don't worry, we've got your back! Share your current location and destination, and we'll find the most convenient alternative public 
    transportation options for you.""", f"""🚧 Attention, there are road closures and diversions affecting the regular routes near {prompt}. 
    🤖 Don't worry, we're here to assist you! Just provide us with your current location and desired destination, and we'll suggest alternative transportation modes."""])
    
    return chatbot_response


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculates the distance between two sets of latitude and longitude coordinates.
    """

    return geodesic((lat1, lon1), (lat2, lon2)).kilometers

@st.cache_resource(show_spinner=False)
def find_nearest_velib_station(start_lat, start_long, dest_lat, dest_long):
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

    # Create a column with the distance between each station and the destination GPS coordinates
    station_information['distance_from_destination'] = station_information.apply(
        lambda row: calculate_distance(dest_lat, dest_long, row['lat'], row['lon']),
        axis=1
    )

    # Merge station information and status based on station_id
    merged_station_data = pd.merge(station_information, station_status, on='station_id')

    # Sort stations by destination distance in ascending order
    sorted_dest_stations = merged_station_data.sort_values(by='distance_from_destination')

    # Get closest destination station
    closest_dest_station_name = sorted_dest_stations.iloc[0]['name']
    closest_dest_station_coords = (sorted_dest_stations.iloc[0]['lat'], sorted_dest_stations.iloc[0]['lon'])

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

    # Return the nearest station & closest destination station coordinates, name, and num_bikes_available
    return nearest_station_coords, closest_dest_station_coords, closest_dest_station_name, nearest_station_name, nearest_station_bikes_available

@st.cache_resource(show_spinner=False)
def find_nearest_ratp_station(start_lat, start_long, dest_lat, dest_long, station_type):
    """
    Finds the nearest station with a type RER, TRAIN, METRO, TRAMWAY or VAL to the given GPS coordinates
    """

    # Get station information
    stations = pd.read_csv("data/transport_stations_paris.csv")
    stations_status = load_station_status_data()
    
    # Merge the filtered stations with the stations_status dataframe based on the "name" and "transport_type" columns
    stations_infos = pd.merge(stations, stations_status, left_on='transport_type', right_on='name', how='left')
    stations_infos = stations_infos.drop(columns='name')


    # Converts the station_coordinates from type object to type list
    stations_infos['station_coordinates'] = stations_infos['station_coordinates'].apply(ast.literal_eval)

    # Create a column with the distance between each station and the input GPS coordinates
    stations_infos['distance_from_input'] = stations_infos.apply(
        lambda row: calculate_distance(start_lat, start_long, row['station_coordinates'][0], row['station_coordinates'][1]),
        axis=1
    )

    # Create a column with the distance between each station and the destination GPS coordinates
    stations_infos['distance_from_destination'] = stations_infos.apply(
        lambda row: calculate_distance(dest_lat, dest_long, row['station_coordinates'][0], row['station_coordinates'][1]),
        axis=1
    )

    # Calculate distance from the input to the destination
    distance_input_destination = calculate_distance(start_lat, start_long, dest_lat, dest_long)

    # Filter stations with station_type 
    filtered_stations = stations_infos[stations_infos['station_type'] == station_type]

    if filtered_stations.empty:
        return "No station found."

    # Sort stations by destination distance in ascending order
    sorted_dest_stations = filtered_stations.sort_values(by='distance_from_destination')

    # Step 1: Get 10 closest stations to the destination
    closest_dest_stations = sorted_dest_stations.head(10)

    # Step 2: Check if the transport_type of the closest stations have "traffic normal"
    closest_dest_station = None
    for _, station in closest_dest_stations.iterrows():
        if 'trafic normal' in station['status']:
            closest_dest_station = station
            break  # Exit the loop once the row is found

    if closest_dest_station is None:
        return "No station with normal traffic found."
    
    closest_dest_station_coords = (closest_dest_station['station_coordinates'][0], closest_dest_station['station_coordinates'][1])
    closest_dest_station_name = closest_dest_station['station_name']
    
    # Sort filtered stations by input distance in ascending order
    sorted_input_stations = filtered_stations.sort_values(by='distance_from_input')

    # Step 3: Filter stations by station_type and transport_type of the closest_dest_station
    filtered_stations = sorted_input_stations[sorted_input_stations['transport_type'] == closest_dest_station['transport_type']]

    if filtered_stations.empty:
        return "No station found with the specified transport type."

    # Retrieve the nearest station coordinates, name, and type
    nearest_station = filtered_stations.iloc[0]
    nearest_station_coords = (nearest_station['station_coordinates'][0], nearest_station['station_coordinates'][1])
    nearest_station_name = nearest_station['station_name']
    nearest_station_type = nearest_station['station_type']

    transport_type = nearest_station['transport_type']
    transport_type_status = nearest_station['status']

    # Return the nearest station & closest destination station coordinates, name, and type (train, metro, tramway etc...)
    return nearest_station_coords, closest_dest_station_coords, closest_dest_station_name, nearest_station_name, nearest_station_type, transport_type, transport_type_status

@st.cache_resource(show_spinner=False)
def find_nearest_bus_station(start_lat, start_long, dest_lat, dest_long):
    """
    Finds the nearest bus station to the given GPS coordinates
    """

    # Get station information
    bus_stations = pd.read_csv("data/bus_stations.csv")

    # Converts the station_coordinates from type object to type list
    bus_stations['station_coordinates'] = bus_stations['station_coordinates'].apply(ast.literal_eval)

    # Create a column with the distance between each station and the input GPS coordinates
    bus_stations['distance_from_input'] = bus_stations.apply(
        lambda row: calculate_distance(start_lat, start_long, row['station_coordinates'][0], row['station_coordinates'][1]),
        axis=1
    )

    # Create a column with the distance between each station and the destination GPS coordinates
    bus_stations['distance_from_destination'] = bus_stations.apply(
        lambda row: calculate_distance(dest_lat, dest_long, row['station_coordinates'][0], row['station_coordinates'][1]),
        axis=1
    )

    # Sort stations by destination distance in ascending order
    sorted_dest_stations = bus_stations.sort_values(by='distance_from_destination')

    # Get the closest stations to the destination
    closest_dest_station = sorted_dest_stations.iloc[0]
    closest_dest_station_coords = (closest_dest_station['station_coordinates'][0], closest_dest_station['station_coordinates'][1])
    closest_dest_station_type = closest_dest_station['station_type_voie']
    closest_dest_station_name = get_area_name(closest_dest_station_coords)

    # Filter stations with station_type 
    filtered_stations = bus_stations[bus_stations['station_type_voie'] == closest_dest_station_type]

    if filtered_stations.empty:
        return "No station found."
    
    # Sort filtered stations by input distance in ascending order
    sorted_input_stations = filtered_stations.sort_values(by='distance_from_input')

    if sorted_input_stations.empty:
        return "No station found with the specified transport type."

    # Retrieve the nearest station coordinates, name, and type
    nearest_station = sorted_input_stations.iloc[0]
    nearest_station_coords = (nearest_station['station_coordinates'][0], nearest_station['station_coordinates'][1])
    nearest_station_type = nearest_station['station_type_voie']
    nearest_station_name = get_area_name(nearest_station_coords)

    # Return the nearest station & closest destianation statio coordinates and type of line 
    return nearest_station_coords, closest_dest_station_coords, closest_dest_station_name, nearest_station_name, nearest_station_type

# Translation service
@st.cache_resource(show_spinner=False)
def translate(text, language_code):
    """Translate text from one language to another"""

    if language_code == "en":
        return text
    
    translator = Translator(service_urls=['translate.google.com'])
    translation = translator.translate(text, dest=language_code)

    return translation.text
