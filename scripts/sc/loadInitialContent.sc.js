document.addEventListener('DOMContentLoaded', function () {
    const container = document.querySelector('.container');
    const loadMoreButton = document.getElementById('loadMore');
    let currentPage = 1;
    const itemsPerPage = 32;
  
    function fetchContent() {
      fetch('../containersc.txt')
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.text();
        })
        .then(data => {
          const parser = new DOMParser();
          const doc = parser.parseFromString(data, 'text/html');
  
          const videoElements = doc.querySelectorAll('.video');
          const startIndex = 0;  // Start from the beginning for initial content
          const endIndex = currentPage * itemsPerPage;
  
          const currentElements = Array.from(videoElements).slice(startIndex, endIndex);
  
          currentElements.forEach(element => {
            container.appendChild(element.cloneNode(true));
          });
  
          if (endIndex < videoElements.length) {
            loadMoreButton.style.display = 'block';
          } else {
            loadMoreButton.style.display = 'none';
          }
        })
        .catch(error => {
          console.error('Error fetching content:', error);
        });
    }
  
    function loadMore() {
      currentPage++;
      fetchContent();
    }
  
    // Event listener for the loadMoreButton
    loadMoreButton.addEventListener('click', loadMore);
  
    // Initial fetch when the page loads
    fetchContent();
  });
  