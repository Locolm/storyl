from datetime import datetime
import json
import os
import re
import context

# Variables globales pour l'heure de la journée
CURRENT_HOUR = 0
TIME_OF_DAY = ""
HOURS_PLAYED = 0

def update_time_of_day():
    """
    Met à jour la variable TIME_OF_DAY en fonction de l'heure actuelle.
    """
    global CURRENT_HOUR, TIME_OF_DAY
    
    if 5 <= CURRENT_HOUR < 12:
        TIME_OF_DAY = "matin"
    elif 12 <= CURRENT_HOUR < 18:
        TIME_OF_DAY = "après-midi"
    elif 18 <= CURRENT_HOUR < 22:
        TIME_OF_DAY = "soir"
    else:
        TIME_OF_DAY = "nuit"
    return TIME_OF_DAY

def advance_time(n):
    try:
        n = int(float(n))
        if n < 0:
            n = -n
        elif n == 0:
            return "Le temps n'a pas avancé."
    except ValueError:
        n = 1

    global CURRENT_HOUR
    CURRENT_HOUR = (CURRENT_HOUR + n) % 24
    HOURS_PLAYED += n
    update_time_of_day()

    #update pnj routines
    update_pnj_routines()

    #update characters
    characters_dir = 'characters'
    
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
                    else:
                        data['etat']["déplacement"] = f"en déplacement vers ({destination_x}, {destination_y}) reste {remaining_hours} heures"
             
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
    return f"Le temps a avancé de {n} heures, il est {CURRENT_HOUR} heures."


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
            
            if HOURS_PLAYED % routine_time == 0:
                context.update_pnj_routine(pnj_name)