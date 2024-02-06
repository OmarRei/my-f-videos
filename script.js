document.addEventListener('DOMContentLoaded', function () {
  const hiddenContent = document.getElementById('hiddenContent');
  const showHiddenContentButton = document.getElementById('showHiddenContentButton');
  const container = document.querySelector('.container');
  const check24 = document.getElementById('check-24');
  const updateContainerButton = document.getElementById('updateContainerButton');
  const loadMoreButton = document.getElementById('loadMore');

  let currentPage = 1;
  const itemsPerPage = 32;

  function scrollToTop() {
      window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function scrollToBottom() {
      window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
  }

  function convertToBFDModeAndOpenLink() {
      const searchTerm = document.querySelector('.searchTerm');
      const searchTermValue = searchTerm.value.trim().replace(/\s/g, '%20');
      const link = 'https://noodlemagazine.com/video/' + searchTermValue;
      window.open(link, '_blank');
  }

  // Function to hash a string using SHA-256
  async function sha256(str) {
      const encoder = new TextEncoder();
      const data = encoder.encode(str);
      return crypto.subtle.digest('SHA-256', data);
  }

  // Function to handle button click
  async function toggleHiddenContent() {
      // Get the password from the user
      const password = prompt('Enter the password:');

      // Hash the entered password using SHA-256
      const hashedPassword = await sha256(password);

      // Convert the hashed password to a hexadecimal string
      const hashedPasswordHex = Array.from(new Uint8Array(hashedPassword))
          .map(byte => byte.toString(16).padStart(2, '0'))
          .join('');

      // Check if the hashed password matches the expected value
      if (hashedPasswordHex === 'fe1128a78348e3ef41d826ba69baacdbc1c89eddfee10cdab8d079aa33947a11') {
          // If the password is correct, toggle the visibility of hidden content
          hiddenContent.style.display = hiddenContent.style.display === 'none' ? 'block' : 'none';
      } else {
          alert('Incorrect password. Please try again.');
      }
  }

  // Fisher-Yates shuffle algorithm
  function shuffle(array) {
      for (let i = array.length - 1; i > 0; i--) {
          const j = Math.floor(Math.random() * (i + 1));
          [array[i], array[j]] = [array[j], array[i]];
      }
  }

  // Function to randomize elements in the container
  function randomizeElements() {
      const elements = Array.from(container.children);
      shuffle(elements);
      container.innerHTML = '';
      elements.forEach(element => {
          container.appendChild(element);
      });
  }

  // Function to fetch content from an external file
  function fetchContent() {
      fetch('container.txt')
          .then(response => {
              if (!response.ok) {
                  throw new Error('Network response was not ok');
              }
              return response.text();
          })
          .then(data => {
              // Parse the data into HTML elements
              const parser = new DOMParser();
              const doc = parser.parseFromString(data, 'text/html');

              // Select all the video elements
              const videoElements = doc.querySelectorAll('.video');

              // Calculate the start and end indices for the current page
              const startIndex = (currentPage - 1) * itemsPerPage;
              const endIndex = currentPage * itemsPerPage;

              // Extract the elements for the current page
              const currentElements = Array.from(videoElements).slice(startIndex, endIndex);

              // Append the elements for the current page to the container
              currentElements.forEach(element => {
                  container.appendChild(element.cloneNode(true));
              });

              // Check if there are more pages
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

  // Function to load more content
  function loadMore() {
      currentPage++;
      fetchContent();
  }

  // Event listener for the loadMoreButton
  if (loadMoreButton) {
      loadMoreButton.addEventListener('click', loadMore);
  }

  // Event listener for the check-24 checkbox
  if (check24 && updateContainerButton) {
      check24.addEventListener('change', function () {
          // If the checkbox is checked, show the updateContainerButton
          updateContainerButton.style.display = check24.checked ? 'inline-block' : 'none';

          // If the checkbox is checked, randomize the elements
          if (check24.checked) {
              randomizeElements();
          }
      });
  }

  // Event listener for the updateContainerButton
  if (updateContainerButton) {
      updateContainerButton.addEventListener('click', function () {
          // Call the randomizeElements function to update the container
          randomizeElements();
      });
  }

  // Event listeners
  if (showHiddenContentButton) {
      showHiddenContentButton.addEventListener('click', toggleHiddenContent);
  }

  document.getElementById('back-to-top-button').addEventListener('click', scrollToTop);
  document.getElementById('back-to-down-button').addEventListener('click', scrollToBottom);
  document.querySelector('.searchButton').addEventListener('click', convertToBFDModeAndOpenLink);

  // Initial fetch when the page loads
  fetchContent();
});
