import requests
import os
from dotenv import load_dotenv


load_dotenv()
API_KEY = os.getenv("ORGANIZATION_TOKEN")


def make_organization_request(ll, text, quantity=10):
    request_organize = "https://search-maps.yandex.ru/v1/"
    organization_params = {
        "apikey": API_KEY,
        "text": text,
        "lang": "ru_RU",
        "type": "biz",
        "results": quantity,
        "ll": ll,
        "spn": "0.05, 0.05"
    }
    response = requests.get(request_organize, params=organization_params)
    if response:
        json_response = response.json()
    else:
        raise RuntimeError(f"""Ошибка выполнения запроса: {request_organize} 
                        Http статус: {response.status_code} ({response.reason})""")
    companies = json_response["features"]
    return companies


def ask_for_orgs(ll, text, quantity=10):
    response = make_organization_request(ll, text, quantity)
    if response == []:
        answer = {'size': 0}
        return answer
    answer = {}
    answer['size'] = min(len(response), quantity)
    comps = []
    for comp in response:
        formatted = comp['properties']['CompanyMetaData']['name']
        if 'address' in comp['properties']['CompanyMetaData']:
            formatted += '\n' + comp['properties']['CompanyMetaData']['address']
        else:
            formatted += '\n*Адрес не найден*'
        comps.append(formatted)
    answer['orgs'] = comps
    return answer


# ll = "36.192629, 51.729312"
# text = 'аптека'
# organization_params = {
#         "apikey": API_KEY,
#         "text": 'аптека',
#         "lang": "ru_RU",
#         "type": "biz",
#         "ll": ll,
#         "results": 12,
#         "spn": "0.05, 0.05"
#     }
# print(requests.get("https://search-maps.yandex.ru/v1/", params=organization_params).json())
# print(make_organization_request(ll, text))
