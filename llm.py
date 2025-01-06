import openai
import json
import os
import util

# Remplacez "YOUR_API_KEY" par votre clé API OpenAI : # Remplacez par votre clé API OpenAI accessible ici https://platform.openai.com/settings/organization/api-keys
openai.api_key = "YOUR_API_KEY"
# Fonction pour générer un personnage
def generate(prompt):
    try:
       
        # Appel à l'API OpenAI avec la nouvelle méthode
        content = "Tu es un assitant qui génère des objets, des personnages ou des lieux pour un jeu de rôle sous forme de JSON bien structuré."
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Modèle utilisé : mettre gpt-4o-mini
            messages=[
                {"role": "system", "content": content},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,  # Limite de tokens pour la réponse
            temperature=0.7  # Réglage de la créativité
        )
        
        # Extraire la réponse textuelle (modification de la manière d'accéder aux données)
        content = response.choices[0].message.content

        # Nettoyer la réponse pour enlever d'éventuels espaces supplémentaires
        content = content.strip()
        
        # Retourner la réponse nettoyée
        return content
    except Exception as e:
        return f"Une erreur s'est produite : {e}"

# Exécution du script
if __name__ == "__main__":
    if openai.api_key == "YOUR_API_KEY":
        openai.api_key = input("Enter your OpenAI API key: ")
    type = "locations"

    prompt = """Créer une boutique utile d'alchimiste. Donne un nom au lieu, une position avec des coordonnées x et y (entiers), et une description détaillée du lieu. Répondez sous la forme d'un JSON contenant les champs suivants : nom, position (coordonnées x et y), et description."""

    response = generate(prompt)

    # Vérifier si la réponse est valide avant de sauvegarder
    if (type =="characters"):
        try:
            # Tentative de conversion en JSON
            required_keys = ["nom","force","dextérité","constitution","sagesse","intelligence","charisme","pv","etat","description","inventaire","or","position"]
            util.save_markdown_to_json(response,required_keys,"characters")
        except Exception as e:
            print(f"Une erreur s'est produite : {e}")
    elif (type =="locations"):
        try:
            # Tentative de conversion en JSON
            required_keys = ["nom", "position", "description"]
            util.save_markdown_to_json(response, required_keys, "locations")
        except Exception as e:
            print(f"Une erreur s'est produite : {e}")
    
    print(response)
