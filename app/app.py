from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    places = ["New York", "London", "Paris", "Tokyo", "Sydney"]
    commands = [
        {
            "command": "create-char",
            "description": "Create a new character",
        },
        {
            "command": "create-loc",
            "description": "Create a new location",
        },
        {
            "command": "create-object",
            "description": "Create a new object",
        },
        {
            "command": "action",
            "description": "Perform an action",
            "playable": True
        },
        {
            "command": "talk",
            "description": "Talk to other characters",
            "playable": True
        },
        {
            "command": "time",
            "description": "Advance the time",
        }
    ]

    players = [
        {
            "name": "Alice",
            "character": "Fizzlebang",
        },
        {
            "name": "Bob",
            "character": "Gandalf",
        },
        {
            "name": "Charlie",
            "character": "Goodguy",
        },
    ]

    messages = [
        {
            "from_master": True,
            "message": "Welcome, adventurer! How can I assist you in these lands filled with danger and mystery?",
        },
        {
            "player": "Goodguy",
            "message": "I'm looking for a way out of this dungeon. This place is cursed",
        },
        {
            "from_master": True,
            "message": "Dungeons are ancient traps, filled with powerful creatures and treacherous traps. Be cautious, every step could be your last.",
        },
    ]

    return render_template(
        'index.html',
        places=places,
        commands=commands,
        players=players,
        messages=messages
    )


if __name__ == '__main__':
    app.run(debug=True)
