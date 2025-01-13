import json
import os

def load_settings(file_path="settings.json"):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Settings file not found: {file_path}")
        with open(file_path, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading settings: {e}")
        return {"temperature_threshold": 25}

def check_temperature(temperature, threshold=None):
    if threshold is None:
        settings = load_settings()
        threshold = settings.get("temperature_threshold", 25)
    
    if temperature < threshold - 5:
        return "Попередження: температура занадто низька"
    elif temperature > threshold + 5:
        return "Попередження: температура занадто висока"
    else:
        return "Температура в безпечному діапазоні"
