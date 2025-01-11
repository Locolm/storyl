import json
import os
import re

from packages import context


# Variables globales pour l'heure de la journée

def update_time_of_day():
    """
    Met à jour la variable TIME_OF_DAY en fonction de l'heure actuelle.
    """
    CURRENT_HOUR = get_const_value("CURRENT_HOUR")
    TIME_OF_DAY = get_const_value("TIME_OF_DAY")
    NEW_TIME_OF_DAY = "matin"
    if 5 <= CURRENT_HOUR < 12:
        NEW_TIME_OF_DAY = "matin"
        update_const_value("TIME_OF_DAY",NEW_TIME_OF_DAY)
    elif 12 <= CURRENT_HOUR < 18:
        NEW_TIME_OF_DAY = "après-midi"
        update_const_value("TIME_OF_DAY",NEW_TIME_OF_DAY)
    elif 18 <= CURRENT_HOUR < 22:
        NEW_TIME_OF_DAY = "soir"
        update_const_value("TIME_OF_DAY",NEW_TIME_OF_DAY)
    else:
        NEW_TIME_OF_DAY = "nuit"
        update_const_value("TIME_OF_DAY",NEW_TIME_OF_DAY)

    if TIME_OF_DAY != NEW_TIME_OF_DAY:
        return True
    return False

def advance_time(n):
    try:
        n = int(float(n))
        if n < 0:
            n = -n
        elif n == 0:
            return "Le temps n'a pas avancé."
    except ValueError:
        n = 1

    CURRENT_HOUR = (get_const_value("CURRENT_HOUR") + n) % 24
    update_const_value("CURRENT_HOUR", CURRENT_HOUR)
    update_const_value("HOURS_PLAYED", get_const_value("HOURS_PLAYED") + n)
    if (update_time_of_day()):
        next_all_state()

    #update pnj routines
    update_pnj_routines()

    #update characters
    update_sleep_status(n)
    
    characters_dir = 'characters'

    #destination_arrived = [{nom:nom_destination,characters:[]},.....]
    destination_arrived = []
    for filename in os.listdir(characters_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(characters_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            if 'etat' in data and data["etat"]["déplacement"] != "non":
                match = re.search(r"en déplacement vers \((\d+), (\d+)\) reste (\d+) heures", data['etat']["déplacement"])
                if match:
                    destination_x, destination_y, remaining_hours = map(int, match.groups())
                    remaining_hours = max(0, remaining_hours - n)
                    if remaining_hours == 0:
                        data['etat']["déplacement"] = "non"
                        data['position'] = {'x': destination_x, 'y': destination_y}
                        
                        location_name = context.get_location_name(destination_x, destination_y)
                        found = False
                        for destination in destination_arrived:
                            if destination[0] == location_name:
                                destination[1].append(filename.replace('.json', '').replace('characters_', ''))
                                found = True
                                break
                        if not found:
                            destination_arrived.append({
                                "nom": location_name,
                                "characters": [filename.replace('.json', '').replace('characters_', '')]
                            })
                    else:
                        data['etat']["déplacement"] = f"en déplacement vers ({destination_x}, {destination_y}) reste {remaining_hours} heures"
             
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
    return destination_arrived


def update_pnj_routines():
    pnjs_dir = 'pnjs'
    
    for filename in os.listdir(pnjs_dir):
        if filename.endswith('.json'):
            pnj_name = filename.replace('pnjs_', '').replace('.json', '')
            try:
                routine_time = context.get_pnj_routine_time(pnj_name)
                if routine_time == 0:
                    routine_time = 8
            except Exception:
                routine_time = 8
            
            if get_const_value("HOURS_PLAYED") % routine_time == 0:
                context.update_pnj_routine(pnj_name)


def update_sleep_status(n):
    characters_dir = 'characters'
    for filename in os.listdir(characters_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(characters_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            if 'etat' in data and 'sommeil' in data['etat']:
                match = re.search(r"en train de dormir reste (\d+) heures", data['etat']['sommeil'])
                if match:
                    remaining_hours = int(match.group(1))
                    remaining_hours = max(0, remaining_hours - n)
                    if remaining_hours == 0:
                        data['etat']['sommeil'] = "reposé"
                    else:
                        data['etat']['sommeil'] = f"en train de dormir reste {remaining_hours} heures"
            
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)


def get_const_value(key):
    const_file = '../../CONST.json'
    if not os.path.exists(const_file):
        return None
    
    with open(const_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    return data.get(key, None)

def update_const_value(key, value):
    const_file = '../../CONST.json'
    if not os.path.exists(const_file):
        data = {}
    else:
        with open(const_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
    
    data[key] = value
    
    with open(const_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def next_all_state():
    characters_dir = 'characters'
    for filename in os.listdir(characters_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(characters_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            if 'etat' in data and 'sommeil' in data['etat']:
                if data['etat']['sommeil'].startswith("en train de dormir"):
                    continue
                elif data['etat']['sommeil'] == "reposé":
                    data['etat']['sommeil'] = "en forme"
                elif data['etat']['sommeil'] == "en forme":
                    data['etat']['sommeil'] = "fatigué"
                elif data['etat']['sommeil'] == "fatigué":
                    data['etat']['sommeil'] = "épuisé"
                elif data['etat']['sommeil'] == "épuisé":
                    data['etat']['sommeil'] = "nuit blanche"
            
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

