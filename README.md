<div align="center">
  <a href="#">
    <img src="https://github.com/Hamagistral/Omdena-france-strikes-transportation/assets/66017329/0dafd773-bc58-4942-a2f2-ed1154e1f975" alt="Banner" width="890">
  </a>

  <div id="user-content-toc">
    <ul>
      <summary><h1 style="display: inline-block;">Omdena AI France Chapter Project</h1></summary>
    </ul>
  </div>
  
  <p>Building a Conversational AI Chatbot for Alternative Transportation During Strikes in France</p>
    <a href="https://www.youtube.com/watch?v=MHPyRCB5QLk" target="_blank">Demo</a>
    🚕
    <a href="https://omdena.com/chapter-challenges/building-a-conversational-ai-chatbot-for-alternative-transportation-during-strikes/" target="_blank">Project Source</a>
    🛸
    <a href="https://github.com/Hamagistral/Omdena-france-strikes-transportation/issues" target="_blank">Request Feature</a>
</div>
<br>

## 📝 Table of Contents

1. [ Project Overview ](#introduction)
2. [ Key Features ](#features)
3. [ Project Architecture ](#arch)
4. [ Usage ](#usage)
5. [ Team ](#team)
6. [ Contact ](#contact)

<a name="introduction"></a>
## 🔬 Project Overview :

#### 🚇 Project background

The current social crisis in France is resulting in repetitive general strikes. These strikes often have a significant impact on transportation in Île-de-France. For example, train drivers’ strikes can lead to many train cancellations and the disturbance of transportation schedules. Strikes led by bus drivers, subway agents, and other public transport workers also lead to a significant disturbance whereas the citizens struggle to arrive at their workplaces, universities, etc.

#### ❔ The problem

During a strike day, users may struggle to find reliable and accurate information about alternative transportation in Ile-De-France. The current transportation infrastructure lacks an efficient and effective way to provide transport users with personalized information and assistance.

#### 🎯 Project goals

The goal of this project is to develop a chatbot application that helps the citizens in the Ile-De-France by providing them with reliable and accurate information about alternative transportation on strike days.

<a name="features"></a>
## 🔌 Key Features

- **Real-Time Transportation Information:** Provide up-to-the-minute information about the status of various transportation options (trains, buses, etc.) in Île-de-France.

- **Alternative Route Calculation:** Calculate alternative routes for users based on their preferences, current location, and destination, considering factors like mode of transportation and strikes.

- **Interactive Chatbot UI:** Offer an interactive chatbot interface alongside a map for an engaging and user-friendly experience.

- **Strike Impact Reduction:** Help users navigate transportation strikes in Île-de-France more effectively, reducing the impact on their daily commutes.

<a name="arch"></a>
## 📝 Project Architecture

### 1️⃣ Version 1

![image](https://github.com/Hamagistral/Omdena-france-strikes-transportation/assets/66017329/404d2004-ba0d-46d9-b9d1-7c3e384489a2)

- Web scraping: [Notebook](https://github.com/Hamagistral/Omdena-france-strikes-transportation/blob/master/tasks/task%201%20-%20Data%20Collection/hamagistral/scraping_traffic_status.ipynb)
- Nearest Station Algorithm: [Notebook](https://github.com/Hamagistral/Omdena-france-strikes-transportation/blob/master/tasks/task%201%20-%20Data%20Collection/hamagistral/train_ratp_stations.ipynb)
- [Version 1 Back End](https://github.com/Hamagistral/Omdena-france-strikes-transportation/blob/master/tasks/task%203%20-%20UI%20Bot/task-3-0-ui-bot/hamagistral/chatbot_man.py)
- [Version 1 Front End](https://github.com/Hamagistral/Omdena-france-strikes-transportation/blob/master/tasks/task%203%20-%20UI%20Bot/task-3-0-ui-bot/hamagistral/01_%F0%9F%92%AC_Chatbot.py)

### 2️⃣ Version 2

![image](https://github.com/Hamagistral/Omdena-france-strikes-transportation/assets/66017329/702027df-ae62-4ae0-ace3-60be7c9f51b6)

- Extracting Informations from Navitia API : [Notebook](https://github.com/Hamagistral/Omdena-france-strikes-transportation/blob/master/tasks/task%201%20-%20Data%20Collection/hamagistral/navitia_route.ipynb)
- [Version 2 Back End](https://github.com/Hamagistral/Omdena-france-strikes-transportation/blob/master/tasks/task%203%20-%20UI%20Bot/task-3-0-ui-bot/hamagistral/chatbot_navitia.py)
- [Version 2 Front End](https://github.com/Hamagistral/Omdena-france-strikes-transportation/blob/master/tasks/task%203%20-%20UI%20Bot/task-3-0-ui-bot/hamagistral/pages/02_%F0%9F%92%AC_Chatbot_V2.py)

For more information, please refer to the [project report](https://github.com/Hamagistral/Omdena-france-strikes-transportation/blob/master/report/Omdena%20Ile-De-France%20Report%20.pdf).

### 🛠️ Technologies Used

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![ChatGPT](https://img.shields.io/badge/OpenAI-74aa9c?style=for-the-badge&logo=openai&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)
<img src="https://github.com/Hamagistral/Omdena-france-strikes-transportation/assets/66017329/4b0f2110-5833-4ebc-a51b-a091310805e3" alt="streamlit" width="85">
<img src="https://user-images.githubusercontent.com/66017329/223900076-e1d5c1e5-7c4d-4b73-84e7-ae7d66149bc6.png" alt="streamlit" width="120">


<a name="usage"></a>
## 💻 Usage

1. Clone the repository:

```
git clone https://github.com/Hamagistral/Omdena-france-strikes-transportation.git
```

2. Go to the UI folder:

```
cd tasks/task 3 - UI Bot/task-3-0-ui-bot/hamagistral
```

3. Install the required dependencies:

```
pip install -r requirements.txt
```

3. Run the app:
```
streamlit run 01_💬_Chatbot.py
```

4. Access the app in your browser at http://localhost:8501

<a name="team"></a>
## 👥 Team

Special thanks to the following contributors who have dedicated their time and expertise to this project:

- Juan Olano
- Viktor Ivanenko
- Shaifali Khulbe
- Teofilo Acholla
- Guillaume Soto
- Feten Ben
- Lydia Chibout
- Lamia Sekkai

Your contributions have played a crucial role in making this project a success. Your dedication and hard work are greatly appreciated. Thank you for being a valuable part of the team!

![image](https://github.com/Hamagistral/Omdena-france-strikes-transportation/assets/66017329/4446fd96-57b2-4293-9c85-1a7c90ac4922)

<a name="contact"></a>
## 📨 Contact Me

[LinkedIn](https://www.linkedin.com/in/hamza-elbelghiti/) •
[Website](https://Hamagistral.me) •
[Gmail](hamza.lbelghiti@gmail.com)
