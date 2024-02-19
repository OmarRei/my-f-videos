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
    var path = 'main.html'; // Maintain the base path
    return path;
}

// Function to update URL with random query parameter and path
function updateURL() {
    // Generate a new random query parameter and path
    var newQuery = generateRandomQuery();
    var newPath = generateRandomPath();

    // Update the URL with the new query parameter and path
    var url = new URL(window.location.href);
    url.searchParams.set('query', newQuery);
    url.pathname = newPath;
    window.history.replaceState({}, '', url.toString());
}

// Function to fetch and open random links
function openRandomLinks() {
    // Fetch content from container.txt
    fetch('./container.txt')
        .then(response => response.text())
        .then(data => {
            // Extract href links from the content
            var links = data.match(/href="([^"]+)"/g).map(function(match) {
                return match.substring(6, match.length - 1);
            });

            // Open a random link in a new tab
            if (links.length >= 2) {
                var randomIndex1 = Math.floor(Math.random() * links.length);
                var randomIndex2 = Math.floor(Math.random() * (links.length - 1));
                randomIndex2 = (randomIndex2 >= randomIndex1) ? randomIndex2 + 1 : randomIndex2;
            
                window.open(links[randomIndex1], '_blank');
                window.open(links[randomIndex2], '_blank');
            } else if (links.length === 1) {
                // Open the single link in a new tab
                window.open(links[0], '_blank');
            } else {
                alert('Not enough links found in container.txt to open two tabs.');
            }
            
        })
        .catch(error => {
            console.error('Error fetching container.txt:', error);
        });
}

// Delay execution by 5 seconds
setTimeout(function() {
    updateURL(); // Update URL after 5 seconds
}, 5000);

// Event listener for clicking randomHrefButton
document.getElementById('randomHrefButton').addEventListener('click', openRandomLinks);
