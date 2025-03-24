document.addEventListener('DOMContentLoaded', function () {
  const container = document.querySelector('.container');
  const loadMoreButton = document.getElementById('loadMore');
  const reverseOrderButton = document.getElementById('reverseOrder');
  let currentPage = 1;
  const itemsPerPage = 32;
  let videoElements = [];

  function fetchContent() {
    fetch('container.txt')
      .then(response => response.text())
      .then(data => {
        container.innerHTML = data;
        videoElements = Array.from(container.querySelectorAll('.video'));
        renderContent();
      })
      .catch(error => console.error('Error fetching content:', error));
  }

  function renderContent() {
    const startIndex = 0;
    const endIndex = currentPage * itemsPerPage;
    
    // Hide all videos first
    videoElements.forEach(el => el.style.display = 'none');
    
    // Show only the current page of videos
    videoElements.slice(startIndex, endIndex).forEach(el => el.style.display = '');

    loadMoreButton.style.display = endIndex < videoElements.length ? 'block' : 'none';
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