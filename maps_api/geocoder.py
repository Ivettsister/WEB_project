from maps_api.request import geocoder_request


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

    data = geocoder_request(geocode=address, lang=lang, format='json')
    components = get_components(data)
    if components is not None:
        for component in components[::-1]:
            if component['kind'] in ('province', 'locality'):
                return component['name']

    return None


def get_country_code(data):
    try:
        for i in ['response', 'GeoObjectCollection', 'featureMember',
                  0, 'GeoObject', 'metaDataProperty', 'GeocoderMetaData',
                  'Address', 'country_code']:
            data = data[i]
        return data
    except (IndexError, KeyError):
        print('aue')
        return None


def get_address(data):
    try:
        for i in ['response', 'GeoObjectCollection', 'featureMember', 0,
                  'GeoObject', 'metaDataProperty', 'GeocoderMetaData', 'text']:
            data = data[i]
        return data
    except (IndexError, KeyError):
        return None


def get_pos(data):
    pos = data
    for i in ['response', 'GeoObjectCollection', 'featureMember',
              0, 'GeoObject', 'Point', 'pos']:
        pos = pos[i]
    return list(map(float, pos.split()))


def get_bbox(data):
    envelope = data
    for i in ['response', 'GeoObjectCollection', 'featureMember',
              0, 'GeoObject', 'boundedBy', 'Envelope']:
        envelope = envelope[i]
    points = list(map(float, envelope['lowerCorner'].split())) + list(map(float, envelope['upperCorner'].split()))
    for i in range(len(points)):
        if i % 2 == 1:
            if points[i] > 90:
                points[i] = 90
            elif points[i] < -90:
                points[i] = -90
        else:
            if points[i] > 180:
                points[i] = 180
            elif points[i] < -180:
                points[i] = -180
    return points


def check_response(data):
    found = data
    for i in ['response', 'GeoObjectCollection', 'metaDataProperty', 'GeocoderResponseMetaData',
              'found']:
        found = found[i]
    print(found)
    return int(found)
