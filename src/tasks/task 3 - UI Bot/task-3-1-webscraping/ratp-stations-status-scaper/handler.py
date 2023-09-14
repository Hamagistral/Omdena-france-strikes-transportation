from bs4 import BeautifulSoup as bs

import pandas as pd
import requests
import boto3
import os

def scrape_stations_status():
    ratp = requests.get("https://www.ratp.fr/")

    soup = bs(ratp.content, 'html.parser')

    transportations_btns = soup.find_all('button', class_='border-line')

    perturbations = []
    for btn in transportations_btns:
        perturbation_span = btn['aria-label']
        perturbations.append(perturbation_span)

    df = pd.DataFrame([x.split(', ')[:2] for x in perturbations], columns=['name', 'status'])

    # Extract the name without leading/trailing spaces
    df['name'] = df['name'].str.strip()

    return df

def export_data_to_s3(data):
    s3 = boto3.client('s3')
    csv_data = data.to_csv(index=False)

    bucket_name = "omdena-paris-ratp-stations-status-useast1"
    file_name = "ratp_stations_traffic_status.csv"

    s3.put_object(Body=csv_data, Bucket=bucket_name, Key=file_name)

    print("Dataframe is saved as CSV in S3 bucket.")

def scrape(event, context):
    data = scrape_stations_status()
    export_data_to_s3(data)