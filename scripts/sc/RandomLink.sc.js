document.getElementById('randomHrefButton').addEventListener('click', function() {
  // Fetch content from container.txt
  fetch('./containersc.txt')
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
});
