// Inline execution of JavaScript code

/**
 * Reset the form when the window is loaded
 */
window.addEventListener('load', function () {
    form.reset();  // Resets all form elements to their default values
});


/*
* Add an event listener to the form to handle form submission and command execution
* Ensure the DOM is fully loaded before binding events
*/
document.addEventListener('DOMContentLoaded', () => {
    // Event Listener for Command Dropdown
    commandDropdown.addEventListener('change', () => {
        console.log('Command Dropdown changed');
        // Get the selected index
        const selectedCommandName = commandDropdown.value;

        // Retrieve the selected command object
        const selectedCommand = commands.find(cmd => cmd.command === selectedCommandName);


        if (selectedCommand.playable) {
            // Populate the player dropdown with players
            playerDropdown.innerHTML = ''; // Clear existing options
            players.forEach(player => {
                const option = document.createElement('option');
                option.value = player.id;
                option.textContent = player.id;
                playerDropdown.appendChild(option);
            });

            // Show the player dropdown
            playerDropdown.classList.remove('hidden');
        } else {
            // Hide the player dropdown
            playerDropdown.classList.add('hidden');
        }

        // Handle coordinate fields visibility
        if (selectedCommand.coordinates) {
            coordinateFields.classList.remove('hidden');
        } else {
            coordinateFields.classList.add('hidden');
            userInput.disabled = false; // Enable the input field
        }

        if (selectedCommand.time_input) {
            timeInput.classList.remove('hidden');
        } else {
            timeInput.classList.add('hidden');
        }

        console.log('Selected Command:', selectedCommand);
        console.log(selectedCommand.no_input)
        // Handle allowed user input
        if (selectedCommand.no_input) {
            userInput.value = ''; // Clear the input field
            userInput.disabled = true; // Disable the input field
            userInput.placeholder = "Cette commande ne nécessite pas d'entrée.";
            userInput.classList.add("hidden");
        } else {
            userInput.disabled = false; // Enable the input field
            userInput.placeholder = "Entrer votre instruction...";
            userInput.classList.remove("hidden");
        }

    });
});


