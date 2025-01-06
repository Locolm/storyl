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
