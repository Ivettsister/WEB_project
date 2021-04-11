from maps_api.request import map_request
from maps_api.geocoder import get_bbox, get_pos


def get_static_map(user_data, l='map'):
    pos = get_pos(user_data['current_response'])
    bbox = get_bbox(user_data['current_response'])
    static_map = map_request(
        ll='{},{}'.format(*pos),
        bbox='{},{}~{},{}'.format(*bbox),
        pt='{},{},pm2rdm'.format(*pos),
        l=l
    )
    return static_map
