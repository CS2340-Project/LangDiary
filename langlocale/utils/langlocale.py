import json

import requests
from dotenv import load_dotenv
import os

load_dotenv()


__API_KEY__ = os.getenv("PLACES_API_KEY")
headers = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": __API_KEY__,
    'X-Goog-FieldMask': 'places.id,places.displayName,places.location,places.photos,places.editorialSummary'
}

TYPES = ["library", "museum", "restaurant", "tourist_attraction"]

LOCATION_RESTRICTION = {
    "circle": {
        "center": {
            "latitude": 33.7756,
            "longitude": -84.3963,
        },
        "radius": 5000.0
    }
}

QUERY = ""

def get_photo_from_place(response):
    photo_name = response['photos'][0]['name'].split('/photos/')[-1]
    base_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={photo_name}&key={__API_KEY__}"
    return base_url

def get_coordinates_for_place_id(place_id):
    details_url = f"https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "geometry",
        "key": __API_KEY__
    }
    response = requests.get(details_url, params=params)
    if response.status_code == 200:
        data = response.json()
        location = data.get("result", {}).get("geometry", {}).get("location", {})
        lat = location.get("lat")
        lng = location.get("lng")
        if lat and lng:
            return f"{lat},{lng}"
    return "nothing" 

def get_place_info(place_name):
    base_url = "https://places.googleapis.com/v1/places:searchNearby"

    data = {
        "includedTypes": TYPES,
        "rankPreference": "DISTANCE",
        "locationRestriction": LOCATION_RESTRICTION,
    }

    response = requests.post(base_url, json=data, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return response.status_code


def prepare_info_for_rendering(ans):
    response = []
    for place in ans['places']:
        maps_url = f"https://www.google.com/maps/place/?q=place_id:{place['id']}"
        response.append({
            "imageUrl": get_photo_from_place(place),
            "name": place["displayName"]["text"],
            "mapsUrl": maps_url,
            "id": place['id'],
            "loc": get_coordinates_for_place_id(place["id"])
        })
    return response

def get_data():
    ans = prepare_info_for_rendering(get_place_info("640 Williams St NW"))
    return ans