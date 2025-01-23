// Utility functions


/**
 * Function to close the overlay
 * @param {HTMLElement} info - The info container
 * @param {HTMLElement} overlay - The overlay
 */
function closeOverlay(info, overlay) {
    overlay.remove(); // Remove the overlay
    info.remove();    // Remove the info container
}

/**
 * Add event listener for every location card
 */
function update_locations_click_event(){
        locationItems.forEach(item => {
        item.addEventListener('click', (event) => {
            event.preventDefault(); // Prevent default link behavior

            // Remove existing overlay and info
            const existingOverlay = document.getElementById('overlay');
            const existingInfo = document.getElementById('info');
            if (existingOverlay) {
                existingOverlay.remove();
            }
            if (existingInfo) {
                existingInfo.remove();
            }

            // Get location ID (or name here for simplicity)
            const locationId = item.textContent.trim();
            const current_location = locations[item.dataset.index];  // Assuming 'locations' data is available
            console.log(current_location);

            // Darken the chat window
            const chatWindow = document.getElementById('chat');

            const overlay = document.createElement('div');
            overlay.id = "overlay";
            overlay.className = 'h-full w-full absolute bg-gray-900 bg-opacity-75 fixed top-0 left-0 z-10';

            // Create the overlay
            const info = document.createElement('div');
            info.id = 'info';

            info.className = 'absolute inset-0 z-30 flex justify-center items-center';
            info.innerHTML = `
                <div class="inset-0 bg-gradient-to-br from-gray-800 to-black text-white p-10 rounded-lg shadow-2xl relative h-5/6 w-full mx-16 " id="location-card">
                    <!-- Close Button -->
                    <button class="absolute top-4 right-4 text-gray-400 hover:text-gray-200 text-3xl" id="close-overlay">
                        ✕
                    </button>

                    <div class="py-8 h-full overflow-y-auto">
                    <!-- Location Info Header -->
                    <h2 class="text-4xl font-extrabold mb-6 text-center text-indigo-400">${current_location.nom}</h2>
                    <p class="text-gray-300 mb-8">${current_location.description}</p>

                    <!-- 2x2 Grid Layout for Sections -->
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        <!-- Coordinates Section -->
                        <div class="p-6 rounded-lg bg-gray-800">
                            <h3 class="text-xl font-semibold text-yellow-500 mb-3">Coordonnées</h3>
                            <p class="text-gray-400">X: ${current_location.position.x}</p>
                            <p class="text-gray-400">Y: ${current_location.position.y}</p>
                        </div>


                    </div>
                </div>
            `;

            chatWindow.append(overlay);
            // Append the overlay to the chat window
            chatWindow.appendChild(info);

            // Close functionality for the close button
            document.getElementById('close-overlay').addEventListener('click', () => {
                closeOverlay(info, overlay);
            });

            overlay.addEventListener('click', () => {
                console.log(
                    "Overlay clicked. Closing overlay..."
                )
                closeOverlay(info, overlay);
            });
        });
    });
}