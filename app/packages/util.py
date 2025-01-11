import json
import re
import os
import chardet

# Réponse du modèle dans un format Markdown (avec la réponse JSON)
response_markdown = """
```json
{
  "description": "Tenzin le Fort se tient fermement, ses muscles tendus comme un arc, alors qu'il fait face aux deux Golems de l'ombre. Inspirant profondément, il canalise son énergie intérieure et exécute une série de mouvements fluides et puissants, frappant avec son bâton de bois. Son attaque fait vibrer l'air autour de lui, frappant le premier Golem avec une force incroyable. Le Golem de l'ombre, bien que résistant, est projeté en arrière, perdant une partie de sa puissance et de sa capacité à absorber la lumière.",
  "état monstre": {
    "nombre restants": 2,
    "puissance restante": 60,
    "état": "affaibli"
  },
  "inventaire personnage": [
    "Bâton de bois",
    "Amulette de protection",
    "Potion de soins",
    "Sandales légères"
  ]
}
```
"""



def extract_json_from_markdown(markdown):
    """Extrait le JSON d'une chaîne Markdown.

    Args:
        markdown (str): La chaîne Markdown contenant le JSON.

    Returns:
        dict: Le JSON extrait sous forme de dictionnaire.
    """
    try:
        json_pattern = r"`json\n(.*?)\n`"
        match = re.search(json_pattern, markdown, re.DOTALL)
        
        if match:
            json_str = match.group(1)
            return json.loads(json_str)
        else:
            print("Aucun JSON trouvé dans le markdown.")
            return None
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'extraction du JSON: {e}")
        return None
    
tetx = extract_json_from_markdown(response_markdown)

def save_markdown_to_json(response_markdown, required_keys, output_dir="characters"):
    """Extrait le JSON d'une chaîne Markdown et le sauvegarde dans un fichier.

    Args:
        response_markdown (str): La chaîne Markdown contenant le JSON.
        output_dir (str, optional): Le répertoire de sortie. Defaults to "characters".
    """

    json_pattern = r"`json\n(.*?)\n`"
    matches = re.findall(json_pattern, response_markdown, re.DOTALL)

    for json_str in matches:
        try:
            character = json.loads(json_str)

            # Validation minimale des données
            if not all(key in character for key in required_keys):
                print("Le JSON ne contient pas toutes les clés requises.")
                continue

            # Obtenir le nom du personnage, avec une valeur par défaut
            character_name = character.get("nom", "default")

            # Construire le nom de fichier de base
            base_filename = f"{output_dir}_{character_name}"
            filepath = os.path.join(f"app/packages/{output_dir}", base_filename + ".json")

            # Gestion des doublons
            counter = 1
            while os.path.exists(filepath):
                filepath = os.path.join(f"app/packages/{output_dir}", f"{base_filename}_{counter}.json")
                counter += 1
                
            # Renommer le personnage en incluant le counter s'il y a des doublons
            if counter > 1:
                character["nom"] = f"{character_name}_{counter - 1}"
    
            # Enregistrer le personnage
            with open(filepath, "w", encoding="utf-8") as file:
                json.dump(character, file, indent=4, ensure_ascii=False)
            print(f"Personnage sauvegardé dans le fichier : {filepath}")
            return filepath
        except Exception as e:
            print(f"Une erreur s'est produite : {e}")
            raise e
            
def detect_encoding(json_file_path):
    try:
        # Ouvrir le fichier en mode binaire pour détecter l'encodage
        with open(json_file_path, 'rb') as file:
            raw_data = file.read()

        # Utiliser chardet pour détecter l'encodage
        result = chardet.detect(raw_data)
        encoding = result['encoding']

        return encoding
    except Exception as e:
        return f"Une erreur s'est produite : {e}"

# Exemple d'utilisation
#required_keys = ["nom","force","dextérité","constitution","sagesse","intelligence","charisme","pv","etat","description","inventaire","or","position"]
#save_markdown_to_json(response_markdown,required_keys)

# Exemple d'utilisation
# file_path = "characters/pj_Fizzlebang.json"  # Remplace ce chemin par le fichier JSON de ton choix
# encoding = detect_encoding(file_path)
# print(f"L'encodage du fichier est : {encoding}")

def extract_last_part(command):
    """Extrait la dernière partie d'une commande après '/'.

    Args:
        command (str): La commande à découper.

    Returns:
        str: La dernière partie de la commande.
    """
    parts = command.split('/')
    if parts:
        return parts[-1].strip()
    return ""

# Exemple d'utilisation
# command = "/move-to /Tenzin le fort/ /x/ /y/ un donjon labyrinthe."
# last_part = """Créer """ + extract_last_part(command) + """ Donne un nom, une description, une position (x, y en entiers), une liste d'objets (avec nom, description et prix), et une liste de monstres (uniquement si le donjon est de type hostile). Les monstres doivent inclure nom, description, puissance, etat, nombre, et objets. Répondez sous la forme d'un JSON structuré contenant uniquement les champs suivants : nom, description,type(boutique, donjon, sauvage,...) position, objets, et monstres. /TODO contexte des lieux à proximité/"""
# print(f"'{last_part}'")


def extract_speed_from_markdown(markdown):
    """Extrait la vitesse d'une chaîne Markdown et la renvoie en entier.

    Args:
        markdown (str): La chaîne Markdown contenant les informations.

    Returns:
        int: La vitesse extraite ou 2 en cas d'erreur.
    """
    try:
        # Rechercher la vitesse dans le markdown
        speed_pattern = r"\"vitesse\":\s*([\d.]+),?"
        match = re.search(speed_pattern, markdown)
        
        if match:
            speed_str = match.group(1)
            return int(float(speed_str))
        else:
            print("Warning: Vitesse non trouvée dans le markdown.")
            return 2
    except Exception as e:
        print(f"Warning: Une erreur s'est produite lors de l'extraction de la vitesse: {e}")
        return 2

# Exemple d'utilisation
# markdown = """
# ```json
# {
#   "nom": "Fizzlebang",
#   "vitesse": 7,
# }
# ```
# """
# speed = extract_speed_from_markdown(markdown)
# print(f"Vitesse extraite: {speed}")

def save_markdown_to_json_return_filename(response_markdown, required_keys, output_dir="characters"):
    """Extrait le JSON d'une chaîne Markdown et le sauvegarde dans un fichier, puis renvoie le nom du fichier.

    Args:
        response_markdown (str): La chaîne Markdown contenant le JSON.
        output_dir (str, optional): Le répertoire de sortie. Defaults to "characters".

    Returns:
        str: Le nom complet du fichier créé.
    """

    json_pattern = r"`json\n(.*?)\n`"
    matches = re.findall(json_pattern, response_markdown, re.DOTALL)

    for json_str in matches:
        try:
            character = json.loads(json_str)

            # Validation minimale des données
            if not all(key in character for key in required_keys):
                print("Le JSON ne contient pas toutes les clés requises.")
                continue

            # Obtenir le nom du personnage, avec une valeur par défaut
            character_name = character.get("nom", "default")

            # Construire le nom de fichier de base
            base_filename = f"{output_dir}_{character_name}"
            filepath = os.path.join(f"app/packages/{output_dir}", base_filename + ".json")

            # Gestion des doublons
            counter = 1
            while os.path.exists(filepath):
                filepath = os.path.join(f"app/packages/{output_dir}", f"{base_filename}_{counter}.json")
                counter += 1
            
            # Renommer le counter s'il y a des doublons
            if counter > 1:
                character["nom"] = f"{character_name}_{counter - 1}"

            # Enregistrer le personnage
            with open(filepath, "w", encoding="utf-8") as file:
                json.dump(character, file, indent=4, ensure_ascii=False)
            print(f"Personnage sauvegardé dans le fichier : {filepath}")
            return os.path.basename(filepath)
        except Exception as e:
            print(f"Une erreur s'est produite : {e}")
            return None
        
# Exemple d'utilisation
# required_keys = ["nom","force","dextérité","constitution","sagesse","intelligence","charisme","pv","etat","description","inventaire","or","position"]
# file_path = save_markdown_to_json_return_filename(response_markdown,required_keys)
# print(file_path)

def process_json_file(json_file_path):
    """Traite un fichier JSON pour modifier les monstres en ajoutant des noms uniques et des caractéristiques supplémentaires.

    Args:
        json_file_path (str): Le chemin du fichier JSON à traiter.
    """
    try:
        # Lire le fichier JSON
        with open(f"app/packages/{json_file_path}", 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Traiter les monstres
        new_monstres = []
        for monstre in data.get("monstres", []):
            nombre = monstre.pop("nombre", 1)
            for i in range(nombre):
                new_monstre = monstre.copy()
                if i > 0:
                    new_monstre["nom"] = f"{monstre['nom']}_{i}"
                new_monstre["etat"] = "en bonne santé"
                new_monstres.append(new_monstre)

        # Mettre à jour les monstres dans les données
        data["monstres"] = new_monstres

        # Sauvegarder les modifications dans le fichier JSON
        with open(f"app/packages/{json_file_path}", 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        print(f"Fichier JSON traité et sauvegardé : {json_file_path}")

    except Exception as e:
        print(f"Une erreur s'est produite lors du traitement du fichier JSON : {e}")

# Exemple d'utilisation
# json_file_path = "locations/locations_test.json"
# process_json_file(json_file_path)

def extract_json_from_markdown(markdown):
    """Extrait le JSON d'une chaîne Markdown.

    Args:
        markdown (str): La chaîne Markdown contenant le JSON.

    Returns:
        dict: Le JSON extrait sous forme de dictionnaire.
    """
    try:
        json_pattern = r"`json\n(.*?)\n`"
        match = re.search(json_pattern, markdown, re.DOTALL)
        
        if match:
            json_str = match.group(1)
            return json.loads(json_str)
        else:
            print("Aucun JSON trouvé dans le markdown.")
            return None
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'extraction du JSON: {e}")
        return None

# Exemple d'utilisation
# markdown = """
# ```json
# {
#   "nom": "Fizzlebang",
#   "force": 8,
#   "dextérité": 14,
#   "constitution": 10,
#   "sagesse": 12,
#   "intelligence": 18,
#   "charisme": 16,
#   "pv": 30,
#   "etat": "en bonne santé",
#   "description": "Fizzlebang est un gnome illusionniste astucieux, capable de créer des copies parfaites de lui-même. Il se fond facilement dans la foule et utilise ses illusions pour tromper et déstabiliser ses ennemis. Toujours avec un sourire malicieux, il porte une baguette magique qui lui permet de projeter des illusions d'une grande réalisme.",
#   "inventaire": [
#     "Baguette magique des illusions",
#     "Chapeau pointu",
#     "Potion de camouflage",
#     "Livre de sorts d'illusion",
#     "Pierre de téléportation"
#   ],
#   "or": 150,
#   "position": {
#     "x": 0,
#     "y": 0
#   }
# }
# ```
# """
# extracted_json = extract_json_from_markdown(markdown)
# print(extracted_json)

def get_description_from_json(json_data):
    """Extrait la description d'un JSON.

    Args:
        json_data (dict): Le dictionnaire JSON contenant les données.

    Returns:
        str: La description extraite ou "l'action n'a pas pu être effectuée" si non trouvée.
    """
    return json_data.get("description", "l'action n'a pas pu être effectuée")


def update_characters_from_json(input_json):
    if not input_json:
        raise ValueError("Input JSON is null, invalid, or empty.")
    if 'personnages' not in input_json.keys():
        raise KeyError("Input JSON does not contain 'personnages' key.")
    
    characters = input_json['personnages']
    
    for character in characters:
        if 'nom' not in character:
            raise KeyError("Character JSON does not contain 'nom' key.")
        
        character_name = character['nom']
        
        # Load the character's JSON file
        file_path = f'app/packages/characters/characters_{character_name}.json'
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        
        with open(file_path, 'r', encoding='utf-8') as file:
            character_data = json.load(file)
        
        # Update the character's inventory and state if they exist in the input JSON
        if 'inventaire' in character:
            character_data['inventaire'] = character['inventaire']
        
        if 'etat' in character:
            character_data['etat'].update(character['etat'])
        
        # Save the updated JSON file
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(character_data, file, indent=4, ensure_ascii=False)

# Example usage:
# input_json = {'description': "Dans le sombre Labyrinthe des Ombres, une atmosphère oppressante plane alors que Sir Mimic et Tenzin le Fort se tiennent face à deux Golems de l'ombre, leurs silhouettes mouvantes glissant sur les murs humides. Les échos des gouttes d'eau résonnent comme un présage funeste, tandis qu'une légère brume enveloppe le terrain. Sir Mimic, en armure brillante d'un mimique, avance prudemment, épée à la main, conscient de la menace qui pèse sur lui. Tenzin, le moine musclé, adopte une posture défensive, prêt à exploiter sa force et sa sagesse pour contrer les attaques des créatures sombres.\n\nLes Golems, bien que blessés, se déplacent lentement mais sûrement, cherchant à encadrer leurs proies. L'un d'eux s'élance vers Tenzin, qui réagit rapidement avec un coup de bâton, mais la créature de ténèbres évite habilement l'attaque avec une agilité inattendue. Sir Mimic, voyant son ami en difficulté, se précipite pour frapper le Golem avec son épée en mimique. L'impact résonne dans le labyrinthe, mais la créature se redresse, presque imperméable à la douleur.\n\nSoudain, trois Spectres errants apparaissent dans un nuage de brume, ajoutant à la confusion. Leur visage tourmenté est une vision d'horreur qui fait frémir même les plus braves. Tenzin, déjà mal en point, est assailli par un des spectres, qui lui inflige une étreinte spectrale, le laissant à bout de souffle. Sir Mimic tente de protéger son camarade, mais sa propre santé est mise à l'épreuve alors qu'un Golem l'attaque avec brutalité.\n\nLe combat devient chaotique. Les personnages, bien que courageux, commencent à réaliser que la situation leur échappe. Les attaques des monstres se font de plus en plus puissantes, et les blessures s'accumulent. Tenzin, sentant ses forces décliner, lance une potion de soin, mais même cela ne suffit pas à renverser le cours du combat. L'un des Golems, presque à terre, parvient à porter un coup fatal à Sir Mimic, qui s'effondre, laissant Tenzin seul face aux ombres.\n\nFinalement, réalisant qu'ils n'ont aucune chance de victoire, Tenzin prend la décision difficile de fuir. Ébranlé, il se détourne des monstres, traversant le labyrinthe dans une course désespérée, laissant derrière lui les échos de la bataille et les cris des Spectres. Ce combat, bien que héroïque, se termine par une retraite précipitée, marquée par la défaite et l'humiliation.", 'gagnant': 'Monstres', 'pnjs': [{'nom': 'Ezran le Cartographe', 'etat': {'humeur': 'inquiet'}, 'inventaire': [{'nom': 'Plume enchantée', 'description': "Une plume magique qui ne s'épuise jamais d'encre, parfaite pour dessiner des cartes."}, {'nom': 'Carnet de cartographie', 'description': 'Un carnet contenant des croquis détaillés de certaines parties du labyrinthe, bien que certaines zones soient incomplètes.'}, {'nom': "Loupe d'observation", 'description': 'Un outil précieux pour détecter les détails cachés sur les murs du labyrinthe.'}]}], 'personnages': [{'nom': 'Sir Mimic', 'inventaire': ['épée en mimique', 'bouclier en mimique', 'potion de soins', 'amulette de camouflage'], 'etat': {'santé': 'mort'}}, {'nom': 'Tenzin le Fort', 'inventaire': ['Bâton de bois', 'Amulette de protection', 'Potion de soin', 'Sandales légères', 'alcool très fort'], 'etat': {'santé': 'mal en point'}}], 'monstres': [{'nom': "Golem de l'ombre", 'description': "Une créature faite d'ombres et de ténèbres...", 'puissance': 80, 'nombre': 2, 'objets': [{'nom': "Cœur d'ombre", 'description': 'Un artefact rare...', 'prix': 50}], 'etat': "Un Golem de l'ombre affaibli, presque à terre."}, {'nom': 'Spectre errant', 'description': "L'âme tourmentée d'un ancien aventurier...", 'puissance': 50, 'nombre': 3, 'objets': [{'nom': 'Étreinte spectrale', 'description': 'Un objet intangible...', 'prix': 30}]}]}
# update_characters_from_json(input_json)

def update_pnjs_from_json(input_json):
    if not input_json:
        raise ValueError("Input JSON is null, invalid, or empty.")
    
    if 'pnjs' not in input_json:
        raise KeyError("Input JSON does not contain 'pnjs' key.")
    
    pnjs = input_json['pnjs']
    
    for pnj in pnjs:
        if 'nom' not in pnj:
            raise KeyError("PNJ JSON does not contain 'nom' key.")
        
        pnj_name = pnj['nom']
        
        # Load the PNJ's JSON file
        file_path = f'app/packages/pnjs/pnjs_{pnj_name}.json'
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        
        with open(file_path, 'r', encoding='utf-8') as file:
            pnj_data = json.load(file)
        
        # Update the PNJ's inventory and state if they exist in the input JSON
        if 'inventaire' in pnj:
            pnj_data['inventaire'] = pnj['inventaire']
        
        if 'etat' in pnj:
            pnj_data['etat'].update(pnj['etat'])
        
        # Save the updated JSON file
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(pnj_data, file, indent=4, ensure_ascii=False)

# Example usage:
# input_json = {
#     "description": "Les ténèbres enveloppent le Labyrinthe des Ombres...",
#     "pnjs": [
#         {
#             "nom": "Ezran le Cartographe",
#             "inventaire": [
#                 {
#                     "nom": "Plume enchantée",
#                     "description": "Une plume magique qui ne s'épuise jamais d'encre, parfaite pour dessiner des cartes."
#                 },
#                 {
#                     "nom": "Carnet de cartographie",
#                     "description": "Un carnet contenant des croquis détaillés de certaines parties du labyrinthe, bien que certaines zones soient incomplètes."
#                 },
#             ],
#             "etat": {
#                 "humeur": "triste"
#             }
#         }
#     ]
# }
# update_pnjs_from_json(input_json)

def update_monsters_from_json(location_name, input_json):
    if not input_json:
        raise ValueError("Input JSON is null, invalid, or empty.")
    
    if 'monstres' not in input_json:
        raise KeyError("Input JSON does not contain 'monstres' key.")
    
    monsters = input_json['monstres']
    
    # Load the location's JSON file
    file_path = f'app/packages/locations/locations_{location_name}.json'
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        location_data = json.load(file)
    
    # Update the monsters in the location data
    location_data['monstres'] = monsters
    
    # Save the updated JSON file
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(location_data, file, indent=4, ensure_ascii=False)
    print(f"Monstres mis à jour dans le fichier : {file_path}")

# Example usage:
# location_name = "Labyrinthe des Ombres"
# input_json = {
#     "description": "Les ténèbres enveloppent le Labyrinthe des Ombres...",
#     "monstres": [
#         {
#             "nom": "Golem de l'ombre",
#             "description": "Une créature faite d'ombres et de ténèbres...",
#             "puissance": 80,
#             "nombre": 2,
#             "objets": [
#                 {
#                     "nom": "Cœur d'ombre",
#                     "description": "Un artefact rare...",
#                     "prix": 50
#                 }
#             ],
#             "etat": "Un Golem de l'ombre affaibli, presque à terre."
#         },
#         {
#             "nom": "Spectre errant",
#             "description": "L'âme tourmentée d'un ancien aventurier...",
#             "puissance": 50,
#             "nombre": 3,
#             "objets": [
#                 {
#                     "nom": "Étreinte spectrale",
#                     "description": "Un objet intangible...",
#                     "prix": 30
#                 }
#             ]
#         }
#     ]
# }
# update_monsters_from_json(location_name, input_json)
