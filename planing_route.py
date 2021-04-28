import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("ROUTE_TOKEN")


def route_request(point_from, point_to, mode='driving'):
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
        it_waypoints = []
        waypoints = route[0]["steps"]
        for i in range(len(waypoints)):
            waypoint = waypoints[i]["polyline"]["points"]
            for index in range(len(waypoint)):
                it_waypoints.append(f"{waypoint[index][1]},{waypoint[index][0]}")
        while len(it_waypoints) > 100:
            it_waypoints = it_waypoints[0:-1:2]
        return ','.join(it_waypoints)
    except:
        return None
