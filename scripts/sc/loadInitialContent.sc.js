document.addEventListener('DOMContentLoaded', function () {
  const container = document.querySelector('.container');
  const loadMoreButton = document.getElementById('loadMore');
  const reverseOrderButton = document.getElementById('reverseOrder');
  let currentPage = 1;
  const itemsPerPage = 32;
  let videoElements = []; // Store video elements from container.txt

  function fetchContent() {
    fetch('./containersc.txt')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.text();
      })
      .then(data => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(data, 'text/html');

        videoElements = Array.from(doc.querySelectorAll('.video'));
        renderContent();
      })
      .catch(error => {
        console.error('Error fetching content:', error);
      });
  }

  function renderContent() {
    const startIndex = 0;
    const endIndex = currentPage * itemsPerPage;
    const currentElements = videoElements.slice(startIndex, endIndex);

    container.innerHTML = ''; // Clear container

    currentElements.forEach(element => {
      container.appendChild(element.cloneNode(true));
    });

    if (endIndex < videoElements.length) {
      loadMoreButton.style.display = 'block';
    } else {
      loadMoreButton.style.display = 'none';
    }
  }

  function loadMore() {
    currentPage++;
    renderContent();
  }

  function reverseOrder() {
    videoElements.reverse();
    renderContent();
  }

  // Event listeners
  loadMoreButton.addEventListener('click', loadMore);
  reverseOrderButton.addEventListener('click', reverseOrder);

  // Initial fetch when the page loads
  fetchContent();
});