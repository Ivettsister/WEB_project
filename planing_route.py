import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("ROUTE_TOKEN")


def route_request(point_from, point_to, mode='walking'):
    request_organize = "https://api.routing.yandex.net/v2/route"
    route_between = f"{point_from}|{point_to}"
    organization_params = {
        "apikey": API_KEY,
        "waypoints": route_between,
        "mode": mode
    }
    response = requests.get(request_organize, params=organization_params)
    if response:
        json_response = response.json()
    else:
        return None
    try:
        route = json_response["route"]["legs"]
        it_waypoints = ''
        waypoints = route[0]["steps"][0]["polyline"]["points"]
        for index in range(len(waypoints)):
            if index != (len(waypoints) - 1):
                it_waypoints += f"{waypoints[index][1]},{waypoints[index][0]},"
            else:
                it_waypoints += f"{waypoints[index][1]},{waypoints[index][0]}"
        return it_waypoints
    except:
        return None
