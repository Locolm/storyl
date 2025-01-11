from flask import Flask, render_template, request
from packages import context, llm, util
from flask_cors import CORS
import json
import traceback
from datetime import datetime


app = Flask(__name__)

CORS(app)

def load_commands(path="config/commands.json"):
    """
    Load the commands list from the command files.
    In deployment mode, the path should include app/packages/ as a prefix.
    """
    with open(path, 'r') as file:
        return json.load(file)

def load_log(path="config/log.json"):
    """
    Load the log from the log file.
    In deployment mode, the path should include app/packages/ as a prefix.
    """
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)

def append_log(message_object, path="config/backend_logs.json"):
    """
    Append a message to the log file.
    Be careful with the default value of the path parameter
    """
    logs = load_log(path)
    logs.append(message_object)
    with open (path, 'w', encoding='utf-8') as file:
        json.dump(logs, file, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    commands = load_commands(path="app/packages/config/commands.json")
    locations = context.load_locations(path="app/packages/locations")
    players = context.load_characters(path="app/packages/characters")
    logs = load_log(path="app/packages/config/log.json")


    return render_template(
        'index.html',
        locations=locations,
        commands=commands,
        players=players,
        logs=logs
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

        append_log(
            {
                "timestamp": datetime.now().isoformat(),
                "user": "SYSTEM_ERROR",
                "command": command_name,
                "user_input": user_input,
                "output_error": "Commande inconnue. Veuillez réessayer.",
            },
            path="app/packages/config/backend_logs.json"
        )

        return [{
            "user": "SYSTEM",
            "message": "Commande inconnue. Veuillez réessayer.",
        }]

    # Construct the prompt based on command and parameters
    if command.get("playable", False):
        if not player:  # Check if the command requires a player but none was provided

            append_log(
                {
                    "timestamp": datetime.now().isoformat(),
                    "user": "SYSTEM_ERROR",
                    "command": command_name,
                    "user_input": user_input,
                    "output_error": "Cette commande nécessite un joueur. Veuillez en sélectionner un.",
                },
                path="app/packages/config/backend_logs.json"
            )

            return [{
                "from_master": True,
                "message": "Cette commande nécessite un joueur. Veuillez en sélectionner un.",
            }]
        prompt = f"/{command_name} /{player}/ {user_input}"
    else:
        prompt = f"/{command_name} {user_input}"

    # Get the response from the Master
    try:
        response = llm.completion(prompt)

        if response is None:
            return []

        # Append the log
        append_log(
            {
                "timestamp": datetime.now().isoformat(),
                "user": player if player else "ADMIN",
                "command": command_name,
                "user_input": user_input,
                "prompt": prompt,
                "output_error": response,
            },
            path="app/packages/config/backend_logs.json"
        )

        return [
            {
                "user": "MASTER",
                "message": response,
            }
        ]
    except Exception as e:
        # Append the log
        append_log(
            {
                "timestamp": datetime.now().isoformat(),
                "user": "SYSTEM_ERROR",
                "prompt": prompt,
                "stack_trace": traceback.format_exc(),
                "output_error": str(e),
            },
            path="app/packages/config/backend_logs.json"
        )

        return [
            {
                "user": "SYSTEM",
                "message": "Une erreur est survenue. Veuillez réessayer.",
            }
        ]

if __name__ == '__main__':
    app.run(debug=True)
