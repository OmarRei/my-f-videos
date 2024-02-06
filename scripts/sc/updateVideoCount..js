document.addEventListener('DOMContentLoaded', function() {
    // Fetch the content of the external file (container.txt)
    fetch('../container.txt')
      .then(response => response.text())
      .then(data => {
        // Create a temporary HTML element to parse the content
        const tempElement = document.createElement('div');
        tempElement.innerHTML = data;
  
        // Find all elements with class="video"
        const videoElements = tempElement.getElementsByClassName('video');
  
        // Get the count and update the page
        const videoCount = videoElements.length;
        document.getElementById('videoCount').innerText = videoCount;
      })
      .catch(error => {
        console.error('Error fetching container.txt:', error);
        document.getElementById('videoCount').innerText = 'Error loading content';
      });
  });
  