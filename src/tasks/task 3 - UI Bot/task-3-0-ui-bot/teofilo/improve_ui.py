from streamlit_extras.colored_header import colored_header
from streamlit_folium import st_folium
from streamlit_chat import message
from folium.plugins import Draw
from googletrans import Translator
import streamlit as st
import folium

from make_request import chatbot_response, generate_response, get_directions, create_route_map, get_area_name, find_nearest_velib_station, find_nearest_train_rer_station
from make_request import translate_code, language_options

# variable of language options
languages = language_options()

# Page layout
st.set_page_config(page_title="Chatbot Ile-De-France Omdena", page_icon='🇫🇷')

# make a language choice
selected_language = st.sidebar.selectbox("Select Language /langue /idioma ", list(languages.keys()))
selected_language_code = languages[selected_language]

# Side bar menu
with st.sidebar:
    st.image("https://omdena.com/wp-content/uploads/2023/05/Strike-image.jpeg")
    st.markdown(translate_code('## 💬 Chatbot for Alternative Transportation During Strikes in France 🤖', selected_language_code))
    st.markdown(translate_code('''
    ---
    ## 🧭 How To Use ?

    1. Choose your current mean of transportation (car, bike, walking...)
    2. Input your current location
    3. Input your desired destination
    4. Get a direction to the nearest alternative transportation that can bring you to your destination

    ---
    ''', selected_language_code))
    
# Layout of input/response containers
input_container = st.container()
colored_header(label='', description='', color_name='blue-30')
response_container = st.container()

def get_text():
    question = st.text_input(translate_code("You :", selected_language_code), "Stade de France", key="input")
    return question

# Initialization of the chat prompts
if 'generated' not in st.session_state:
    st.session_state['generated'] = [translate_code("👋🏻 Hello! I am Paris TransportChat, where are you trying to go ?", selected_language_code)]

if 'past' not in st.session_state:
    st.session_state['past'] = [translate_code("Hi !", selected_language_code)]

with input_container:
    st.markdown(translate_code("### 🚘 Île-De-France Alternative Transportation Chatbot 🚍", selected_language_code))

    user_input = get_text()
    send_btn = st.button(translate_code("Send", selected_language_code))

colored_header(label='', description='', color_name='red-40')

## Conditional display of AI generated responses as a function of user provided prompts
with response_container:
    if send_btn and user_input:
        response = generate_response(user_input)
        st.session_state.past.append(user_input)
        st.session_state.generated.append(response)
            
    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])-1, -1, -1):
            message(st.session_state["generated"][i], key=str(i), avatar_style="bottts-neutral", seed=90)
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user', avatar_style="avataaars-neutral", seed=10)    
        
# Select Transportation Mean to the Station
transport_options = {
    "Car 🚘 ": 'driving-car',
    "Bike 🚲 ": 'cycling-road',
    "Walking 🚶‍♂️": 'foot-walking',
    "Wheelchair 🦽 ": 'wheelchair'
}

transport_mean_option = st.radio(translate_code("🚘 Please provide your current mean of transportation:", selected_language_code), list(transport_options.keys()), horizontal=True)
transport_mean_value = transport_options[transport_mean_option]

# Select Station Type 
station_options = {
    "Velib 🚲": 'VELIB',
    "Rer": 'RER',
    "Train 🚆": 'TRAIN',
    "Metro 🚇": 'METRO',
    "Tramway 🚊": 'TRAMWAY',
    "Val": 'VAL'
}

station_type_option = st.radio(translate_code("🚉 Please provide the station type:", selected_language_code), list(station_options.keys()), horizontal=True)
station_type_value = station_options[station_type_option]

# Current location & destination maps
st.markdown(translate_code("#### 📍 Please provide your current and destination location :", selected_language_code))
    
# Input Map (Starting & Destination Location)
m_input  = folium.Map(location=[48.866667, 2.333333], zoom_start=10, min_zoom=8)

# Add Location Marker
Draw(draw_options={
        'polyline': False, 'rectangle': False, 
        'circle': False, 'polygon': False,
        'circlemarker': False
    }, edit_options={'edit': False}).add_to(m_input)

input_map = st_folium(m_input, width=700, height=350, key='1')

# Check if there's atleast one marker and markers are not more than 2
if input_map['last_active_drawing'] and len(input_map['all_drawings']) >= 2:

    all_drawings = input_map['all_drawings']

    if len(all_drawings) > 2:
        st.warning(translate_code("⚠️ Please select only one current location and one destination.", selected_language_code))
        all_drawings = all_drawings[:2]

    else:
        longitude_startloc = input_map['all_drawings'][0]['geometry']['coordinates'][0]
        latitude_startloc = input_map['all_drawings'][0]['geometry']['coordinates'][1]

        # Create a marker for the user-inputted location
        start_loc = (latitude_startloc, longitude_startloc)

        longitude_destloc = input_map['all_drawings'][1]['geometry']['coordinates'][0]
        latitude_destloc = input_map['all_drawings'][1]['geometry']['coordinates'][1]

        # Create a red marker for the user-inputted location
        dest_loc = (latitude_destloc, longitude_destloc)

        if start_loc and dest_loc:
            start_loc_name = get_area_name(start_loc)
            dest_loc_name = get_area_name(dest_loc)

            st.info(translate_code(f"🧳 **Current Location** : {start_loc_name} *(Latitude : {latitude_startloc}, Longitude : {longitude_startloc})*", selected_language_code))
            st.info(translate_code(f"🛎️ **Destination Location** : {dest_loc_name} *(Latitude : {latitude_destloc}, Longitude : {longitude_destloc})*", selected_language_code))

            st.markdown(translate_code("#### 🗺️ Here's the route to the nearest transportation station:", selected_language_code))
                    
            m_route = folium.Map(location=[48.866667, 2.333333], zoom_start=10)
            Draw(draw_options={
                        'polyline': False, 'rectangle': False, 
                        'circle': False, 'polygon': False,
                        'circlemarker': False
                    }, edit_options={'edit': False}).add_to(m_route)

            route_start_loc = f'{longitude_startloc}, {latitude_startloc}'
            route_dest_loc = f'{longitude_destloc}, {latitude_destloc}'

            if station_type_value == "VELIB":
                nearest_station, station_name, num_bikes_available = find_nearest_velib_station(latitude_startloc, longitude_startloc)
            else:
                nearest_station, station_name, station_type = find_nearest_train_rer_station(latitude_startloc, longitude_startloc, station_type_value)
                
            lat_stationloc = nearest_station[0]
            long_stationloc = nearest_station[1]
            
            route_station_loc = f'{long_stationloc}, {lat_stationloc}'

            response = get_directions(route_start_loc, route_station_loc, transport_mean_value)

            create_route_map(response, m_route, start_loc_name, station_name, station_type_option)

            folium.Marker(dest_loc, icon=folium.Icon(color='red'), tooltip=f"🛎️ Destination: {dest_loc_name}").add_to(m_route)

            route_map = st_folium(m_route, width=700, height=350, key='2')

            if station_type_value == "VELIB":
                chatbot_response(response, transport_mean_option, station_name, num_bikes_available)    
            else:
                chatbot_response(response, transport_mean_option, station_name, station_type)            