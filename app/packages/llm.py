import re
import openai

from packages import context, util
import json
import os
import time_of_day

# Remplacez "YOUR_API_KEY" par votre clé API OpenAI : # Remplacez par votre clé API OpenAI accessible ici https://platform.openai.com/settings/organization/api-keys
openai.api_key = "YOUR_API_KEY"
count_time = 0

# Fonction pour générer un personnage
def response(prompt, purpose, tokens=300, temp=0.7, ):
    try:
       
        # Appel à l'API OpenAI avec la nouvelle méthode
        content = purpose
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Modèle utilisé : mettre gpt-4o-mini
            messages=[
                {"role": "system", "content": content},
                {"role": "user", "content": prompt}
            ],
            max_tokens=tokens,  # Limite de tokens pour la réponse
            temperature=temp  # Réglage de la créativité
        )
        
        # Extraire la réponse textuelle (modification de la manière d'accéder aux données)
        content = response.choices[0].message.content

        # Nettoyer la réponse pour enlever d'éventuels espaces supplémentaires
        content = content.strip()

        # Retourner la réponse nettoyée
        return content
    except Exception as e:
        return f"Une erreur s'est produite : {e}"

def completion(prompt):
    global count_time
    type = "stop"
    if (count_time>=20):
        completion("""/time 1""")
        count_time=0

    #prompt = """/move-to /Tenzin le fort/ /x/ /y/ Créer un donjon labyrinthe."""
    #prompt = """/create-char Un moine musclé dont la force incroyable est déployée à travers des techniques martiales ancestrales."""
    #prompt = """/action /Tenzin le fort/ donner un coup d'épée au goblin devant lui. /TODO context json à définir avec character_name et position => lieux où il se trouve/"""
    #prompt = """/speed /Tenzin le fort/ /TODO context json à définir avec character_name/"""
    #prompt = """/time 1"""
    #prompt = """/create-pnj /location_name/"""
    #prompt = """/sleep /Tenzin le fort/ 7""""
    #prompt = """/create-char Un moine musclé dont la force incroyable est déployée à travers des techniques martiales ancestrales."""


    #repérer la commande
    _response = "command not recognized"
    if prompt.startswith("/create-char"):
        type = "characters"
        prompt = """Créer un personnage avec cette description :"""+prompt.replace("/create-char", "").strip() + """"Répondez sous la forme d'un JSON contenant les champs suivants : nom, force, dextérité, constitution, sagesse, intelligence, charisme, pv, etat : [santé :en bonne santé, sommeil: reposé, déplacement: non], description, inventaire (liste), or et position (coordonnées x=0 et y=0)."""
    elif prompt.startswith("/move-to"):
        character_name = prompt.split("/")[2].strip()
        if not context.is_moving(character_name):
            try:
                parts = prompt.split("/")
                if len(parts) > 3:
                    x = int(float(parts[3].strip()))
                    y = int(float(parts[4].strip()))
                else:
                    x, y = context.get_character_position(character_name)
            except ValueError:
                x, y = context.get_character_position(character_name)
            matching_location = context.check_location_exists(x, y)
            if matching_location is None or matching_location == []:
                type = "locations"
                locations_context = context.get_nearby_locations(x, y)
                
                locations_data = [context.load_json(f"app/packages/locations/locations_{matching_location}.json") for matching_location in locations_context]
                
                prompt = """Créer """ + util.extract_last_part(prompt) + """ Donne un nom, une description, une position (x, y en entiers), une liste d'objets (avec nom, description et prix), et une liste de monstres (uniquement si le donjon est de type hostile). Les monstres doivent inclure nom, description, puissance, etat, nombre, et objets. Répondez sous la forme d'un JSON structuré contenant uniquement les champs suivants : nom, description, type(boutique, donjon, sauvage, confort) position, objets, et monstres."""
                
                prompt =    f"Contexte des lieux alentours : {locations_data}\n"\
                            f"Prompt : " + prompt.strip() + "\n"
            else :
                context.moving_character_to_location(character_name, matching_location[0]) #,completion("""/speed /{character_name}/ /TODO context json à définir avec character_name/""")
        else:
            return "Le personnage est déjà en mouvement."
    elif prompt.startswith("/action"):
        count_time+=1
        character_name = prompt.split("/")[2].strip()
        if not context.is_moving(character_name):
            type = "actions"
            prompt = prompt.replace("/action", "").replace(f"""/{character_name}/""", "").strip()
            
            character_data = context.load_json(f"app/packages/characters/characters_{character_name}.json")
            character_position = character_data["position"]

            location_list = context.check_location_exists(character_position["x"], character_position["y"])

            if len(location_list) == 0:
                # Blindage temp : récupérer le premier lieu enregistré
                for filename in os.listdir("app/packages/locations"):
                    if filename.endswith('.json'):
                        file_path = os.path.join("app/packages/locations", filename)
                        with open(file_path, 'r') as file:
                            location_list = [filename.split(".")[0].replace("locations_", "")]
                            break


            matching_location = location_list[0]
            
            if matching_location is not None:
                location_data = context.load_json(f"app/packages/locations/locations_{matching_location}.json")
            
            prompt =    f"Contexte du personnage : {character_data}\n"\
                        f"Contexte du lieu : {location_data}\n"\
                        f"Prompt : {character_name} essaye de " + prompt.strip() + "Décrivez sous forme d'une phrase l'issue de l'action demandée. Assurez-vous de vérifier l'inventaire du personnage avant de répondre à l'action.\n"
        else:
            return "Le personnage est en mouvement, il ne peut pas effectuer d'action pour le moment."
    elif prompt.startswith("/speed"):
        type = "speed"
        character_name = prompt.split("/")[2].strip()
        character_data = context.load_json(f"app/packages/characters/characters_{character_name}.json")
        
        prompt = prompt.replace("/speed", "").strip() + """ "Estime la vitesse de déplacement du personnage en m/s en fonction de ses caractéristiques, en prenant comme base qu'un humain moyen se déplace à 2 m/s. Nous sommes dans dnd5. Répondez sous la forme d'un json qui contient les champs nom (du personnage) et vitesse."""
        prompt =    f"Contexte du personnage : {character_data}\n"\
                    f"Prompt : " + prompt.strip() + "\n"

    elif prompt.startswith("/time"):
        count_time = 0
        time_of_day.advance_time(prompt.split(" ")[1])
        return "Le temps a avancé de " + prompt.split(" ")[1] + " heure(s)."
    elif prompt.startswith("/create-pnj"):
        type = "pnjs"
        location_name = prompt.split("/")[2].strip()
        prompt = """Crée un personnage non-joueur. Répondez sous la forme d'un JSON contenant les champs suivants :
- nom : le nom du PNJ.
- puissance : un entier représentant la force ou l'influence du PNJ.
- etat : un objet décrivant des éléments comme la santé ou d'autres états (ex. : santé : "en bonne santé", sommeil : "en train de dormir").
- description : une description détaillée de la personnalité, de l'apparence et du rôle du PNJ.
- inventaire : une liste d'objets que possède le PNJ.
- or : un entier représentant la quantité d'or que possède le PNJ.
- routine : un objet contenant deux champs :
    - time : l'heure en entier de la journée à laquelle le PNJ change de lieu (au format 24h).
    - locations : une liste des lieux que le PNJ visite.
- position : les coordonnées actuelles du PNJ, qui correspondent à celles du lieu."""
    elif prompt.startswith("/sleep"):
        type = "sleep"
        character_name = prompt.split("/")[2].strip()
        match = re.search(r'\d+', prompt)
        if match:
            number = match.group()
        else:
            number = "7"
        return f"""{character_name} se repose pour la nuit."""
    # Vérifier si la réponse est valide avant de sauvegarder
    try :
        if (type =="characters"):
                _response = response(prompt,"Tu es un assistant qui génère des personnages pour un jeu de rôle sous forme de JSON bien structuré.",tokens=300)
                # Tentative de conversion en JSON
                required_keys = ["nom","force","dextérité","constitution","sagesse","intelligence","charisme","pv","etat","description","inventaire","or","position"]
                util.save_markdown_to_json(_response, required_keys, "characters")
        elif (type =="locations"):
                _response = response(prompt,"Tu es un assistant qui génère des lieux pour un jeu de rôle sous forme de JSON bien structuré.",tokens=600)
                # Tentative de conversion en JSON
                required_keys = ["nom", "position", "description"]
                location_to_go = util.save_markdown_to_json_return_filename(_response, required_keys, "locations")

                # on vient de créer un lieux, on va maintenant créer un personnage sur ce lieux avec une probabilité
                if location_to_go is not None:
                    location_name = location_to_go.split("locations_")[1].split(".json")[0]
                    if context.random.randint(1, 5) == 1:
                        _response = completion("/create-pnj /" + location_name + "/")
                        # Tentative de conversion en JSON
                        required_keys = ["nom","force","dextérité","constitution","sagesse","intelligence","charisme","pv","etat","description","inventaire","or","position"]
                        util.save_markdown_to_json(_response,required_keys,"pnjs")
                
                util.process_json_file(location_to_go) #modifie les données des monstres

                location_name = location_to_go.split("locations_")[1].split(".json")[0]
                return context.moving_character_to_location(character_name, location_name) #,completion("""/speed /{character_name}/ /TODO context json à définir avec character_name/""")
        elif (type =="actions"):
                return response(prompt,"Tu es un assistant qui génère des actions pour un jeu de rôle sous forme de phrase.",tokens=300)
        elif (type =="speed"):
                return util.extract_speed_from_markdown(response(prompt,"Tu es un assistant qui estime la vitesse de déplacement des personnages en m/s et qui le renvoie avec leur nom sous forme de json",tokens=300))
        elif (type =="pnjs"):
                _response = response(prompt,"Tu es un assistant qui génère des personnages non-joueurs pour un jeu de rôle sous forme de JSON bien structuré.",tokens=400)
                # Tentative de conversion en JSON
                required_keys = ["nom","puissance","description","inventaire","or","position"]
                util.save_markdown_to_json(_response,required_keys,"pnjs")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

# Exécution du script
if __name__ == "__main__":
    if openai.api_key == "YOUR_API_KEY":
        openai.api_key = input("Enter your OpenAI API key: ")

    prompt = input("Entrez votre commande : ")
    _response = completion(prompt)
    print(_response)
