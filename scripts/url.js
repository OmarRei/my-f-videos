// Function to generate a random query parameter
function generateRandomQuery() {
    var query = '';
    var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    var charactersLength = characters.length;
    for (var i = 0; i < 8; i++) {
        query += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return query;
}

// Function to generate a random path
function generateRandomPath() {
    var path = 'my-f-videos/main.html'; // Maintain the base path
    return path;
}

// Delay execution by 5 seconds
setTimeout(function() {
    // Generate a new random query parameter and path
    var newQuery = generateRandomQuery();
    var newPath = generateRandomPath();

    // Update the URL with the new query parameter and path
    var url = new URL(window.location.href);
    url.searchParams.set('query', newQuery);
    url.pathname = newPath;
    window.history.replaceState({}, '', url.toString());
}, 5000); // 5000 milliseconds = 5 seconds
