


# Useful URLs (you need to add the appropriate parameters for your requests)
MAPBOX_BASE_URL = "https://api.mapbox.com/geocoding/v5/mapbox.places"
MBTA_BASE_URL = "https://api-v3.mbta.com/stops"
TICKETMASTER_BASE_URL = "https://app.ticketmaster.com/discovery/v2/events.json"

MAPBOX_TOKEN= 'pk.eyJ1IjoiMTA2NTA1Mjk2OSIsImEiOiJjbHVvbTZuMGkxaGtqMmxtd2EwZWt4cXg3In0.4NeXehtn1kqfXOjLzdv4pw' 
MBTA_API= '0c275e6ca55c4cc1ba807109f9a6480d'
TICKETMASTER_API_KEY = '7BOmHx1ProcU4LkGG9MAlI7Lo8hWKklE'
import json
import pprint
import urllib.request


query = 'Babson College'
query = query.replace(' ', '%20') # In URL encoding, spaces are typically replaced with "%20". You can also use urllib.parse.quote function. 
url=f'{MAPBOX_BASE_URL}/{query}.json?access_token={MAPBOX_TOKEN}&types=poi'
print(url) # Try this URL in your browser first



# A little bit of scaffolding if you want to use it

def get_json(url: str) -> dict:
    """
    Given a properly formatted URL for a JSON web API request, return a Python JSON object containing the response to that request.

    Both get_lat_lng() and get_nearest_station() might need to use this function.
    """
    with urllib.request.urlopen(url) as f:
        response_text = f.read().decode('utf-8')
        response_data = json.loads(response_text)
        pprint.pprint(response_data)
        return response_data



def get_lat_lng(place_name: str) -> tuple[str, str]:
    """
    Given a place name or address, return a (latitude, longitude) tuple with the coordinates of the given place.

    See https://docs.mapbox.com/api/search/geocoding/ for Mapbox Geocoding API URL formatting requirements.
    """
    query = place_name
    query= query.replace(' ', '%20')
    url = f"{MAPBOX_BASE_URL}/{query}.json?access_token={MAPBOX_TOKEN}&limit=1"
    response_data = get_json(url)
    if response_data['features']:
        coordinates = response_data['features'][0]['geometry']['coordinates']
        return (str(coordinates[1]), str(coordinates[0]))
    else:
        return (None, None) 

def get_nearest_station(latitude: str, longitude: str) -> tuple[str, bool]:
    """
    Given latitude and longitude strings, return a (station_name, wheelchair_accessible) tuple for the nearest MBTA station to the given coordinates.

    See https://api-v3.mbta.com/docs/swagger/index.html#/Stop/ApiWeb_StopController_index for URL formatting requirements for the 'GET /stops' API.
    """
    if latitude is None or longitude is None:
        return(None, False)
    url = f"{MBTA_BASE_URL}?api_key={MBTA_API}&filter[latitude]={latitude}&filter[longitude]={longitude}&sort=distance"

    response_data=get_json(url)
    if response_data['data']:
        station_name = response_data['data'][0]['attributes']['name']
        wheelchair_accessible = response_data['data'][0]['attributes']['wheelchair_boarding'] == 1
        return (station_name, wheelchair_accessible)
    else:
        return (None, False)




def find_stop_near(place_name: str) -> tuple[str, bool]:
    """
    Given a place name or address, return the nearest MBTA stop and whether it is wheelchair accessible.

    This function might use all the functions above.
    """
    lat = get_lat_lng(place_name)[0]
    lng = get_lat_lng(place_name)[1]
    if lat and lng:
        return get_nearest_station(lat, lng)
    else:
        return ("No no nearest station found", False)

def get_events (latitude: str, longitude: str, radius: int = 10) -> list:
    url = f"{TICKETMASTER_BASE_URL}?apikey={TICKETMASTER_API_KEY}&geoPoint={latitude},{longitude}&radius={radius}&unit=miles"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            events = data['_embedded']['events'] if '_embedded' in data else []
            return events
    except Exception as e:
        print(f"Error fetching events from Ticketmaster: {e}")
        return []
    
def main():
    """
    Test all the above functions here.
    """
    place_name = "Kendall Square, Cambridge, MA"
    station_name, wheelchair_accessible = find_stop_near(place_name)
    latitude, longitude = get_lat_lng(place_name)
    events = get_events(latitude, longitude)
    print(f"Nearest MBTA stop to '{place_name}':")
    pprint.pprint({ 'Events': events,
        'Station Name': station_name,
        'Wheelchair Accessible': wheelchair_accessible 
    })


if __name__ == '__main__':
    main()
