import requests

API_KEY = '40d1649f-0493-4b70-98ba-98533de7710b'


def geocode(address):
    geocoder_request = "http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": address,
        "format": "json"}
    response = requests.get(geocoder_request, params=geocoder_params)
    if response:
        json_response = response.json()
    else:
        raise RuntimeError(
            f"""Ошибка выполнения запроса:
            {geocoder_request}
            Http статус: {response.status_code} ({response.reason})""")
    features = json_response["response"]["GeoObjectCollection"]["featureMember"]
    if features:
        return features[0]["GeoObject"]
    else:
        return None


def get_coordinates(address):
    toponym = geocode(address)
    if not toponym:
        return None, None
    toponym_coodrinates = toponym["Point"]["pos"]
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    return float(toponym_longitude), float(toponym_lattitude)


def get_ll_span(address):
    toponym = geocode(address)
    if not toponym:
        return None, None
    toponym_coodrinates = toponym["Point"]["pos"]
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    ll = ",".join([toponym_longitude, toponym_lattitude])
    envelope = toponym["boundedBy"]["Envelope"]
    l, b = envelope["lowerCorner"].split(" ")
    r, t = envelope["upperCorner"].split(" ")
    dx = abs(float(l) - float(r)) / 2.0
    dy = abs(float(t) - float(b)) / 2.0
    span = f"{dx},{dy}"
    return ll, span


def get_district(lat, lon):
    pass


def get_nearest_object(point1, point2):
    ll = f"{point1[0]},{point1[1]}"
    spn = f"{point2[0]},{point2[1]}"
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": API_KEY,
        "ll": ll,
        "spn": spn,
        "type": 'biz',
        "kind": 'аптека'}
    """if kind:
        geocoder_params['kind'] = kind"""
    print(geocoder_params)
    response = requests.get(geocoder_request, params=geocoder_params)
    if not response:
        raise RuntimeError(
            f"""Ошибка выполнения запроса:
            {geocoder_request}
            Http статус: {response.status_code,} ({response.reason})""")
    json_response = response.json()
    features = json_response["response"]["GeoObjectCollection"]["featureMember"]
    if features:
        return features[0]["GeoObject"]["name"]
    else:
        return None
