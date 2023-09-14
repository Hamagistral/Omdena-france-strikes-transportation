import streamlit as st

st.set_page_config(page_title="About Ile-De-France Omdena Project", page_icon='🇫🇷')
from chatbot_man import translate

# Languages options
languages = options = {
                "English": "en",
                "French": "fr",
                "Spanish": "es"
            }

# Side bar menu
with st.sidebar:
    st.image("https://omdena.com/wp-content/uploads/2023/05/Strike-image.jpeg")

    # Make a language choice
    selected_language = st.sidebar.selectbox("Select Language:", list(languages.keys()))
    selected_language_code = languages[selected_language]

    st.markdown("## 💬 " + translate('Chatbot for Alternative Transportation During Strikes in France 🤖', selected_language_code))

    st.markdown("---")
    
    st.markdown(translate("## 🧭 How To Use ?", selected_language_code))
    
    st.write(translate("1. Choose your current mean of transportation (car, bike, walking...)", selected_language_code))
    st.write(translate("2. Input your current location", selected_language_code))
    st.write(translate("3. Input your desired destination", selected_language_code))
    st.write(translate("4. Get a direction to the nearest alternative transportation that can bring you to your destination", selected_language_code))
    
st.info('## ❔ '+ translate('About the project', selected_language_code))
st.image("https://i.ibb.co/M8Z50DB/omdana-iledefrance-strike.png")

st.markdown('---')

st.markdown('### 🚌 ' + translate('Project background', selected_language_code))

st.markdown(translate('''The current social crisis in France is resulting in repetitive general strikes. These strikes often have a significant impact on 
transportation in Île-de-France. For example, train drivers strikes can lead to many train cancellations and the disturbance of transportation 
schedules. Strikes led by bus drivers, subway agents, and other public transport workers also lead to a significant disturbance whereas the citizens 
struggle to arrive at their workplaces, universities, etc.''', selected_language_code))

st.markdown('---')

st.markdown('### 🔎 ' + translate('The problem', selected_language_code))

st.markdown(translate('''During a strike day, users may struggle to find reliable and accurate information about alternative transportation in Ile-De-France. 
The current transportation infrastructure lacks an efficient and effective way to provide transport users with personalized information and assistance.''', selected_language_code))

st.markdown('---')

st.markdown('### 🎯 ' + translate('Project goals', selected_language_code))

st.markdown(translate('''The goal of this project is to develop a chatbot application that helps the citizens in the Ile-De-France by providing them with reliable and
accurate information about alternative transportation on strike days.''', selected_language_code))

st.markdown('---')

st.markdown('### 📋 ' + translate('Project plan', selected_language_code))

st.image("https://i.ibb.co/HH5qXmh/projectplan.png")
