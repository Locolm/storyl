import json
import re
import os
import chardet

# Réponse du modèle dans un format Markdown (avec la réponse JSON)
response_markdown = """
```json
{
  "nom": "Fizzlebang",
  "force": 8,
  "dextérité": 14,
  "constitution": 10,
  "sagesse": 12,
  "intelligence": 18,
  "charisme": 16,
  "pv": 30,
  "etat": "en bonne santé",
  "description": "Fizzlebang est un gnome illusionniste astucieux, capable de créer des copies parfaites de lui-même. Il se fond facilement dans la foule et utilise ses illusions pour tromper et déstabiliser ses ennemis. Toujours avec un sourire malicieux, il porte une baguette magique qui lui permet de projeter des illusions d'une grande réalisme.",
  "inventaire": [
    "Baguette magique des illusions",
    "Chapeau pointu",
    "Potion de camouflage",
    "Livre de sorts d'illusion",
    "Pierre de téléportation"
  ],
  "or": 150,
  "position": {
    "x": 0,
    "y": 0
  }
}
```
"""

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
            filepath = os.path.join(output_dir, base_filename + ".json") 

            # Gestion des doublons
            counter = 1
            while os.path.exists(filepath):
                filepath = os.path.join(output_dir, f"{base_filename}_{counter}.json")
                counter += 1

            # Enregistrer le personnage
            with open(filepath, "w", encoding="utf-8") as file:
                json.dump(character, file, indent=4, ensure_ascii=False)
            print(f"Personnage sauvegardé dans le fichier : {filepath}")
            return filepath
        except Exception as e:
            print(f"Une erreur s'est produite : {e}")
            
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
            filepath = os.path.join(output_dir, base_filename + ".json") 

            # Gestion des doublons
            counter = 1
            while os.path.exists(filepath):
                filepath = os.path.join(output_dir, f"{base_filename}_{counter}.json")
                counter += 1

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
        with open(json_file_path, 'r', encoding='utf-8') as file:
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
                new_monstre["tape"] = ""
                new_monstre["se_fait_taper_par"] = ""
                new_monstres.append(new_monstre)

        # Mettre à jour les monstres dans les données
        data["monstres"] = new_monstres

        # Sauvegarder les modifications dans le fichier JSON
        with open(json_file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        print(f"Fichier JSON traité et sauvegardé : {json_file_path}")

    except Exception as e:
        print(f"Une erreur s'est produite lors du traitement du fichier JSON : {e}")

# Exemple d'utilisation
# json_file_path = "locations/locations_test.json"
# process_json_file(json_file_path)