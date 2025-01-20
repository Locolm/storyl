import random
import re
import openai
import json
import os
import context
import time_of_day
import util

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
    #prompt = """/create-loc /x/ /y/"""
    #prompt = """/resolve-fight /location_name/"""

    #repérer la commande
    _response = "command not recognized"
    if prompt.startswith("/create-char"):
        type = "characters"
        prompt = """Créer un personnage avec cette description :"""+prompt.replace("/create-char", "").strip() + """"Répondez sous la forme d'un JSON contenant les champs suivants : nom, force, dextérité, constitution, sagesse, intelligence, charisme, pv, etat : [santé :en bonne santé, sommeil: reposé, déplacement: non], description, inventaire (liste), or et position (coordonnées x=0 et y=0)."""
    elif prompt.startswith("/move-to"):
        character_name = prompt.split("/")[2].strip()
        is_sleeping = context.is_sleeping(character_name)
        if is_sleeping!=0:
            return f"{character_name} est en train de dormir, il reste " + str(is_sleeping) + " heures."
        if not context.is_moving(character_name):
            try:
                parts = [part.strip() for part in prompt.split("/") if part.strip()]
                if len(parts) > 3:
                    x = int(float(parts[2]))
                    y = int(float(parts[3]))
                else:
                    x, y = context.get_character_position(character_name)
            except ValueError:
                x, y = context.get_character_position(character_name)
            matching_location = context.check_location_exists(x, y)
            if matching_location is None or matching_location == []:
                type = "locations"
                locations_context = context.get_nearby_locations(x, y)
                
                locations_data = [context.load_json(f"./locations/locations_{matching_location}.json") for matching_location in locations_context]             
                
                prompt = """Créer """ + util.extract_last_part(prompt) + """ Donne un nom, une description, une position (x"""+str(x)+""", y"""+str(y)+""" en entiers), une liste d'objets (avec nom, description et prix), et une liste de monstres (uniquement si le donjon est de type hostile). Les monstres doivent inclure nom, description, puissance, etat, nombre, et objets. Répondez sous la forme d'un JSON structuré contenant uniquement les champs suivants : nom, description, type(boutique, donjon, sauvage, confort) position, objets, et monstres."""
                
                prompt =    f"Contexte des lieux alentours : {locations_data}\n"\
                            f"Prompt : " + prompt.strip() + "\n"
            else :
                return context.moving_character_to_location(character_name, matching_location[0], completion(f"""/speed /{character_name}/"""))
        else:
            return "Le personnage est déjà en mouvement."
    elif prompt.startswith("/create-loc"):
                type = "locations-only"
                parts = [part.strip() for part in prompt.split("/") if part.strip()]
                x,y=0,0
                if len(parts) > 2:
                    x = int(float(parts[1]))
                    y = int(float(parts[2]))
                locations_context = context.get_nearby_locations(x, y)
                
                locations_data = [context.load_json(f"./locations/locations_{matching_location}.json") for matching_location in locations_context]             
                
                prompt = """Créer """ + util.extract_last_part(prompt) + """ Donne un nom, une description, une position (x="""+str(x)+""", y="""+str(y)+""" en entiers), une liste d'objets (avec nom, description et prix), et une liste de monstres (uniquement si le lieu est de type hostile comme un donjon, un lieu hanté ou autre). Les monstres doivent inclure nom, description, puissance, etat, nombre, et objets. Répondez sous la forme d'un JSON structuré contenant uniquement les champs suivants : nom, description, type(boutique, donjon, sauvage, confort) position, objets, et monstres."""
                
                prompt =    f"Contexte des lieux alentours : {locations_data}\n"\
                            f"Prompt : " + prompt.strip() + "\n"

    elif prompt.startswith("/action"):
        character_name = prompt.split("/")[2].strip()
        is_sleeping = context.is_sleeping(character_name)
        if is_sleeping!=0:
            return f"{character_name} est en train de dormir, il reste " + str(is_sleeping) + " heures."
        count_time+=1
        if not context.is_moving(character_name):
            type = "actions"
            prompt = prompt.replace("/action", "").replace(f"""/{character_name}/""", "").strip()
            
            character_data = context.load_json(f"./characters/characters_{character_name}.json")
            character_position = character_data["position"]
            matching_location = context.check_location_exists(character_position["x"], character_position["y"])[0]
            characters_name = context.get_characters_in_location(matching_location)
            characters_data = [context.load_json(f"./characters/characters_{character_name}.json") for character_name in characters_name]
            
            if matching_location is not None:
                location_data = context.load_json(f"./locations/locations_{matching_location}.json")
            
            prompt =    f"""Moment de la journée : {time_of_day.get_const_value("TIME_OF_DAY")}\n"""\
                        f"Contexte des personnages : {characters_data}\n"\
                        f"Contexte du lieu : {location_data}\n"\
                        f"Contexte des PNJs : {context.get_pnjs_in_location(matching_location)}\n"\
                        f"Prompt : {character_name} essaye de {prompt.strip()}\n"\
                        f"""Contexte de fonctionnement :
Le modèle doit vérifier si l'action demandée est possible et cohérente avec le contexte actuel. Cela inclut :

Validation des ressources : Vérifie que les personnages ou PNJs disposent des objets, or, ou capacités nécessaires à l'action.
Si le personnage tente d'acheter un objet ***mais n'a pas assez d'or***, l'action doit échouer avec une explication.
Si un PNJ est ***furieux*** ou indifférent, des actions nécessitant de flatter ou marchander échouent.
Si un PNJ est mort, alors son cadavre est présent dans la pièce et tenter de lui parler est inutile sans sort de nécromancie.
Mise à jour des inventaires : Les objets acquis ou échangés doivent être retirés des inventaires et des lieux, et ajoutés aux inventaires correspondants.
Création de PNJs au besoin : Si un PNJ absent est nécessaire pour l'action, le modèle doit en générer un avec des valeurs cohérentes (puissance, inventaire, or, etc.).
Echanges et négociations : Si une action de vente échoue faute d’or chez le PNJ, celui-ci effectue un échange équivalent (si possible).
Disponibilité des objets : ***Vérifie que les objets demandés sont présents dans les inventaires*** des lieux ou des PNJs avant d'accepter une action.\n"""\
                        f"""Sortie attendue :

Renvoie un JSON structuré contenant uniquement les changements résultant de l'action, avec ces champs :

description : Résumé narratif réaliste de l'action et de son issue (succès, échec ou ajustement). On ne doit pas se rendre compte que l'on est dans un jeu de rôle.
characters : Un tableau json contenant :
- nom : Nom du personnage concerné.
- inventaire : Liste  mise à jour des objets dans l’inventaire du personnage après l’action, en retirant les objets consommés et en ajoutants les objets acquis.
- or : Or restant si utilisé ou modifié.
- santé : Modifications du champ santé du personnage (bourré, euphorique, mal en point, en bonne santé ...)(s'il y a eu modification).
pnjs : Tableau contenant :
- nom : Nom du PNJ impliqué.
- inventaire : Liste mise à jour des objets après l’action, en retirant les objets consommés et en ajoutants les objets acquis.
- or : Or restant (si utilisé ou modifié).
- santé: Modifications de l'état de santé du PNJ (mort, blessé, apeuré, ...)(si applicables).
- humeur: Modifications d’humeur (en colère, heureux, ivre, ...)(si applicables).
- puissance : Puissance du PNJ (si applicable).
locations : Un objet contenant :
- nom : Nom du lieu impacté.
- objets : Liste mise à jour des objets restant dans le lieu après l’action."""
        else:
            return "Le personnage est en mouvement, il ne peut pas effectuer d'action pour le moment."
    elif prompt.startswith("/resolve-fight"):
        type = "fight"
        location_name = prompt.split("/")[2].strip()
        
        prompt =    """Renvoie-moi un JSON contenant :

description : Une description narrative détaillée et fluide du déroulement du combat entre les personnages, les PNJs et les monstres. Raconte les événements de manière cohérente et logique en plusieurs paragraphes, en tenant compte de la puissance estimée des personnages, des PNJs et des monstres, ainsi que de leur équipement, état initial, et description.

gagnant : (valeurs possibles : Monstres ou Personnages). Si les personnages gagnent, indique s'ils ont éradiqué tous les monstres ou si certains monstres ont fui. Si les monstres gagnent, précise que les personnages ont dû fuir.

pnjs : Un tableau listant les PNJs présents à la fin du combat. Pour chaque PNJ, indique :
  - nom
  - humeur (ex. : "flatté", "apeuré", "inquiet", "concentré" etc.)
  - santé (ex. : "en bonne santé", "blessé", "mourant", "mort")
  - mise à jour de l’inventaire (ajout ou retrait d’objets consommés pendant le combat, Une pomme est consommable, une épée ne l’est pas, l'épée reste dans l'inventaire).

personnages : Un tableau contenant les personnages mis à jour après le combat. Pour chaque personnage, indique :
  - nom
  - inventaire (mis à jour selon les objets utilisés ou gagnés)
  - état de santé mis à jour (par ordre de gravité [etat][santé] : "en bonne santé", "légèrement blessé", "blessé", "mal en point", "Gravement blessé", "Agonisant", "inconscient", "mort", il existe aussi d'autres état en fonction de la situation comme "empoisonné", "brûlé", "gêlé" etc.). Ne modifie pas [etat][sommeil], [etat][déplacement].

monstres : Une liste des monstres encore vivant après le combat. Indique leur état (vivant, blessé, mourant,...).

Contexte spécifique :
1. La puissance des personnages doit être estimée à partir de leurs caractéristiques et de leur description :
   - **Faible** : Puissance 1-15 → Exemples : personnages maladroits, sans entraînement ou avec des caractéristiques physiques très basses.
   - **Moyenne** : Puissance 16-40 → Exemples : personnages ordinaires avec des compétences variées et des objets simples.
   - **Forte** : Puissance 41-80 → Par défaut, un personnage bien équilibré avec des caractéristiques cohérentes et un bon équipement devrait avoir une puissance dans cette fourchette.
   - **Très forte** : Puissance 81-120 → Exemples : personnages particulièrement remarquables avec des talents ou un équipement exceptionnel.
   - **Épique** : Puissance 121-200 → Exemples : héros légendaires ou personnages incroyablement puissants avec des descriptions uniques.
   - La puissance estimée doit être cohérente avec les caractéristiques et descriptions. Par exemple, un personnage avec une dextérité de 18 et un charisme de 20 devrait être considéré comme ayant une puissance **forte** ou **très forte**, sauf s'il est affaibli.
   - Si un personnage est affaibli (ex. : "mal en point"), sa puissance doit être réduite d'un nombre de niveau équivalant à l'affaiblissement, par exemple s'il est mal en point son état est critique donc on le descend de 3 niveau (ex. : de **forte** à **faible**).
2. Les personnages peuvent vaincre facilement des monstres faibles (1-15), même en grand nombre, sauf dans des circonstances défavorables (ex. : état affaibli, environnement hostile).
3. Les personnages mal en points se battent avec difficultée, ceux ayant un état plus critique ne peuvent pas se battre.
4. La difficulté des combats est déterminée par la puissance des monstres et leur nombre :
    - Un monstre de puissance 300 ne peut pas être vaincu par un seul personnage, même s'il est très puissant, il faut au moins 3 personnages pour le vaincre.
    - Un personnage sort forcément blessé d'un combat contre un monstre de puissance 80 ou plus.
5. Décris les actions de manière logique :
   - Si les personnages sont bien préparés (ex. : potions, objets spéciaux, stratégie), ils doivent triompher des monstres faibles avec peu de dégâts.
   - Si les personnages sont affaiblis (ex. : "mal en point"), adapte la description pour montrer qu'ils rencontrent plus de difficulté, mais sans les rendre incohérents avec leur puissance globale.
"""
        
        characters_name = context.get_characters_in_location(location_name)
        characters_data = [context.load_json(f"./characters/characters_{character_name}.json") for character_name in characters_name]
        
        location_data = context.load_json(f"./locations/locations_{location_name}.json")
        
        pnjs_data = context.get_pnjs_in_location(location_name)
        
        prompt =    f"""Moment de la journée : {time_of_day.get_const_value("TIME_OF_DAY")}\n"""\
                    f"Contexte du lieu : {location_data}\n"\
                    f"Contexte des personnages dans le lieu : {characters_data}\n"\
                    f"Contexte des pnjs présents dans le lieu : {pnjs_data}\n"\
                    """Contexte de l'affrontement : voici un ordre d'idée de la puissance des monstres : faible : 1-15, moyen : 16-40, fort : 41-70, très fort : 71-120, extrêmement fort : 121-200, légendaire : 201-300\n
                    La puissance d'un monstre indique la difficulté de l'affrontement, un personnage (en fonction de son équipement et de sa description qui indique un ordre d'idée de sa puissance) peut facilement à lui seul vaincre une dizaine de monstres faible, 5 monstres moyen, 2 monstre fort, 1 monstre très fort. Deux personnages viennent à bout de 1 monstre extrêmement fort, et un monstre légendaire est un défi pour un groupe de 5 personnages très puissants.\n
                    certains personnages peuvent mourir lors de cet affrontement (rare seulement si les mosntres sont extrêmement fort), ils peuvent gagner cet affrontement malgré la différence de nombre s'ils sont suffisament bien préparé (inventaire) ou suffisamment fort (les monstres sont faible, accompagné d'un pnj puissant, les personnages ont une description qui indique leur puissance) dans ce cas là les personnages peuvent gagner l'affrontement et erradiquer tous les monstres (leur état de santé finale dépendra de la difficulté du combat).\n"""\
                    f"Prompt : {prompt.strip()}\n"
        
    elif prompt.startswith("/speed"):
        type = "speed"
        character_name = prompt.split("/")[2].strip()
        character_data = context.load_json(f"./characters/characters_{character_name}.json")
        
        prompt = prompt.replace("/speed", "").strip() + """ "Estime la vitesse de déplacement du personnage en m/s en fonction de ses caractéristiques, en prenant comme base qu'un humain moyen se déplace à 2 m/s. Nous sommes dans dnd5. Répondez sous la forme d'un json qui contient les champs nom (du personnage) et vitesse."""
        prompt =    f"Contexte du personnage : {character_data}\n"\
                    f"Prompt : " + prompt.strip() + "\n"
    elif prompt.startswith("/time"):
        count_time = 0
        _response = context.get_arrival_descriptions(time_of_day.advance_time(prompt.split(" ")[1]))
        if _response=="":
            return "Le temps a avancé de " + prompt.split(" ")[1] + " heure(s)."
        else:
            return _response
    elif prompt.startswith("/create-pnj"):
        type = "pnjs"
        location_name = prompt.split("/")[2].strip()
        current_location_data = context.load_json(f"./locations/locations_{location_name}.json")
        x = current_location_data["position"]["x"]
        y = current_location_data["position"]["y"]
        
        locations_context = context.get_nearby_locations(x, y)
                
        locations_data = [context.load_json(f"./locations/locations_{matching_location}.json") for matching_location in locations_context]   
        
        
        prompt = f"""Crée un personnage non-joueur. Répondez sous la forme d'un JSON contenant les champs suivants :
- nom : le nom du PNJ.
- puissance : un entier représentant la force ou l'influence du PNJ.
- etat : un objet décrivant des éléments comme la santé ou d'autres états (ex. : santé : "en bonne santé", sommeil : "en train de dormir").
- description : une description détaillée de la personnalité, de l'apparence et du rôle du PNJ.
- inventaire : une liste d'objets que possède le PNJ.
- or : un entier représentant la quantité d'or que possède le PNJ.
- routine : un objet contenant deux champs :
    - time : l'heure en entier de la journée à laquelle le PNJ change de lieu (au format 24h).
    - locations : une liste des lieux que le PNJ visite.
- position : les coordonnées actuelles du PNJ, qui correspondent à celles du lieu.x={x},y={y}."""

        prompt =    f"Contexte du lieu actuel : {current_location_data}\n"\
                    f"Contexte des lieux alentours : {locations_data}\n"\
                    f"Prompt : " + prompt.strip() + "\n"
    elif prompt.startswith("/sleep"):
        type = "sleep"
        character_name = prompt.split("/")[2].strip()
        is_sleeping = context.is_sleeping(character_name)
        if is_sleeping!=0:
            return f"{character_name} est déjà en train de dormir, il reste " + str(is_sleeping) + " heures."
        match = re.search(r'\d+', prompt)
        if match:
            number = match.group()
        else:
            number = "8"
        context.update_character_state_with_sleep(character_name, number)
        return f"""{character_name} se repose pour la nuit."""
    # Vérifier si la réponse est valide avant de sauvegarder
    try :
        if (type =="characters"):
                _response = response(prompt,"Tu es un assistant qui génère des personnages pour un jeu de rôle sous forme de JSON bien structuré.",tokens=300)
                # Tentative de conversion en JSON
                required_keys = ["nom","force","dextérité","constitution","sagesse","intelligence","charisme","pv","etat","description","inventaire","or","position"]
                util.save_markdown_to_json(_response,required_keys,"characters")
                return "personnage sauvegardé"
        elif (type =="locations"):
                _response = response(prompt,"Tu es un assistant qui génère des lieux pour un jeu de rôle sous forme de JSON bien structuré.",tokens=600)
                # Tentative de conversion en JSON
                required_keys = ["nom", "position", "description"]
                location_to_go = util.save_markdown_to_json_return_filename(_response, required_keys, "locations")

                # on vient de créer un lieux, on va maintenant créer un personnage sur ce lieux avec une probabilité
                if location_to_go is not None:
                    location_name = location_to_go.split("locations_")[1].split(".json")[0]
                    if random.randint(1, 3) == 1:
                        _response = completion("/create-pnj /" + location_name + "/")
                        # Tentative de conversion en JSON
                        required_keys = ["nom","force","dextérité","constitution","sagesse","intelligence","charisme","pv","etat","description","inventaire","or","position"]
                        util.save_markdown_to_json(_response,required_keys,"pnjs")
                
                util.process_json_file(location_to_go) #modifie les données des monstres

                location_name = location_to_go.split("locations_")[1].split(".json")[0]
                return context.moving_character_to_location(character_name, location_name,speed_m_s=completion("""/speed /{character_name}/"""))
        elif (type =="locations-only"):
                _response = response(prompt,"Tu es un assistant qui génère des lieux pour un jeu de rôle sous forme de JSON bien structuré.",tokens=600)
                # Tentative de conversion en JSON
                required_keys = ["nom", "position", "description"]
                location_to_go = util.save_markdown_to_json_return_filename(_response, required_keys, "locations")

                # on vient de créer un lieux, on va maintenant créer un personnage sur ce lieux avec une probabilité
                if location_to_go is not None:
                    location_name = location_to_go.split("locations_")[1].split(".json")[0]
                    if random.randint(1, 3) == 1:
                        _response = completion("/create-pnj /" + location_name + "/")
                        # Tentative de conversion en JSON
                        required_keys = ["nom","force","dextérité","constitution","sagesse","intelligence","charisme","pv","etat","description","inventaire","or","position"]
                        util.save_markdown_to_json(_response,required_keys,"pnjs")
                
                #util.process_json_file(location_to_go) #modifie les données des monstres

                location_name = location_to_go.split("locations_")[1].split(".json")[0]
                return "Lieu créé"
        elif (type =="actions"):
                _response = response(prompt,"Tu es un assistant qui génère des actions pour un jeu de rôle sous forme de JSON.",tokens=950)
                print("_response",_response)
                _reponse_json = util.extract_json_from_markdown(_response)
                # enregistrement des changements
                context.process_actions(_reponse_json)
                return util.get_description_from_json(_reponse_json)
        elif (type =="fight"):
            _response = response(prompt,"Tu es un assistant qui génère des combats pour un jeu de rôle sous forme de JSON bien structuré.",tokens=5000)
            # Tentative de conversion en JSON
            print("_response",_response)
            _dict_response = util.extract_json_from_markdown(_response)

            if "personnages" in _dict_response:
                util.update_characters_from_json(_dict_response)
                            
            if "pnjs" in _dict_response:
                util.update_pnjs_from_json(_dict_response)
            
            if "monstres" in _dict_response:
                util.update_monsters_from_json(location_name,_dict_response)
            
            count_time+=15 #un combat fait passer le temps

            if "description" in _dict_response:
                return _dict_response['description']
            else:
                return "Le combat s'est déroulé sans encombre."
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
