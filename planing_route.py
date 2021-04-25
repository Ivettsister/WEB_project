import requests

API_KEY = 'ждём...'


def route_request(**kwargs):
    response = requests.get('https://api.routing.yandex.net/v2/route', params=kwargs)
    if not response:
        raise RuntimeError(
            'Ошибка выполнения запроса:'
            'Http статус: {} ({})'.format(response.status_code, response.reason)
        )
    return response.json()


def geocode(from_adress, to_adress):
    response = requests.get(f"https://api.routing.yandex.net/v2/route?waypoints=56.856617,60.602026|56.795675,60.631176&mode=transit&apikey={API_KEY}")
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
