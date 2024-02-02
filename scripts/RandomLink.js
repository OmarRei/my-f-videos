document.getElementById('randomHrefButton').addEventListener('click', function() {
  // Fetch content from container.txt
  fetch('./container.txt')
    .then(response => response.text())
    .then(data => {
      // Extract href links from the content
      var links = data.match(/href="([^"]+)"/g).map(function(match) {
        return match.substring(6, match.length - 1);
      });

      // Shuffle the links array
      for (let i = links.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [links[i], links[j]] = [links[j], links[i]];
      }

      // Open two random links
      if (links.length > 1) {
        window.open(links[0], '_blank');
        window.open(links[1], '_blank');
      } else if (links.length === 1) {
        window.open(links[0], '_blank');
        alert('Only one link found in container.txt. Opening one link.');
      } else {
        alert('No links found in container.txt');
      }
    })
    .catch(error => {
      console.error('Error fetching container.txt:', error);
    });
});
