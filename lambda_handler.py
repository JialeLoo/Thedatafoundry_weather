import os
import json
import requests
import boto3
from datetime import datetime, timedelta

def lambda_handler(event, context):
    # Define the API endpoint for weather data

    base_url = os.environ.get('base_url')
    api_key = os.environ.get('api_key')
    city = os.environ.get('city')
    
    weather_api_url = base_url+'q='+city+'&APPID='+api_key

    response = requests.get(weather_api_url)
    
    # Parse 'time' attribute into datetime object
    event_time = datetime.strptime(event['time'], '%Y-%m-%dT%H:%M:%SZ')  + timedelta(hours=10)
   
    if response.status_code == 200:
        # Extract weather data from the response
        weather_data = response.json()
        
        # Store weather data in S3
        s3 = boto3.client('s3')
        # Retrieve the bucket name from the environment variables
        bucket_name = os.environ.get('S3_BUCKET_NAME')
        s3_key = f"Raw_weather/{event_time}.json"
        s3.put_object(Bucket=bucket_name, Key=s3_key, Body=json.dumps(weather_data))
        
        
        # ETL pipeline
        temp_kelvin = weather_data['main']['temp']
        temp_celsius = temp_kelvin - 273.15
        feels_like_kelvin = weather_data['main']['feels_like']
        feels_like_celsius = feels_like_kelvin - 273.15
        wind_speed = weather_data['wind']['speed']
        humidity = weather_data['main']['humidity']
        
        
        # Example data as a dictionary
        data_dict = {
            "temp_celsius(C)": "{:.1f}".format(temp_celsius),
            "feels_like_celsius(C)": "{:.1f}".format(feels_like_celsius),
            "humidity(%)": humidity,
            "wind_speed(km/h)": wind_speed
        }
        
        s3_key = f"Melbourne_weather/{event_time}.json"
        s3.put_object(Bucket=bucket_name, Key=s3_key, Body=json.dumps(data_dict))

        
        return {
            'statusCode': 200,
            'body': json.dumps('Weather data stored in S3 successfully')
        }
    else:
        return {
            'statusCode': response.status_code,
            'body': json.dumps('Failed to fetch weather data from the API')
        }
