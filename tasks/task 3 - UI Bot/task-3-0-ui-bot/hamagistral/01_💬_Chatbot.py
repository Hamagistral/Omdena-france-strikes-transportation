from streamlit_extras.colored_header import colored_header
from streamlit_folium import folium_static
from streamlit_folium import st_folium
from streamlit_chat import message
from folium.plugins import Draw

import streamlit as st
import folium

from chatbot_man import chatbot_response, generate_response, get_directions, create_route_map, route_station_dest_station, get_area_name, find_nearest_velib_station, find_nearest_ratp_station, find_nearest_bus_station, translate

# Languages options
languages = options = {
                "English": "en",
                "French": "fr",
                "Spanish": "es"
            }

# Page layout
st.set_page_config(page_title="Ile-De-France Alternative Transportation", layout="wide", page_icon='🇫🇷')

# Side bar menu
with st.sidebar:
    st.image("https://omdena.com/wp-content/uploads/2023/05/Strike-image.jpeg")

    # Make a language choice
    selected_language = st.sidebar.selectbox("🗣️ Select Language:", list(languages.keys()))
    selected_language_code = languages[selected_language]

    st.markdown("## 💬 " + translate('Chatbot for Alternative Transportation During Strikes in France 🤖', selected_language_code))

    st.markdown("---")
    
    st.markdown(translate("## 🧭 How To Use ?", selected_language_code))
    
    st.write(translate("1. Choose your current mean of transportation (car, bike, walking...)", selected_language_code))
    st.write(translate("2. Input your current location", selected_language_code))
    st.write(translate("3. Input your desired destination", selected_language_code))
    st.write(translate("4. Get a direction to the nearest alternative transportation that can bring you to your destination", selected_language_code))

st.markdown("# 🚇 " + translate("Île-De-France Alternative Transportation Chatbot 🚍", selected_language_code))
colored_header(label='', description='', color_name='blue-30')

st.markdown("#")

chatbot_col, map_col = st.columns([2, 3], gap="medium")

with chatbot_col:
    # Layout of input/response containers
    input_container = st.container()
    response_container = st.container()

    def get_text():
        question = st.text_input("You :", "Stade de France", key="input")
        return question

    # Initialization of the chat prompts
    if 'generated' not in st.session_state:
        st.session_state['generated'] = [translate("👋🏻 Hello! I am Île-De-France Alternative Transportation Chatbot, where are you trying to go ?", selected_language_code)]

    if 'past' not in st.session_state:
        st.session_state['past'] = [translate('Hi !', selected_language_code)]

    with input_container:
        user_input = get_text()
        send_btn = st.button(translate('Send', selected_language_code))

        st.markdown("#")

    ## Conditional display of AI generated responses as a function of user provided prompts
    with response_container:
        if send_btn and user_input:
            response = translate(generate_response(user_input), selected_language)
            st.session_state.past.append(user_input)
            st.session_state.generated.append(response)
                
        if st.session_state['generated']:
            for i in range(len(st.session_state['generated'])-1, -1, -1):
                message(st.session_state["generated"][i], key=str(i), avatar_style="bottts-neutral", seed=90)
                message(st.session_state['past'][i], is_user=True, key=str(i) + '_user', avatar_style="avataaars-neutral", seed=10)    

with map_col:  
    # Select Transportation Mean to the Station
    transport_options = {
        translate("🚘 Car", selected_language_code): 'driving-car',
        translate("🚲 Bike", selected_language_code): 'cycling-road',
        translate("🚶‍♂️ Walking", selected_language_code): 'foot-walking',
        translate("🦽 Wheelchair", selected_language_code): 'wheelchair'
    }

    transport_mean_option = st.radio(translate("🛸 Please provide your current mean of transportation:", selected_language_code), list(transport_options.keys()), horizontal=True)
    transport_mean_value = transport_options[transport_mean_option]

    # Select Station Type 
    station_options = {
        translate("🚲 Velib", selected_language_code): 'VELIB',
        translate("🚈 Rer", selected_language_code): 'RER',
        translate("🚆 Transilien", selected_language_code): 'TRAIN',
        translate("🚇 Metro", selected_language_code): 'METRO',
        translate("🚊 Tramway", selected_language_code): 'TRAMWAY',
        translate("🚍 Bus", selected_language_code): 'BUS'
    }

    station_type_option = st.radio(translate("🚉 Please provide your preffered station type:", selected_language_code), list(station_options.keys()), horizontal=True)
    station_type_value = station_options[station_type_option]

    # Current location & destination maps
    st.markdown(translate("#### 📍 Please provide your current and destination location :", selected_language_code))

    # Input Map (Starting & Destination Location)
    m_input  = folium.Map(location=[48.866667, 2.333333], zoom_start=10, min_zoom=10)

    # Add Location Marker
    Draw(draw_options={
            'polyline': False, 'rectangle': False, 
            'circle': False, 'polygon': False,
            'circlemarker': False
        }, edit_options={'edit': False}).add_to(m_input)

    input_map = st_folium(m_input, width=800, height=450, key='1')

    # Check if there's atleast one marker and markers are not more than 2
    if input_map['last_active_drawing'] and len(input_map['all_drawings']) >= 2:

        all_drawings = input_map['all_drawings']

        if len(all_drawings) > 2:
            st.warning(translate("⚠️ Please select only one current location and one destination.", selected_language_code))
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

                st.info(f"🧳 **{translate('Current Location', selected_language_code)}** : {start_loc_name} *(Latitude : {latitude_startloc}, Longitude : {longitude_startloc})*")
                st.info(f"🛎️ **{translate('Destination Location', selected_language_code)}** : {dest_loc_name} *(Latitude : {latitude_destloc}, Longitude : {longitude_destloc})*")

                st.markdown(translate("#### 🗺️ Here's the route to the nearest transportation station:", selected_language_code))
                        
                m_route = folium.Map(location=[48.866667, 2.333333], zoom_start=10, min_zoom=10)
                Draw(draw_options={
                            'polyline': False, 'rectangle': False, 
                            'circle': False, 'polygon': False,
                            'circlemarker': False
                        }, edit_options={'edit': False}).add_to(m_route)

                route_start_loc = f'{longitude_startloc}, {latitude_startloc}'
                route_dest_loc = f'{longitude_destloc}, {latitude_destloc}'

                if station_type_value == "VELIB":
                    nearest_station, closest_dest_station, closest_dest_station_name, station_name, num_bikes_available = find_nearest_velib_station(latitude_startloc, longitude_startloc, latitude_destloc, longitude_destloc)
                elif station_type_value == "BUS":
                    nearest_station, closest_dest_station, closest_dest_station_name, station_name, station_type = find_nearest_bus_station(latitude_startloc, longitude_startloc, latitude_destloc, longitude_destloc)
                else:
                    nearest_station, closest_dest_station, closest_dest_station_name, station_name, station_type, transport_type, transport_type_status = find_nearest_ratp_station(latitude_startloc, longitude_startloc, latitude_destloc, longitude_destloc, station_type_value)

                lat_stationloc = nearest_station[0]
                long_stationloc = nearest_station[1]
                
                route_station_loc = f'{long_stationloc}, {lat_stationloc}'

                directions_input_station = get_directions(route_start_loc, route_station_loc, transport_mean_value)

                create_route_map(directions_input_station, m_route, start_loc_name, station_name, station_type_option, "green")

                folium.Marker(dest_loc, icon=folium.Icon(color='red'), tooltip=f"🛎️ Destination: {dest_loc_name}").add_to(m_route)
                
                if station_type_value == "VELIB":
                    folium.Marker(closest_dest_station, icon=folium.Icon(color='green'), tooltip=f"🚲 Destination Station : {closest_dest_station_name}").add_to(m_route)

                    lat_dest_stationloc = closest_dest_station[0]
                    long_dest_stationloc = closest_dest_station[1]
                    
                    route_dest_station_loc = f'{long_dest_stationloc}, {lat_dest_stationloc}'

                    directions_station_dest_station = get_directions(route_station_loc, route_dest_station_loc, "cycling-regular")

                    route_station_dest_station(directions_station_dest_station, m_route, "blue")
                else:
                    folium.Marker(closest_dest_station, icon=folium.Icon(color='green'), tooltip=f"🚉 Destination Station : {closest_dest_station_name}").add_to(m_route)

                route_map = folium_static(m_route, width=800, height=450)

                if station_type_value == "VELIB":
                    chatbot_response(directions_input_station, transport_mean_option, station_name, num_bikes_available, '', '')
                elif station_type_value == "BUS":
                    chatbot_response(directions_input_station, transport_mean_option, station_name, 'BUS', station_type, '')
                else:
                    chatbot_response(directions_input_station, transport_mean_option, station_name, station_type, transport_type, transport_type_status)

                directions_dict = directions_input_station.json()
                
                # Extract the 'steps' field from the directions dictionary
                steps = directions_dict['features'][0]['properties']['segments'][0]['steps']

                # Generate the list of instructions
                instructions = []
                for i, step in enumerate(steps):
                    distance = step['distance']
                    duration = step['duration']
                    instruction = step['instruction']
                    instructions.append(f"\n **Step {i+1}**: {instruction} | {transport_mean_option[0]} {'**Distance:** ' + str(round(distance))  + ' meters' if i != len(steps) -1 else '**You arrived to your destination!** 🎉'} \n")

                # Print the instructions
                instruction_text = '\n'.join(instructions)
                st.info(f"🧭 **{translate('Directions', selected_language_code)}** :  ")
                
                st.info(translate(f"{instruction_text}", selected_language_code))
