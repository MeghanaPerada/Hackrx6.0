import requests
import json
import os

# Fixed city_landmarks mapping based on PDF document
city_landmarks = {
    # Indian Cities (corrected based on PDF)
    'delhi': 'gateway_of_india',
    'mumbai': ['india_gate', 'space_needle'],  # Mumbai has both landmarks
    'chennai': 'charminar',
    'hyderabad': ['marina_beach', 'taj_mahal'],  # Hyderabad has both landmarks
    'ahmedabad': 'howrah_bridge',
    'mysuru': 'golconda_fort',
    'kochi': 'qutub_minar',
    'pune': ['meenakshi_temple', 'golden_temple'],  # Pune has both landmarks
    'nagpur': 'lotus_temple',
    'chandigarh': 'mysore_palace',
    'kerala': 'rock_garden',
    'bhopal': 'victoria_memorial',
    'varanasi': 'vidhana_soudha',
    'jaisalmer': 'sun_temple',
    
    # International Cities (corrected based on PDF)
    'newyork': 'eiffel_tower',
    'london': ['statue_of_liberty', 'sydney_opera_house'],  # London has both landmarks
    'tokyo': 'big_ben',
    'beijing': 'colosseum',  # Fixed spelling from PDF
    'bangkok': 'christ_the_redeemer',
    'toronto': 'burj_khalifa',
    'dubai': 'cn_tower',
    'amsterdam': 'petronas_towers',
    'cairo': 'leaning_tower_of_pisa',
    'sanfrancisco': 'mount_fuji',
    'berlin': 'niagara_falls',
    'barcelona': 'louvre_museum',
    'moscow': 'stonehenge',
    'seoul': ['sagrada_familia', 'times_square'],  # Seoul has both landmarks
    'capetown': 'acropolis',
    'istanbul': 'big_ben',
    'riyadh': 'machu_picchu',
    'paris': 'taj_mahal',
    'dubaiairport': 'moai_statues',
    'singapore': 'christchurch_cathedral',
    'jakarta': 'the_shard',
    'vienna': 'blue_mosque',
    'kathmandu': 'neuschwanstein_castle',
    'losangeles': 'buckingham_palace'
}

def get_primary_landmark(landmarks):
    """
    For cities with multiple landmarks, determine which one to use for flight selection.
    Priority based on the flight endpoint hierarchy from the PDF.
    """
    if isinstance(landmarks, str):
        return landmarks
    
    # Priority order based on flight endpoints
    priority_order = ['gateway_of_india', 'taj_mahal', 'eiffel_tower', 'big_ben']
    
    for priority_landmark in priority_order:
        if priority_landmark in landmarks:
            return priority_landmark
    
    # If no priority landmark found, return the first one
    return landmarks[0]

def get_flight_number(endpoint_url):
    try:
        print(f"Making request to: {endpoint_url}")
        response = requests.get(endpoint_url, timeout=10)
        response.raise_for_status()
        
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text[:200]}...")
        
        # Check if response is valid JSON
        try:
            city_data = response.json()
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON from city API: {e}")
            print(f"Raw response: {response.text}")
            raise Exception(f"Invalid JSON response from city API: {response.text[:100]}")
        
        city = city_data['data']['city'].lower().replace(' ', '')
        print(f"Extracted city: {city}")
        
        landmarks = city_landmarks.get(city)
        print(f"Mapped landmarks: {landmarks}")
        
        if not landmarks:
            raise Exception(f"No landmark found for city: {city}")
        
        # Get the primary landmark for flight selection
        primary_landmark = get_primary_landmark(landmarks)
        print(f"Primary landmark for flight selection: {primary_landmark}")
        
        # Flight selection logic as per PDF
        base_url = "https://register.hackrx.in/teams/public/flights/"
        if primary_landmark == "gateway_of_india":
            flight_url = base_url + "getFirstCityFlightNumber"
        elif primary_landmark == "taj_mahal":
            flight_url = base_url + "getSecondCityFlightNumber"
        elif primary_landmark == "eiffel_tower":
            flight_url = base_url + "getThirdCityFlightNumber"
        elif primary_landmark == "big_ben":
            flight_url = base_url + "getFourthCityFlightNumber"
        else:
            flight_url = base_url + "getFifthCityFlightNumber"
        
        print(f"Making flight request to: {flight_url}")
        flight_response = requests.get(flight_url, timeout=10)
        flight_response.raise_for_status()
        
        print(f"Flight response status: {flight_response.status_code}")
        print(f"Flight response text: {flight_response.text[:200]}...")
        
        try:
            flight_data = flight_response.json()
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON from flight API: {e}")
            print(f"Raw flight response: {flight_response.text}")
            raise Exception(f"Invalid JSON response from flight API: {flight_response.text[:100]}")
        
        flight_number = flight_data['data']['flightNumber']
        
        print(f"City: {city}")
        print(f"All landmarks: {landmarks}")
        print(f"Primary landmark: {primary_landmark}")
        print(f"Flight Number: {flight_number}")
        
        return flight_number
        
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        raise Exception(f"API request failed: {e}")
    except KeyError as e:
        print(f"Key error: {e}")
        raise Exception(f"Missing expected data in API response: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise