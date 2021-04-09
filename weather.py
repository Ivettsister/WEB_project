import requests


def get_city_id(city, countrycode, token):
    locality = ','.join([city, countrycode])

    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/find",
                           params={'q': locality, 'type': 'like', 'units': 'metric', 'APPID': token})
        data = res.json()

        return data['list'][0]['id']

    except Exception as e:
        return -1


def get_current_weather(city, countrycode, token, runame):
    city_id = get_city_id(city, countrycode, token)
    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                           params={'id': city_id, 'units': 'metric', 'lang': 'ru', 'APPID': token})
        data = res.json()

        return 'Текущая погода в городе {}:\n\n-{} {}\n-Температура воздуха: {}°С\n-Влажность воздуха: {}%\n-Скорость ' \
               'ветра: {} м/с'.format(runame, data['weather'][0]['description'].capitalize(),
                                      data['weather'][0]['icon'],
                                      data['main']['temp'], data['main']['humidity'], data['wind']['speed'])
    except Exception as e:
        print("Exception (find):", e)
        return 'Ошибка запроса! Погоды для данного города не найдено:('


def get_forecast_weather(city, countrycode, token, runame):
    city_id = get_city_id(city, countrycode, token)
    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/forecast?",
                           params={'id': city_id, 'units': 'metric', 'lang': 'ru', 'APPID': token})
        data = res.json()
        temps = {}
        weather = {}
        for forecast in data['list']:
            date = forecast['dt_txt'].split()[0]
            if date not in temps:
                temps[date] = set()
            if date not in weather:
                weather[date] = set()
            temps[date].add(forecast['main']['temp'])
            weather[date].add(forecast['weather'][0]['description'])
        res = 'Прогноз погоды в городе {}:\n\n'.format(runame)
        for date in temps.keys():
            res += '{}\n-В течение дня: {}\n-Максимальная температура: {}°С\n-Минимальная ' \
                   'температура: {}°С\n\n'.format('/'.join(reversed(date.split('-'))), ', '.join(weather[date]),
                                                  max(temps[date]), min(temps[date]))
    except Exception as e:
        print("Exception (find):", e)
        return 'Ошибка запроса! Погоды для данного города не найдено:('
    return res
