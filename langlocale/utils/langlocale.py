import json

import requests
from dotenv import load_dotenv
import os

load_dotenv()


__API_KEY__ = os.getenv("PLACES_API_KEY")

headers = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": __API_KEY__,
    'X-Goog-FieldMask': 'places.id,places.displayName,places.location,places.photos'
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

def get_place_info(place_name):
    base_url = "https://places.googleapis.com/v1/places:searchNearby"

    data = {
        "includedTypes": TYPES,
        "maxResultCount": 1,
        "rankPreference": "DISTANCE",
        "locationRestriction": LOCATION_RESTRICTION,
    }

    response = requests.post(base_url, json=data, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return response.status_code


ans = get_place_info("640 Williams St NW")
print(ans)
