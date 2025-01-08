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


commands = load_commands(path="app/packages/config/commands.json")
locations = context.load_locations(path="app/packages/locations")
players = context.load_characters(path="app/packages/characters")
messages = load_log(path="app/packages/config/log.json")


@app.route('/')
def index():


    return render_template(
        'index.html',
        locations=locations,
        commands=commands,
        players=players,
        messages=messages
    )

@app.route('/submit', methods=['POST'])
def submit():
    """Process the information, request and return the response"""

    # Retrieve the information from the form
    # Retrieve the information from the form
    command_name = request.form.get('command')  # Safely retrieve the command
    player = request.form.get('player')
    user_input = request.form.get('prompt')

    command = next((cmd for cmd in commands if cmd["command"] == command_name), None)

    prompt = None

    prompt = f"/{command_name} {user_input}"

    if command.get("playable", False):
        if player is None: return [
            {
                "message": "Cette commande ne peut pas être effectuée",
                "from_master": True
            }
        ]
        prompt = f"/{command_name} /{player}/ {user_input}"

    return [{
        "from_master": True,
        "message": prompt,
    },
        {
            "player": "Goodguy",
            "message": prompt,
        }
    ]








if __name__ == '__main__':
    app.run(debug=True)
