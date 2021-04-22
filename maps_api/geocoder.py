import requests

API_KEY = '40d1649f-0493-4b70-98ba-98533de7710b'


def geocoder_request(**kwargs):
    response = requests.get('http://geocode-maps.yandex.ru/1.x/', params=kwargs)
    if not response:
        raise RuntimeError(
            'Ошибка выполнения запроса:'
            'Http статус: {} ({})'.format(response.status_code, response.reason)
        )
    return response.json()


def geocode(address):
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": API_KEY,
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


def get_nearest_object(point, kind):
    ll = f"{point[0]},{point[1]}"
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": API_KEY,
        "geocode": ll,
        "format": "json"}
    if kind:
        geocoder_params['kind'] = kind
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


def get_components(data):
    try:
        for i in ['response', 'GeoObjectCollection', 'featureMember',
                  0, 'GeoObject', 'metaDataProperty', 'GeocoderMetaData',
                  'Address', 'Components']:
            data = data[i]
        return data
    except (IndexError, KeyError):
        return None


def get_city(data, lang='en_US'):
    address = get_address(data)
    data = geocoder_request(geocode=address, apikey=API_KEY, lang=lang, format='json')
    components = get_components(data)
    if components is not None:
        for component in components[::-1]:
            if component['kind'] in ('province', 'locality'):
                return component['name']
    return None


def get_country_code(data):
    data = geocoder_request(geocode=data, apikey=API_KEY, format='json')
    try:
        spic = ['response', 'GeoObjectCollection', 'featureMember',
                0, 'GeoObject', 'metaDataProperty', 'GeocoderMetaData',
                'Address', 'country_code']
        for i in range(len(spic)):
            data = data[spic[i]]
        return data
    except (IndexError, KeyError):
        print('Oh, fail!')
        return None


def get_address(data):
    data = geocoder_request(geocode=data, apikey=API_KEY, format='json')
    try:
        spic = ['response', 'GeoObjectCollection', 'featureMember', 0,
                'GeoObject', 'metaDataProperty', 'GeocoderMetaData', 'text']
        for i in range(len(spic)):
            data = data[spic[i]]
        return data
    except (IndexError, KeyError):
        print('Oh, fail!')
        return None
