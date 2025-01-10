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
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)

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
        return [{
            "user": "SYSTEM",
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
    try:
        response = llm.completion(prompt)

        print(response)

        if response is None:
            return []

        return [
            {
                "user": "MASTER",
                "message": response,
            },
            {
                "user": "SYSTEM",
                "message": response,
            },
            {
                "user": "FIGHT-DESCRIPTION",
                "message": response,
            },
            {
                "user": "goodguy",
                "message": response,
            }
        ]
    except Exception as e:
        return [
            {
                "user": "MASTER",
                "message": "Une erreur est survenue. Veuillez réessayer.",
            },
            {
                "user": "SYSTEM",
                "message": "Une erreur est survenue. Veuillez réessayer.",
            },
            {
                "user": "FIGHT_DESCRIPTION",
                "message": "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?.\n\nBut I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure. To take a trivial example, which of us ever undertakes laborious physical exercise, except to obtain some advantage from it? But who has any right to find fault with a man who chooses to enjoy a pleasure that has no annoying consequences, or one who avoids a pain that produces no resultant pleasure?",
            },
            {
                "user": "goodguy",
                "message": "Une erreur est survenue. Veuillez réessayer.",
            }
        ]



if __name__ == '__main__':
    app.run(debug=True)
