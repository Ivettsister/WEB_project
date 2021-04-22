import requests

API_KEY = '9fc14eed-73a1-4799-9473-a1140264b26f'


def route_request(**kwargs):
    response = requests.get('https://api.routing.yandex.net/v2/route', params=kwargs)
    if not response:
        raise RuntimeError(
            'Ошибка выполнения запроса:'
            'Http статус: {} ({})'.format(response.status_code, response.reason)
        )
    return response.json()


def geocode(from_adress, to_adress):
    waypoint = f"{from_adress}|{to_adress}"
    route_request = f"https://api.routing.yandex.net/v2/route"
    route_params = {
        "apikey": '9fc14eed-73a1-4799-9473-a1140264b26f',
        "waypoints": waypoint}
    response = requests.get(route_request, params=route_params)
    if response:
        json_response = response.json()
    else:
        raise RuntimeError(
            f"""Ошибка выполнения запроса:
            {route_request}
            Http статус: {response.status_code} ({response.reason})""")
    features = json_response["response"]
    if features:
        return features
    else:
        return None


from_adress = '37.500342,55.931225'
to_adress = '37.518434,55.929444'
print(geocode(from_adress, to_adress))
