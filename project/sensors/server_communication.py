import requests

def send_data_to_server(temperature, humidity, server_url, sensor_id):
    data = {'temperature': temperature, 'humidity': humidity, 'sensor_id': sensor_id}
    response = requests.post(server_url, json=data)
    return response.status_code
