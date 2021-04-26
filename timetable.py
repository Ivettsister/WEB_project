import requests
import os
from dotenv import load_dotenv


load_dotenv()
API_KEY = os.getenv("TIMETABLE_TOKEN")


def nearest_stations_request(lat, lon, distance=50):
    request_organize = "https://api.rasp.yandex.net/v3.0/nearest_stations/"
    organization_params = {
        "apikey": API_KEY,
        "lat": lat,
        "lng": lon,
        "lang": "ru_RU",
        "distance": distance
    }
    response = requests.get(request_organize, params=organization_params)
    if response:
        json_response = response.json()
    else:
        raise RuntimeError(f"""Ошибка выполнения запроса: {request_organize} 
                        Http статус: {response.status_code} ({response.reason})""")
    stations = json_response["stations"]
    for station in stations:
        title = station["title"]
        type = station["transport_type"]
        print(f"{title} - {type}")


nearest_stations_request(55.93075855, 37.500036459921546)
