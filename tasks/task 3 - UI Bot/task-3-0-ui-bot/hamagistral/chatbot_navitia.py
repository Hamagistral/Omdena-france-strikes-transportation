from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from googletrans import Translator
from navitia_client import Client
from dotenv import load_dotenv
from datetime import datetime

import streamlit as st
import pandas as pd
import numpy as np
import requests
import folium
import random
import time
import ast
import os

import unidecode

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')

NAVITIA_USER = os.getenv('NAVITIA_USER')

translator = Translator()

# Helper functions
def convert_duration(seconds):
    min, sec = divmod(seconds, 60)
    hour, min = divmod(min, 60)
    return '%d:%02d:%02d' % (hour, min, sec)

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculates the distance between two sets of latitude and longitude coordinates.
    """

    return geodesic((lat1, lon1), (lat2, lon2)).kilometers

# Translation service
@st.cache_resource(show_spinner=False)
def translate(text, language_code):
    """Translate text from one language to another"""

    if language_code == "en":
        return text
    
    translator = Translator(service_urls=['translate.google.com'])
    translation = translator.translate(text, dest=language_code)

    return translation.text

@st.cache_resource
def generate_response(prompt):
    """
    Generates a response message for the strike situation in Paris and offers assistance in finding alternative transportation.
    """

    chatbot_response = random.choice([f"""🚧 It seems like there's a strikes currently in Paris. Public transport may be disturbed in your way to {prompt}. 
    🗺️ We will give you alternative transportation. Please enter your current location and destination! We will help you find the nearest alternative transportation.""",
    f"""⚠️ Attention! There are disruptions in the public transportation system that could impact your journey to {prompt}.  
    🤖 Don't worry, we're here to help. Please provide your current location and destination, and we'll suggest alternative routes for you.""", f"""🚦 Traffic congestion is high around {prompt}, making it difficult to rely on private transportation. Don't worry, we've got your back! Share your current location and destination, and we'll find the most convenient alternative public 
    transportation options for you.""", f"""🚧 Attention, there are road closures and diversions due to strikes are affecting the regular routes near {prompt}. 
    🤖 Don't worry, we're here to assist you! Just provide us with your current location and desired destination, and we'll suggest alternative transportation modes."""])
    
    return chatbot_response


@st.cache_resource(show_spinner=False)
def get_navitia_journey(departure, destination, traveler_type, commercial_mode):
    """
    This function gets the directions from a starting and destination position in (latitude, longitude) format and the traveler type (walking, bike, wheelchair...)
    and preffered commercial mode (bus, metro...) and return a json response containing the coordinates of the directions to take, trip length in meters, trip duration in seconds etc...
    """

    client = Client(user=NAVITIA_USER)

    client.set_region("fr-idf")

    raw_url = f'coverage/fr-idf/journeys?from={departure}&to={destination}&traveler_type={traveler_type}&allowed_id%5B%5D=commercial_mode%3A{commercial_mode}&max_nb_journeys=3&'
    response = client.raw(url=raw_url)

    response = response.json()

    try:
        # Extract routes and schedules
        journeys = response['journeys']

        # Get best journey route
        for i, journey in enumerate(journeys):
            if journey['status'] == '':
                if commercial_mode == '':
                    best_route = journey
                    break
                else:
                    for j in range(0, len(journey['sections'])):
                        mode = journey['sections'][j].get('display_informations', '')
                        if 'physical_mode' in mode:
                            mode = mode.get('physical_mode')
                            mode = unidecode.unidecode(mode).lower()
                            if mode == commercial_mode.lower():
                                best_route = journey
                                break
        
        return best_route
    except: 
        return response

@st.cache_resource(show_spinner=False)
def journey_summary(best_route, trp_mean, trp_mode):
    """
    This function gets journey summery from the best_route json
    """

    try:
        departure_time = best_route['departure_date_time']

        datetime_obj = datetime.strptime(departure_time, '%Y%m%dT%H%M%S')
        formatted_time_dep = datetime_obj.strftime('%H:%M:%S')

        arrival_time = best_route['arrival_date_time']

        datetime_obj = datetime.strptime(arrival_time, '%Y%m%dT%H%M%S')
        formatted_time_arr = datetime_obj.strftime('%H:%M:%S')

        durations = []
        for i, transportation in enumerate(best_route['durations']):
            if best_route['durations'][transportation] > 0:
                durations.append({transportation: convert_duration(best_route['durations'][transportation])})

        distances = []
        for i, transportation in enumerate(best_route['distances']):
            if best_route['distances'][transportation] > 0:
                distances.append({transportation: best_route['distances'][transportation]})

        start = best_route['sections'][0]['from']['address']['label']
        start_coordinates = best_route['sections'][0]['from']['address']['coord']

        dest = best_route['sections'][len(best_route['sections']) - 1]['to']['address']['label']
        dest_coordinates = best_route['sections'][len(best_route['sections']) - 1]['to']['address']['coord']
        
        total_duration = durations[0]['total']

        time_components = total_duration.split(':')
        hours = int(time_components[0])
        minutes = int(time_components[1])
        seconds = int(time_components[2])

        if hours == 0:
            if minutes == 0:
                total_duration = f"{seconds} seconds"
            else:
                total_duration = f"{minutes} minutes"
        else:
            total_duration = total_duration

        distance_string = ', '.join([f"{list(d.keys())[0].capitalize()}: {list(d.values())[0]}m" for d in distances])

        journey_summary = random.choice([f"""
                Here's the best route journey we found for you using your current transportation mode (**{trp_mean}**) and your preffered transportation (**{trp_mode}**):  
                
                🛎️ **Departure** at **{formatted_time_dep}** from **{start}**  
                🧳 **Arrival** in **{formatted_time_arr}** to **{dest}**  
                🕖 **Total duration** of the trip **{total_duration}**   
                🛸 **Distances** {distance_string}""", f"""
                We have discovered the optimal route for you based on your chosen transportation mode (**{trp_mean}**) and preferred means of travel (**{trp_mode}**). 
                Your journey details are as follows:  

                🛎️ **Departure**: **{formatted_time_dep}** from **{start}**  
                🧳 **Arrival**: **{formatted_time_arr}** at **{dest}**  
                🕖 **Total duration**: **{total_duration}**  
                🛸 **Distance**: {distance_string}""", f"""
                Based on your chosen transportation mode (**{trp_mean}**) and preferred means of travel (**{trp_mode}**), we have identified the best route for your journey. Here are the specifics:

                🛎️ **Departure**: **{formatted_time_dep}** from **{start}**  
                🧳 **Arrival**: **{formatted_time_arr}** at **{dest}**  
                🕖 **Total duration**: **{total_duration}**  
                🛸 **Distances**: {distance_string}""", f"""
                Taking into account your current transportation mode (**{trp_mean}**) and your preferred means of travel (**{trp_mode}**), we have curated the ideal journey for you. Here are the key details:
                
                🛎️ **Departure**: **{formatted_time_dep}** from **{start}**  
                🧳 **Arrival**: **{formatted_time_arr}** at **{dest}**  
                🕖 **Total duration**: **{total_duration}**  
                🛸 **Distances**: {distance_string}"""])

        st.success(journey_summary)
    except:
        st.error("❌ Sorry there's no route found for you ! Please choose other types of transportation. 🛵")


@st.cache_resource(show_spinner=False)
def get_journey_steps(best_route, commercial_mode):
    """
    This function gets journey steps for each sections (step) from the best_route json
    """
    try:
        journey_info = []

        for i, section in enumerate(best_route['sections']):
            try:
                from_label = section['from'].get('address', {}).get('label') or section['from'].get('stop_point', {}).get('label') or section['from'].get('poi', {}).get('label') or ''
                to_label = section['to'].get('address', {}).get('label') or section['to'].get('stop_point', {}).get('label') or section['to'].get('poi', {}).get('label') or ''
                via_label = section.get('vias', [{}])[0].get('name', '')

                duration = section.get('duration')
                duration = convert_duration(duration)

                time_components = duration.split(':')
                hours = int(time_components[0])
                minutes = int(time_components[1])
                seconds = int(time_components[2])

                if hours == 0:
                    if minutes == 0:
                        duration = f"{seconds} seconds"
                    else:
                        duration = f"{minutes} minutes"
                else:
                    duration = duration

                step_info = f"**Step {i+1}**. From **{from_label}** to **{to_label}** | ⏱️ **Duration:** {duration}  "

                transport_mode = section.get('display_informations', {}).get('commercial_mode', {}) or ''
                transport_direction = section.get('display_informations', {}).get('direction', {}) or ''
                transport_code = section.get('display_informations', {}).get('code', {}) or ''

                if via_label:
                    step_info += f"via **{via_label}**\n"
                else:
                    step_info += "\n"

                try:
                    stop_datetime = section['stop_date_times'][0].get('departure_date_time') or ''
                    stop_datetime = datetime.strptime(stop_datetime, '%Y%m%dT%H%M%S')
                    stop_datetime = stop_datetime.strftime('%H:%M:%S')

                    step_info += f"🛎️ **Departure Time:** {stop_datetime} | "
                except:
                    pass

                if commercial_mode == "Bus":
                    emoji_trp = "🚍"
                elif commercial_mode == "Metro":
                    emoji_trp = "🚇"
                elif commercial_mode == "RapidTransit":
                    emoji_trp = "🚈"
                elif commercial_mode == "LocalTrain":
                    emoji_trp = "🚆"
                elif commercial_mode == "Tramway":
                    emoji_trp = "🚊"
                else:
                    emoji_trp = "🛸"

                if transport_mode and stop_datetime:
                    step_info += f"{emoji_trp} **{transport_mode}** Line {transport_code} heading to {transport_direction}\n\n"
                else:
                    step_info += "\n"

                journey_info.append(step_info)
            except:
                duration = section.get('duration')
                step_info = f"**Step {i+1}**. ⏳ Wait for **{int(duration / 60)} min**\n\n"

                journey_info.append(step_info)

        st.info('\n'.join(journey_info))
    except:
        st.info("🚧 No journey information available.")

@st.cache_resource
def plot_route_on_map(best_route, _map):
    """
    This function plot the routes for each step (section)
    """

    colors = ['blue', 'red', 'green', 'purple', 'orange', 'darkred', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'gray']

    for i, section in enumerate(best_route['sections']):
        try:
            to_label = section['to'].get('address', {}).get('label') or section['to'].get('stop_point', {}).get('label') or section['to'].get('poi', {}).get('label') or ''

            # Create a polyline from the list of coordinates
            res_coordinates = section['geojson']['coordinates']
            points = [(i[1], i[0]) for i in res_coordinates]

            # Randomly select a color from the set, allowing repetition when colors run out
            color = random.choice(colors)

            # add the lines
            folium.PolyLine(points, weight=5, color=color, opacity=0.8).add_to(_map)
            
            # create optimal zoom
            df = pd.DataFrame(res_coordinates).rename(columns={0: 'Lon', 1: 'Lat'})[['Lat', 'Lon']]
            folium.Marker(df.iloc[-1], icon=folium.Icon(color=color), tooltip=f"🛎️ Destination {i+1}: {to_label}").add_to(_map)

            sw = df[['Lat', 'Lon']].min().values.tolist()
            ne = df[['Lat', 'Lon']].max().values.tolist()

            _map.fit_bounds([sw, ne])

            # Remove the selected color from the list if it is still available
            if color in colors:
                colors.remove(color)
        except:
            pass

    return _map


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


