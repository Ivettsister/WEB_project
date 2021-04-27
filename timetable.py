import requests
import datetime
import os
from dotenv import load_dotenv


load_dotenv()
API_KEY = os.getenv("TIMETABLE_TOKEN")


def nearest_stations_request(lat, lon, distance=2):
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
    if len(stations) > 0:
        slov_stations = {}
        for station in stations:
            title = station["title"]
            code = station["code"]
            slov_stations[f"{title}"] = code
        return slov_stations
    else:
        return {}


def get_transport(code):
    request_organize = "https://api.rasp.yandex.net/v3.0/schedule/"
    organization_params = {
        "apikey": API_KEY,
        "station": code,
        "date": datetime.date.today()
    }
    response = requests.get(request_organize, params=organization_params)
    if response:
        json_response = response.json()
    else:
        raise RuntimeError(f"""Ошибка выполнения запроса: {request_organize} 
                        Http статус: {response.status_code} ({response.reason})""")
    stations = json_response["schedule"]
    spic = []
    for station in stations:
        find_title = station["thread"]["title"]
        find_departure = station["departure"]
        find_departure = find_departure.split('T')[1]
        if f"{find_title} - {find_departure}" not in spic:
            spic.append(f"{find_title}; Первый рейс по расписанию - {find_departure}")
    return spic
