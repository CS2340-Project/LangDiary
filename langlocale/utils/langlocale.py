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

def get_place_info(place_name):
    base_url = "https://places.googleapis.com/v1/places:searchNearby"

    data = {
        "includedTypes": TYPES,
        "maxResultCount": 3,
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
        response.append({
            "imageUrl": get_photo_from_place(place),
            "name": place["displayName"]["text"],
        })
    return response

def get_data():
    ans = prepare_info_for_rendering(get_place_info("640 Williams St NW"))
    return ans