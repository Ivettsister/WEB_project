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
        return None
    companies = json_response["features"]
    return companies


def ask_for_orgs(ll, text, quantity=10):
    response = make_organization_request(ll, text, quantity)
    if response is None:
        return None
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
