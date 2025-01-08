import json
import math
import os
from math import sqrt, floor

import llm
import re

# Charger un fichier JSON spécifique
def load_json(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def get_character_position(name):
    file_path = f'characters/characters_{name}.json'
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    if 'position' not in data or 'x' not in data['position'] or 'y' not in data['position']:
        raise KeyError("The JSON file does not contain 'position' key with 'x' or 'y' keys.")
    
    return data['position']['x'], data['position']['y']

# Example usage:
# x, y = get_character_position('Tenzin le fort')
# print(f"Position: x={x}, y={y}")

def get_location_position(name):
    file_path = f'locations/locations_{name}.json'
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    if 'position' not in data or 'x' not in data['position'] or 'y' not in data['position']:
        raise KeyError("The JSON file does not contain 'position' key with 'x' or 'y' keys.")
    
    return data['position']['x'], data['position']['y']

# Example usage:
# x, y = get_location_position('L\'Atelier des Elixirs_1')
# print(f"Position: x={x}, y={y}")

def get_item_from_location(location_name, item_name, item_type):
    if item_type not in ['monster', 'object']:
        raise ValueError("item_type must be either 'monster' or 'object'")
    
    file_path = f'locations/locations_{location_name}.json'
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    if item_type == 'monster':
        if 'monstres' not in data:
            raise KeyError("The JSON file does not contain 'monstres' key.")
        for monster in data['monstres']:
            if monster['nom'] == item_name:
                return monster
    
    if item_type == 'object':
        if 'objets' not in data:
            raise KeyError("The JSON file does not contain 'objets' key.")
        for obj in data['objets']:
            if obj['nom'] == item_name:
                return obj
    
    raise ValueError(f"{item_type.capitalize()} named {item_name} not found in location {location_name}.")

# Example usage:
# monster = get_item_from_location('Labyrinthe des Ombres', 'Golem de l\'ombre', 'monster')
# print(monster)
# obj = get_item_from_location('Labyrinthe des Ombres', 'Lanternes anciennes', 'object')
# print(obj)


#give speed_m_s by calling llm.response("/speed /tenzin le fort/") => give etat du character to the llm and return speed_m_s
def get_travel_time(x1, y1, x2, y2, speed_m_s):

    #llm.completion(f"/speed /tenzin le fort/") => give speed_m_s and x1, y1
    # Calculate the distance in kilometers
    distance_km = sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    # Convert speed from m/s to km/h
    speed_kmh = speed_m_s * 3.6
    
    # Calculate travel time in hours
    travel_time_hours = math.floor(distance_km / speed_kmh)
    # Return the travel time
    if travel_time_hours < 1:
        return 0
    return travel_time_hours

# Example usage:
# time = get_travel_time(0, 0, 18, 0, 3)
# print(f"Travel time: {time} hours")

def update_character_state_with_travel_time(character_name, speed_m_s, destination_x, destination_y):
    # Get the current position of the character
    x, y = get_character_position(character_name)
    
    # Calculate the travel time
    travel_time_hours = get_travel_time(x, y, destination_x, destination_y, speed_m_s)
    print(travel_time_hours)
    
    # Load the character's JSON file
    file_path = f'characters/characters_{character_name}.json'
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # Update the character's state
    if 'etat' in data and data["etat"]["déplacement"].startswith("en déplacement"):
        # Remove existing "en déplacement" state
        data['etat']["déplacement"] = re.sub(r"en déplacement vers \(\d+, \d+\) reste \d+ heures", "", data['etat']["déplacement"]).strip()
    
    if travel_time_hours != 0:
        data['etat']["déplacement"] = f"en déplacement vers ({destination_x}, {destination_y}) reste {travel_time_hours} heures".strip()
    
    # Save the updated JSON file
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

# Example usage:
# update_character_state_with_travel_time('Tenzin le fort', 4, 18, 0)

def is_moving(character_name):
    # Load the character's JSON file
    file_path = f'characters/characters_{character_name}.json'
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Check if the character's state contains "en déplacement" and if it is not empty
    if 'etat' in data and data["etat"]["déplacement"].startswith("en déplacement"):
        return True
    
    return False

# Example usage:
# moving = is_moving('Tenzin le fort')
# print(f"Is moving: {moving}")

def get_nearby_locations(x,y, radius_km=10):
    
    nearby_locations = []
    locations_dir = 'locations'
    
    # Iterate over all location files in the locations directory
    for filename in os.listdir(locations_dir):
        if filename.endswith('.json'):
            location_name = filename[len('locations_'):-len('.json')]
            loc_x, loc_y = get_location_position(location_name)
            
            # Calculate the distance to the location
            distance_km = sqrt((loc_x - x)**2 + (loc_y - y)**2)
            
            # Check if the location is within the specified radius
            if distance_km <= radius_km:
                nearby_locations.append(location_name)
    
    return json.dumps(nearby_locations, ensure_ascii=False, indent=4)

# Example usage:
# nearby = get_nearby_locations(12, 5)
# print(nearby)


def update_character_position(character_name, new_x, new_y):
    # Load the character's JSON file
    file_path = f'characters/characters_{character_name}.json'
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # Update the character's position
    if 'position' not in data:
        data['position'] = {}
    data['position']['x'] = new_x
    data['position']['y'] = new_y
    
    # Save the updated JSON file
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

# Example usage:
# update_character_position('Tenzin le fort', 15, 25)


def check_location_exists(x, y):
    matching_locations = []
    locations_dir = 'locations'
    
    # Iterate over all location files in the locations directory
    for filename in os.listdir(locations_dir):
        if filename.endswith('.json'):
            # Extract the location name, handling both formats
            location_name = '_'.join(filename.split('_')[1:]).split('.')[0]
            loc_x, loc_y = get_location_position(location_name)
            
            # Check if the location matches the given coordinates
            if loc_x == x and loc_y == y:
                matching_locations.append(location_name)
    
    return matching_locations

# Example usage:
# locations = check_location_exists(12, 5)
# print(locations)

def moving_character_to_location(character_name, location_name, speed_m_s=2):
    # Check if the character is already moving
    if is_moving(character_name):
        return "Impossible, le personnage est déjà en déplacement."
    
    # Get the destination location's position
    destination_x, destination_y = get_location_position(location_name)
    
    # Update the character's state with the travel time to the destination
    update_character_state_with_travel_time(character_name, speed_m_s, destination_x, destination_y)
    
    return f"Le personnage {character_name} est maintenant en déplacement vers {location_name}."

# Example usage:
# result = moving_character_to_location('Tenzin le fort', 'L\'Atelier des Elixirs', 2)
# print(result)

def is_sleeping(character_name):
    # Load the character's JSON file
    file_path = f'characters/characters_{character_name}.json'
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # Check if the character's state contains "en train de dormir"
    if 'etat' in data and 'sommeil' in data['etat']:
        match = re.search(r"en train de dormir reste (\d+) heures", data['etat']['sommeil'])
        if match:
            return int(match.group(1))
    
    return 0

# Example usage:
# sleep_hours = is_sleeping('Tenzin le fort')
# print(f"Sleeping hours remaining: {sleep_hours}")

def update_character_state_with_sleep(character_name, sleep_hours):
    number = is_sleeping(character_name)
    if number > 0:
        return f"Le personnage est déjà en train de dormir, reste {number} heures."

    try:
        sleep_hours = int(float(sleep_hours))
        if sleep_hours < 0:
            sleep_hours = 0
        elif sleep_hours == 0:
            sleep_hours = 8
    except ValueError:
        sleep_hours = 8

    # Load the character's JSON file
    file_path = f'characters/characters_{character_name}.json'
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # Update the character's state
    if 'etat' in data:
        if data['etat'].get('déplacement')=="non":
            # Extract the remaining hours of travel
            match = re.search(r"en déplacement vers \((\d+), (\d+)\) reste (\d+) heures", data['etat']['déplacement'])
            if match:
                destination_x, destination_y, remaining_hours = map(int, match.groups())
                remaining_hours = max(0, remaining_hours + sleep_hours)
            data['etat']['déplacement'] = f"en déplacement vers ({destination_x}, {destination_y}) reste {remaining_hours} heures"
        
        # Replace the sleep state
        data['etat']['sommeil'] = f"en train de dormir reste {sleep_hours} heures"
        
        # Save the updated JSON file
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        return f"Le personnage {character_name} est en train de dormir reste {sleep_hours} heures."

# Example usage:
# print(update_character_state_with_sleep('Tenzin le fort', 8))
