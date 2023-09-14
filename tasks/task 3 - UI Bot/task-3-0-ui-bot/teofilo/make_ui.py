import streamlit as st
import json
from streamlit_lottie import st_lottie
import requests
from streamlit_option_menu import option_menu
import numpy
from googletrans import Translator
from streamlit_folium import st_folium
import folium

# Geolocation
from geopy.geocoders import Nominatim

# Instantiating a Translator object
translator = Translator()

# GitHub: https://github.com/andfanilo/streamlit-lottie
# Lottie Files: https://lottiefiles.com/


# Lottie animation url
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Page layout
st.set_page_config(page_title='Omdena-Ile-de-France',
                   layout='wide')


# Side bar menu
with st.sidebar:
    selected = option_menu(
        menu_title = "Main Menu",
        options = ['Home', 'About', 'Try it now', 'Settings'],
        icons=['house', 'book', 'chat-dots', 'tools'],
        menu_icon='cast',
        default_index=0,
        styles={
        "container": {"padding": "0!important", "background-color": "#ADD8E6"},
        "icon": {"color": "orange", "font-size": "25px"}, 
        "nav-link": {"font-size": "25px", "text-align": "left", "margin":"0px", "--hover-color": "#00FFFF"},
        "nav-link-selected": {"background-color": "#00FFFF"},
    }
    )
    
# Home
if selected == 'Home':
    st.title("Conversational AI Chatbot For Alternative Transportation During Strikes in France :cycle")

     # Load lottie url - chatbot hello
    lottie_animation = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_og5hz8nv.json")

    # Animate
    st_lottie(
        lottie_animation,
        speed=1,
        reverse=False,
        loop=True,
        quality="low", # medium ; high
        height=None,
        width=None,
        key=None,
    )
    
# About    
elif selected == 'About':
    st.title("About Us")
    
    # Columns
    abt_col1, abt_col2 = st.columns(2)
    
    # Column 1
    

# Try it now    
elif selected == 'Try it now':
    st.title('Are you stranded due to a strike? We can help you find alternative transport')
    
    # Load lottie url - bicycle
    lottie_animation = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_iCUJtrbdxk.json")
    
    # Animate
    st_lottie(
        lottie_animation,
        speed=1,
        reverse=False,
        loop=True,
        quality="low", # medium ; high
        height=None,
        width=None,
        key=None,
    )
    
    # Current Location
    st.markdown("Location")
    current_location = st.text_input("What is your current Location?")
    current_latitude = st.number_input(label='Latitude', min_value=-90.00, max_value=90.00, step=1.,format="%.8f", value=48.864716)
    current_longitude = st.number_input(label='Longitude', min_value=-180.00, max_value=180.00, step=1.,format="%.8f", value=2.349014)
    
    # Nearest velib location
    
    
    
    # Destination location
    
    
    
    # Foium map
    m = folium.Map(Location = [current_latitude, current_longitude], zoom_start = 5)
    
    # Mark current location on the map
    folium.Marker(
        [current_latitude, current_longitude],
        popup = current_location,
        tooltip =current_location,
        icon = folium.Icon(color='blue')
    ).add_to(m)
    
    
    # folium.Marker(
    #     [nearest_velib_latitude, nearest_velib_longitude]
    # )
    
    st_data = st_folium(m, width=725)
    
elif selected == 'Settings':
    
    # Still working on it
    st.title('Language Preference')
    
    # Language codes dictionary
    language_codes = {'English': 'en',
                      'français': 'fr',
                      'Deutsch': 'de',
                      'Italiano': 'it',
                      'Español': 'es',
                      'Portugues': 'pt'}
    
    

    selected_language = st.selectbox(label="Language / Langue / Sprache / idioma / lingua / linguagem", 
                                     options=list(language_codes.keys()),
                                     index=0)
    
    