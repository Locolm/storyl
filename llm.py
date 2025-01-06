import openai
import json
import os
import context
import util

# Remplacez "YOUR_API_KEY" par votre clé API OpenAI : # Remplacez par votre clé API OpenAI accessible ici https://platform.openai.com/settings/organization/api-keys
openai.api_key = "YOUR_API_KEY"
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
    type = "stop"

    #prompt = input("Entrez votre commande : ")
    #prompt = """/create-loc Créer un donjon labyrinthe."""
    #prompt = """/create-char Un moine musclé dont la force incroyable est déployée à travers des techniques martiales ancestrales."""
    #prompt = """/action /Tenzin le fort/ donner un coup d'épée au goblin devant lui. /TODO context json à définir avec character_name et position => lieux où il se trouve/"""
    #prompt = """/speed /Tenzin le fort/ /TODO context json à définir avec character_name/"""

    #repérer la commande /create-char ou /create-loc
    _response = "command not recognized"
    if prompt.startswith("/create-char"):
        type = "characters"
        prompt = """Créer un personnage avec cette description :"""+prompt.replace("/create-char", "").strip() + """"Répondez sous la forme d'un JSON contenant les champs suivants : nom, force, dextérité, constitution, sagesse, intelligence, charisme, pv, etat, description, inventaire (liste), or et position (coordonnées x=0 et y=0)."""
    elif prompt.startswith("/create-loc"):
        type = "locations"
        prompt = prompt.replace("/create-loc", "").strip() + """Donne un nom, une description, une position (x, y en entiers), une liste d'objets (avec nom, description et prix), et une liste de monstres (uniquement si le donjon est de type hostile). Les monstres doivent inclure nom, description, puissance, etat, nombre, et objets. Répondez sous la forme d'un JSON structuré contenant uniquement les champs suivants : nom, description,type(boutique, donjon, sauvage,...) position, objets, et monstres."""
    elif prompt.startswith("/action"):
        type = "actions"
        character_name = prompt.split("/")[2].strip()
        prompt = prompt.replace("/action", "").replace(f"""/{character_name}/""", "").strip()
        prompt = f"""{character_name} essaye de """ + prompt.strip() + """"Décrivez sous forme d'une phrase l'issue de l'action demandée. Assurez-vous de vérifier l'inventaire du personnage avant de répondre à l'action. /TODO context json à définir avec character_name et position => lieux où il se trouve/"""
    elif prompt.startswith("/speed"):
        type = "speed"
        character_name = prompt.split("/")[2].strip()
        prompt = prompt.replace("/speed", "").strip() + """ "Estime la vitesse de déplacement du personnage en m/s en fonction de ses caractéristiques, en prenant comme base qu'un humain moyen se déplace à 2 m/s. Nous sommes dans un jeu de rôle. /TODO context json à définir avec character_name/"""

    if type == "":
        _response = response(prompt,"tu es un assitant bref", tokens= 50)

    # Vérifier si la réponse est valide avant de sauvegarder
    try :
        if (type =="characters"):
                _response = response(prompt,"Tu es un assistant qui génère des personnages pour un jeu de rôle sous forme de JSON bien structuré.",tokens=300)
                # Tentative de conversion en JSON
                required_keys = ["nom","force","dextérité","constitution","sagesse","intelligence","charisme","pv","etat","description","inventaire","or","position"]
                util.save_markdown_to_json(_response,required_keys,"characters")
        elif (type =="locations"):
                _response = response(prompt,"Tu es un assistant qui génère des lieux pour un jeu de rôle sous forme de JSON bien structuré.",tokens=600)
                # Tentative de conversion en JSON
                required_keys = ["nom", "position", "description"]
                util.save_markdown_to_json(_response, required_keys, "locations")
        elif (type =="actions"):
                _response = response(prompt,"Tu es un assistant qui génère des actions pour un jeu de rôle sous forme de phrase.",tokens=300)
        elif (type =="speed"):
                _response = response(prompt,"Tu es un assistant qui estime la vitesse de déplacement des personnages en m/s et qui le renvoie avec leur nom sous forme de json",tokens=300)
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

# Exécution du script
if __name__ == "__main__":
    if openai.api_key == "YOUR_API_KEY":
        openai.api_key = input("Enter your OpenAI API key: ")

    prompt = input("Entrez votre commande : ")
    if prompt.startswith("/time"):
        _response = context.advance_time(prompt.split(" ")[1])
    else:
        _response = completion(prompt)
    print(_response)
