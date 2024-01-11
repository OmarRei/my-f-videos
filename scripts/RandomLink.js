document.getElementById('randomHrefButton').addEventListener('click', function() {
    // Fetch content from container.txt
    fetch('../container.txt')
        .then(response => response.text())
        .then(data => {
            // Extract href links from the content
            var links = data.match(/href="([^"]+)"/g).map(function(match) {
                return match.substring(6, match.length - 1);
            });

            // Open a random link
            if (links.length > 0) {
                var randomIndex = Math.floor(Math.random() * links.length);
                window.open(links[randomIndex], '_blank');
            } else {
                alert('No links found in container.txt');
            }
        })
        .catch(error => {
            console.error('Error fetching container.txt:', error);
        });
});
