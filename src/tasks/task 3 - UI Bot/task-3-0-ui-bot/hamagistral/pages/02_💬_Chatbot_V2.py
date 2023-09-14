from streamlit_extras.colored_header import colored_header
from streamlit_folium import folium_static
from streamlit_folium import st_folium
from streamlit_chat import message
from googletrans import Translator
from folium.plugins import Draw

import streamlit as st
import folium


from chatbot_navitia import generate_response, get_navitia_journey, journey_summary, get_journey_steps, get_area_name, plot_route_on_map, translate

translator = Translator()
# variable of language options
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
        question = st.text_input(translate("You :", selected_language), "Stade de France", key="input")
        return question

    # Initialization of the chat prompts
    if 'generated' not in st.session_state:
        st.session_state['generated'] = [translate("👋🏻 Hello! I am Paris TransportChat, where are you trying to go ?", selected_language)]

    if 'past' not in st.session_state:
        st.session_state['past'] = [translate('Hi !', selected_language)]

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
                message(translate(st.session_state["generated"][i], selected_language), key=str(i), avatar_style="bottts-neutral", seed=90)
                message(translate(st.session_state['past'][i], selected_language), is_user=True, key=str(i) + '_user', avatar_style="avataaars-neutral", seed=10)    

with map_col:
    # Select Transportation Mean to the Station
    transport_options = {
        translate("🚶‍♂️ Walking", selected_language_code): 'slow_walker',
        translate("🧳 Luggage", selected_language_code): 'luggage',
        translate("🚲 Bike", selected_language_code): 'cyclist',
        translate("🦽 Wheelchair", selected_language_code): 'wheelchair'
    }

    transport_mean_option = st.radio(translate("🚙 Please provide your current mean of transportation:", selected_language_code), list(transport_options.keys()), horizontal=True)
    transport_mean_value = transport_options[transport_mean_option]

    # Select Station Type 
    station_options = {
        translate("🚈 Rer", selected_language_code): 'RapidTransit',
        translate("🚆 Transilien", selected_language_code): 'LocalTrain',
        translate("🚇 Metro", selected_language_code): 'Metro',
        translate("🚊 Tramway", selected_language_code): 'Tramway',
        translate("🚍 Bus", selected_language_code): 'Bus',
        translate("🛸 Any", selected_language_code): ''
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

                route_start_loc = f'{longitude_startloc};{latitude_startloc}'
                route_dest_loc = f'{longitude_destloc};{latitude_destloc}'

                best_route = get_navitia_journey(route_start_loc, route_dest_loc, transport_mean_value, station_type_value)

                if 'error' in best_route:
                    st.error(f"🚨 {best_route['error']['message'].capitalize()}. Please try another preffered transportation mode.")
                else:
                    folium.Marker(start_loc, icon=folium.Icon(color='blue'), tooltip=f"📍 Current Location: {start_loc_name}").add_to(m_route)

                    try:
                        plot_route_on_map(best_route, m_route)
                    except:
                        folium.Marker(dest_loc, icon=folium.Icon(color='red'), tooltip=f"🛎️ Destination: {dest_loc_name}").add_to(m_route)
                        pass

                    route_map = folium_static(m_route, width=800, height=450)

                    journey_summary(best_route, transport_mean_option, station_type_option)

                    # Print the instructions
                    st.info(f"🧭 **{translate('Directions', selected_language_code)}** :  ")
                    
                    get_journey_steps(best_route, station_type_value)


            
        


