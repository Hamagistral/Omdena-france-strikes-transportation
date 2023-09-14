import streamlit as st
from googletrans import Translator
from improve_ui import translate_code

st.set_page_config(page_title="About Ile-De-France Omdena Project", page_icon='🇫🇷')

# Side bar menu
with st.sidebar:
    st.image("https://omdena.com/wp-content/uploads/2023/05/Strike-image.jpeg")
    st.markdown('## 💬 Chatbot for Alternative Transportation During Strikes in France 🤖')
    st.markdown('''
    ---
    ## 🧭 How To Use ?

    1. Choose your current mean of transportation (car, bike, walking...)
    2. Input your current location
    3. Input your desired destination
    4. Get a direction to the nearest alternative transportation that can bring you to your destination

    ---
    ''')
    
st.info('## ❔ About the project')
st.image("https://i.ibb.co/M8Z50DB/omdana-iledefrance-strike.png")

st.markdown('---')

st.markdown('### 🚌 Project background')

st.markdown('''The current social crisis in France is resulting in repetitive general strikes. These strikes often have a significant impact on 
transportation in Île-de-France. For example, train drivers’ strikes can lead to many train cancellations and the disturbance of transportation 
schedules. Strikes led by bus drivers, subway agents, and other public transport workers also lead to a significant disturbance whereas the citizens 
struggle to arrive at their workplaces, universities, etc.''')

st.markdown('---')

st.markdown('### 🔎 The problem')

st.markdown('''During a strike day, users may struggle to find reliable and accurate information about alternative transportation in Ile-De-France. 
The current transportation infrastructure lacks an efficient and effective way to provide transport users with personalized information and assistance.''')

st.markdown('---')

st.markdown('### 🎯 Project goals')

st.markdown('''The goal of this project is to develop a chatbot application that helps the citizens in the Ile-De-France by providing them with reliable and
accurate information about alternative transportation on strike days.''')

st.markdown('---')

st.markdown('### 📋 Project plan')

st.image("https://i.ibb.co/HH5qXmh/projectplan.png")
