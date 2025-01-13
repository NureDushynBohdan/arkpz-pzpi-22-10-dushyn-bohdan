import time
import random
import json
import requests
import os
from data_processing import check_temperature
from server_communication import send_data_to_server
from config import SERVER_URL, SENSOR_ID

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")

def fetch_sensor_value(sensor_id, server_url):
    try:
        response = requests.get(f"{server_url}/sensors/{sensor_id}/value/")
        response.raise_for_status() 
        data = response.json()
        value = data.get("value", "25").replace("°C", "").strip() 
        return float(value) 
    except requests.exceptions.RequestException as e:
        print(f"Помилка отримання значення датчика: {e}")
        return 25 

def update_settings_file(threshold):
    settings = {"temperature_threshold": threshold}
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file)

def read_temperature_threshold():
    with open(SETTINGS_FILE, "r") as file:
        settings = json.load(file)
        return settings["temperature_threshold"]

def main():
    temperature_threshold = fetch_sensor_value(SENSOR_ID, SERVER_URL)
    print(f"Температурний поріг, отриманий від датчика: {temperature_threshold}°C")

    update_settings_file(temperature_threshold)

    iterations = 0
    while iterations < 5:
        try:
            temperature = random.uniform(18, 30)
            humidity = random.uniform(40, 70)

            print(check_temperature(temperature, temperature_threshold))

            response_code = send_data_to_server(temperature, humidity, SERVER_URL, SENSOR_ID)
            if response_code == 200:
                print("Дані успішно надіслано.")
                break
            else:
                print("Не вдалося надіслати дані.")
                iterations += 1

            time.sleep(2)
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    main()
