import requests
import json

def traffic_request():
    url = "https://api-ratp.pierre-grimaud.fr/v4/traffic"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        indented_data = json.dumps(data, indent=2)
        with open('traffic_request.json', 'w') as file:
            file.write(indented_data)

    return indented_data

scraped_data_traffic = traffic_request()
print(scraped_data_traffic)