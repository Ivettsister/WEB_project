import requests


def geocoder_request(**kwargs):
    response = requests.get('http://geocode-maps.yandex.ru/1.x/', params=kwargs)

    if not response:
        raise RuntimeError(
            'Ошибка выполнения запроса:'
            'Http статус: {} ({})'.format(response.status_code, response.reason)
        )

    return response.json()


def map_request(**kwargs):
    response = requests.get('http://static-maps.yandex.ru/1.x/', params=kwargs)

    if not response:
        raise RuntimeError(
            'Ошибка выполнения запроса:'
            'Http статус: {} ({})'.format(response.status_code, response.reason)
        )

    return response.url
