import pandas as pd
import numpy as np
import folium
import requests
import geopy
import json
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

api = 'https://opendata.paris.fr/api/records/1.0/search/?dataset=velib-disponibilite-en-temps-reel&q=&lang=en&facet=name&facet=is_installed&facet=is_renting&facet=is_returning&facet=nom_arrondissement_communes&timezone=Africa%2FNairobi'

# create a function that returns the closest velib station to a given address and plot it on a map
# the function should take the address as an argument and return the name of the closest velib station
# It should return map, distance, name of the closest velib station
# ie
def get_closest_velib_station(address):
    # call the API and parse the response
    response = requests.get(api)
    response_json = response.json()
    # get the coordinates of the address
    geolocator = Nominatim(user_agent="my_app")
    location = geolocator.geocode(address)
    # calculate the distance between the address and the velib stations
    distances = []
    for record in response_json['records']:
        lat = record['geometry']['coordinates'][0]
        lon = record['geometry']['coordinates'][1]
        distance = geodesic((location.latitude, location.longitude), (lat, lon)).km
        distances.append(distance)
    # get the name of the closest velib station
    closest_station_index = np.argmin(distances)
    closest_station_name = response_json['records'][closest_station_index]['fields']['name']
    # plot the velib stations on a map
    m = folium.Map(location=[location.latitude, location.longitude], zoom_start=12)
    folium.Marker([location.latitude, location.longitude], popup=address).add_to(m)
    folium.Marker([response_json['records'][closest_station_index]['geometry']['coordinates'][1], response_json['records'][closest_station_index]['geometry']['coordinates'][0]], popup=closest_station_name).add_to(m)
    return m, distances[closest_station_index], closest_station_name

get_closest_velib_station("175 5th Avenue NYC")