from flask import Flask, render_template, request
from packages import context, llm, util
from flask_cors import CORS
import json


app = Flask(__name__)

CORS(app)

def load_commands(path="config/commands.json"):
    with open(path, 'r') as file:
        return json.load(file)

def load_log(path="config/log.json"):
    with open(path, 'r') as file:
        return json.load(file)

@app.route('/')
def index():
    commands = load_commands(path="app/packages/config/commands.json")
    locations = context.load_locations(path="app/packages/locations")
    players = context.load_characters(path="app/packages/characters")
    messages = load_log(path="app/packages/config/log.json")


    return render_template(
        'index.html',
        locations=locations,
        commands=commands,
        players=players,
        messages=messages
    )

@app.route('/submit', methods=['POST'])
def submit():
    """
    Process the incoming request and return the appropriate response.
    """

    commands = load_commands(path="app/packages/config/commands.json")
    players = context.load_characters(path="app/packages/characters")

    # Retrieve form data safely
    command_name = request.form.get('command')
    player = request.form.get('player')
    user_input = request.form.get('prompt')

    # Find the matching command
    command = next((cmd for cmd in commands if cmd["command"] == command_name), None)

    # If the command is not found, return an error message
    if not command:
        return [{
            "from_master": True,
            "message": "Commande inconnue. Veuillez réessayer.",
        }]

    # Construct the prompt based on command and parameters
    if command.get("playable", False):
        if not player:  # Check if the command requires a player but none was provided
            return [{
                "from_master": True,
                "message": "Cette commande nécessite un joueur. Veuillez en sélectionner un.",
            }]
        prompt = f"/{command_name} /{player}/ {user_input}"
    else:
        prompt = f"/{command_name} {user_input}"

    # Get the response from the Master
    response = llm.completion(prompt)


    return [
        {
            "player": player if player is not None else "Administrator",
            "message": user_input,
        },
        {
            "from_master": True,
            "message": response,
        }
    ]






if __name__ == '__main__':
    app.run(debug=True)
