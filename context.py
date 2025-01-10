import json
import math
import os
from math import sqrt, floor

import llm
import re

# Charger un fichier JSON spécifique
def load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def get_character_position(name):
    file_path = f'characters/characters_{name}.json'
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    with open(file_path, 'r', encoding='utf-8') as file:
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
    
    with open(file_path, 'r', encoding='utf-8') as file:
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
    
    with open(file_path, 'r', encoding='utf-8') as file:
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
    
    return nearby_locations

# Example usage:
# nearby = get_nearby_locations(42, 17)
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
# locations = check_location_exists(42, 17)
# print(locations)

def moving_character_to_location(character_name, location_name, speed_m_s=2):
    try:
        speed_m_s = int(float(speed_m_s))
    except ValueError:
        speed_m_s = 2

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
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # Check if the character's state contains "en train de dormir"
    if 'etat' in data and 'sommeil' in data['etat']:
        match = re.search(r"en train de dormir reste (\d+) heures", data['etat']['sommeil'])
        if match:
            return int(match.group(1))
    
    return 0

# Example usage:
# sleep_hours = is_sleeping('Tenzin le Fort')
# print(f"Sleeping hours remaining: {sleep_hours}")

def update_character_state_with_sleep(character_name, sleep_hours):
    number = is_sleeping(character_name)
    if number > 0:
        return f"{character_name} est déjà en train de dormir, reste {number} heures."

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
    
    # Check if the character's state contains "en forme", "fatigué", or "épuisé"
    if 'etat' in data:
        if data['etat']["sommeil"] == "en forme" and sleep_hours < 2:
            sleep_hours = 2
        elif data['etat']["sommeil"] == "fatigué" and sleep_hours < 7:
            sleep_hours = 7
        elif data['etat']["sommeil"] == "épuisé" and sleep_hours < 9:
            sleep_hours = 9
        elif data['etat']["sommeil"] == "nuit blanche" and sleep_hours < 12:
            sleep_hours = 12

    # Replace the sleep state
    data['etat']['sommeil'] = f"en train de dormir reste {sleep_hours} heures"
    # Update the character's state
    if 'etat' in data:
        if data['etat']['déplacement']!="non":
            # Extract the remaining hours of travel
            match = re.search(r"en déplacement vers \((\d+), (\d+)\) reste (\d+) heures", data['etat']['déplacement'])
            if match:
                destination_x, destination_y, remaining_hours = map(int, match.groups())
                remaining_hours = remaining_hours + sleep_hours
                data['etat']['déplacement'] = f"en déplacement vers ({destination_x}, {destination_y}) reste {remaining_hours} heures"

        # Save the updated JSON file
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        return f"Le personnage {character_name} est en train de dormir reste {sleep_hours} heures."

# Example usage:
# print(update_character_state_with_sleep('Tenzin le fort', 8))

def get_location_name(x, y):
    locations_dir = 'locations'
    
    # Iterate over all location files in the locations directory
    for filename in os.listdir(locations_dir):
        if filename.endswith('.json'):
            location_name = filename[len('locations_'):-len('.json')]
            loc_x, loc_y = get_location_position(location_name)
            
            # Check if the coordinates match
            if loc_x == x and loc_y == y:
                return location_name
    
    raise ValueError(f"No location found with coordinates x={x}, y={y}")

# Example usage:
# location_name = get_location_name(42, 17)
# print(location_name)

def update_all_pnj_routines():
    # Implement the function to update PNJ routines
    # For now, let's just return a message indicating the function was called
    pnjs_dir = 'pnjs'
    
    # Iterate over all PNJ files in the pnjs directory
    for filename in os.listdir(pnjs_dir):
        if filename.endswith('.json'):
            pnj_name = filename[len('pnjs_'):-len('.json')]
            file_path = os.path.join(pnjs_dir, filename)
            
            # Load the PNJ's JSON file
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            if 'position' in data:
                loc_x, loc_y = data['position']['x'], data['position']['y']
                location_name = get_location_name(loc_x, loc_y)
                
                # Find the index of the current location in the PNJ's routine
                if 'routine' in data and 'locations' in data['routine']:
                    locations = data['routine']['locations']
                    if location_name in locations:
                        current_index = locations.index(location_name)
                        next_index = (current_index + 1) % len(locations)
                        next_location_name = locations[next_index]
                        
                        # Get the position of the next location
                        next_loc_x, next_loc_y = get_location_position(next_location_name)
                        
                        # Update the PNJ's position to the next location's position
                        data['position']['x'] = next_loc_x
                        data['position']['y'] = next_loc_y

            
            # Save the updated JSON file
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

# Example usage:
# result = update_all_pnj_routines()
# print(result)

def update_pnj_routine(pnj_name):
    pnjs_dir = 'pnjs'
    file_path = os.path.join(pnjs_dir, f'pnjs_{pnj_name}.json')
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    # Load the PNJ's JSON file
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    if 'position' in data:
        loc_x, loc_y = data['position']['x'], data['position']['y']
        location_name = get_location_name(loc_x, loc_y)
        
        # Find the index of the current location in the PNJ's routine
        if 'routine' in data and 'locations' in data['routine']:
            locations = data['routine']['locations']
            if location_name in locations:
                current_index = locations.index(location_name)
                next_index = (current_index + 1) % len(locations)
                next_location_name = locations[next_index]
                
                # Get the position of the next location
                next_loc_x, next_loc_y = get_location_position(next_location_name)
                
                # Update the PNJ's position to the next location's position
                data['position']['x'] = next_loc_x
                data['position']['y'] = next_loc_y
    
    # Save the updated JSON file
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

# Example usage:
# update_pnj_routine('test')

def get_all_pnj_routine_times():
    pnjs_dir = 'pnjs'
    pnj_routine_times = {}

    # Iterate over all PNJ files in the pnjs directory
    for filename in os.listdir(pnjs_dir):
        if filename.endswith('.json'):
            pnj_name = filename[len('pnjs_'):-len('.json')]
            file_path = os.path.join(pnjs_dir, filename)
            
            # Load the PNJ's JSON file
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            if 'routine' in data and 'time' in data['routine']:
                pnj_routine_times[pnj_name] = data['routine']['time']
    
    return pnj_routine_times

# Example usage:
# routine_times = get_all_pnj_routine_times()
# print(routine_times)

def get_pnj_routine_time(pnj_name):
    pnjs_dir = 'pnjs'
    file_path = os.path.join(pnjs_dir, f'pnjs_{pnj_name}.json')
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    # Load the PNJ's JSON file
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    if 'routine' in data and 'time' in data['routine'] and data['etat']['humeur'] != 'mort' and data['etat']['humeur'] != 'morte':
        return data['routine']['time']
    
    raise KeyError(f"No routine time found for PNJ {pnj_name}")

# Example usage:
# routine_time = get_pnj_routine_time('test')
# print(routine_time)

def get_arrival_descriptions(destination_arrived):
    descriptions = []
    
    for destination in destination_arrived:
        location_name = destination['nom']
        characters = destination['characters']
        
        # Load the location's JSON file
        file_path = f'locations/locations_{location_name}.json'
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        if 'description' not in data:
            raise KeyError(f"The JSON file for location {location_name} does not contain 'description' key.")
        
        description_location = data['description']
        character_names = ', '.join(characters)
        
        if len(characters) > 1:
            arrival_text = f"{character_names} sont arrivés à {location_name}, {description_location}"
        else:
            arrival_text = f"{character_names} est arrivé à {location_name}, {description_location}"
        
        descriptions.append(arrival_text)
    
    return '\n\n'.join(descriptions)

# Example usage:
# destination_arrived = [{'nom': 'L\'Atelier des Elixirs', 'characters': ['Tenzin le fort', 'Lara la sage']}, {'nom': 'Labyrinthe des ombres', 'characters': ['Tenzin le fort', 'Lara la sage']}]
# print(get_arrival_descriptions(destination_arrived))

def get_locations_with_monsters(destination_arrived):
    locations_with_monsters = []
    
    for destination in destination_arrived:
        location_name = destination['nom']
        
        # Load the location's JSON file
        file_path = f'locations/locations_{location_name}.json'
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        if 'monstres' in data and data['monstres']:
            locations_with_monsters.append(location_name)
    
    return locations_with_monsters

# Example usage:
# destination_arrived = [{'nom': 'Temple de la Lumière Éternelle', 'characters': ['Tenzin le fort', 'Lara la sage']},{'nom': 'L\'Atelier des Elixirs', 'characters': ['Tenzin le fort', 'Lara la sage']}, {'nom': 'Labyrinthe des ombres', 'characters': ['Tenzin le fort', 'Lara la sage']}]
# print(get_locations_with_monsters(destination_arrived))

def get_pnjs_in_location(location_name):
    pnjs_in_location = []
    pnjs_dir = 'pnjs'
    
    # Get the position of the location
    loc_x, loc_y = get_location_position(location_name)
    
    # Iterate over all PNJ files in the pnjs directory
    for filename in os.listdir(pnjs_dir):
        if filename.endswith('.json'):
            pnj_name = filename[len('pnjs_'):-len('.json')]
            file_path = os.path.join(pnjs_dir, filename)
            
            # Load the PNJ's JSON file
            pnj_data = load_json(file_path)
            
            if pnj_data and 'position' in pnj_data:
                pnj_x, pnj_y = pnj_data['position']['x'], pnj_data['position']['y']
                
                # Check if the PNJ's position matches the location's position
                if pnj_x == loc_x and pnj_y == loc_y:
                    pnjs_in_location.append(pnj_data)
    
    return json.dumps(pnjs_in_location, ensure_ascii=False)

# Example usage:
# pnjs = get_pnjs_in_location('test')
# print(pnjs)


def parse_json_input(json_input):
    character = json_input.get('character', {})
    pnjs = json_input.get('pnjs', [])
    locations = json_input.get('locations', [])
    
    return character, pnjs, locations

# Example usage:
# json_input = {'description': "Tenzin le Fort utilise son charisme pour convaincre l'alchimiste de lui vendre une potion de soin à un prix réduit. L'alchimiste, charmé par la présence imposante de Tenzin, accepte de la vendre pour 10 pièces d'or.", 'character': {'inventaire': ['Bâton de bois', 'Amulette de protection', 'Potion de soins', 'Sandales légères', 'Potion de soin'], 'or': 40}, 'pnjs': [], 'locations': [{'nom': 'Potion de soin', 'prix': 15}, {'nom': 'Elixir de force', 'prix': 25}, {'nom': "Poudre d'invisibilité", 'prix': 50}, {'nom': 'Herbes médicinales', 'prix': 5}, {'nom': 'Flacon vide', 'prix': 2}]}
# character, pnjs, locations = parse_json_input(json_input)
# print(character)
# print(pnjs)
# print(locations)

def update_character_from_json(input_json):
    if not input_json:
        raise ValueError("Input JSON is null, invalid, or empty.")
    
    if 'nom' not in input_json:
        raise KeyError("Input JSON does not contain 'nom' key.")
    
    character_name = input_json['nom']
    
    # Load the character's JSON file
    file_path = f'characters/characters_{character_name}.json'
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        character_data = json.load(file)
    
    # Update the character's inventory, gold, and health state if they exist in the input JSON
    if 'inventaire' in input_json:
        character_data['inventaire'] = input_json['inventaire']

    if 'or' in input_json:
        character_data['or'] = input_json['or']

    if 'santé' in input_json:
        character_data['etat']["santé"] = input_json['santé']
    
    # Save the updated JSON file
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(character_data, file, indent=4, ensure_ascii=False)

# Example usage:
# input_json = {'nom': 'Tenzin le fort', 'inventaire': ['Épée en fer', 'Bouclier en bois'], 'or': 100, 'etat': {'santé': 'bonne'}}
# update_character_from_json(input_json)

def update_location_from_json(input_json):
    if not input_json:
        raise ValueError("Input JSON is null, invalid, or empty.")
    
    if 'nom' not in input_json or 'objets' not in input_json:
        raise KeyError("Input JSON does not contain 'nom' or 'objets' key.")
    
    location_name = input_json['nom']
    new_objects = input_json['objets']
    
    # Load the location's JSON file
    file_path = f'locations/locations_{location_name}.json'
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        location_data = json.load(file)
    
    # Update the location's objects
    location_data['objets'] = new_objects
    
    # Save the updated JSON file
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(location_data, file, indent=4, ensure_ascii=False)

# Example usage:
# input_json = {'nom': 'L\'Atelier des Elixirs_1', 'objets': [{'nom': 'Potion de soin', 'prix': 15}, {'nom': 'Elixir de force', 'prix': 25}]}
# update_location_from_json(input_json)

def update_pnj_from_json(input_json, location_name):
    if not input_json:
        raise ValueError("Input JSON is null, invalid, or empty.")
    
    if 'nom' not in input_json:
        raise KeyError("Input JSON does not contain 'nom' key.")
    
    pnj_name = input_json['nom']
    file_path = f'pnjs/pnjs_{pnj_name}.json'
    
    # Load the PNJ's JSON file if it exists, otherwise create a new one
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            pnj_data = json.load(file)
    else:
        loc_x, loc_y = get_location_position(location_name)
        pnj_data = {
            "nom": pnj_name,
            "description": "un pnj",
            "etat": {
                "santé": "en bonne santé",
                "humeur": "neutre"
            },
            "routine": {
                "time":8,
                "locations": [location_name]
            },
            "position": {
                "x": loc_x,
                "y": loc_y
            }
        }

        if 'puissance' in input_json:
            pnj_data['etat']['puissance'] = input_json['puissance']
        else :
            pnj_data['etat']['puissance'] = 5
    
    # Update the PNJ's fields
    if 'inventaire' in input_json:
        pnj_data['inventaire'] = input_json['inventaire']
    
    if 'or' in input_json:
        pnj_data['or'] = input_json['or']
    
    if 'humeur' in input_json:
        pnj_data['etat']['humeur'] = input_json['humeur']
    
    # Save the updated JSON file
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(pnj_data, file, indent=4, ensure_ascii=False)

# Example usage:
# input_json = {'nom': 'Alchimiste', 'inventaire': ['Potion de soin', 'Elixir de force', "Poudre d'invisibilité", 'Herbes médicinales', 'Flacon vide', 'cristal de clairvoyance'], 'or': 40, 'humeur': "joyeux"}
# update_pnj_from_json(input_json, 'L\'Atelier des Elixirs')

def update_pnjs_from_json(pnjs_json, location_name):
    for pnj_json in pnjs_json:
        update_pnj_from_json(pnj_json, location_name)

def process_actions(json_input):
    if not json_input:
        raise ValueError("Input JSON is null, invalid, or empty.")
    
    if 'character' not in json_input or 'pnjs' not in json_input or 'locations' not in json_input:
        raise KeyError("Input JSON does not contain 'character', 'pnjs', or 'locations' key.")
    
    character_data = json_input['character']
    pnjs_data = json_input['pnjs']
    location_data = json_input['locations']
    
    # Update character
    update_character_from_json(character_data)
    
    # Update location
    update_location_from_json(location_data)
    
    # Update PNJ
    update_pnjs_from_json(pnjs_data, location_data['nom'])

# Example usage:
# json_input = {'description': "Tenzin le Fort s'approche de l'alchimiste avec un sourire chaleureux, lui faisant des compliments sur sa beauté. L'alchimiste, flatté, accepte de lui vendre une potion de soin pour 10 pièces d'or au lieu de 15. Tenzin, n'ayant pas d'or, doit renoncer à l'achat.", 'character': {'nom': 'Tenzin le Fort', 'inventaire': ['Bâton de bois', 'Amulette de protection', 'Potion de soins', 'Sandales légères', 'Potion de soin', 'Potion de soin', 'Potion de soin'], 'or': 0, 'etat': {}}, 'pnjs': [{'nom': 'Alchimiste', 'inventaire': ['Potion de soin', 'Elixir de force', "Poudre d'invisibilité", 'Herbes médicinales', 'Flacon vide'], 'or': 25, 'humeur': 'flatté', 'puissance': 5}], 'locations': {'nom': "L'Atelier des Elixirs_1", 'objets': [{'nom': 'Potion de soin', 'prix': 15}, {'nom': 'Elixir de force', 'prix': 25}, {'nom': "Poudre d'invisibilité", 'prix': 50}, {'nom': 'Herbes médicinales', 'prix': 5}, {'nom': 'Flacon vide', 'prix': 2}]}}
# process_actions(json_input)