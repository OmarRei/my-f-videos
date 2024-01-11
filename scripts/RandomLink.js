// script.js

// Function to open a random href from elements with class "container"
function openRandomHref() {
  // Get all elements with class "container"
  var containerElements = document.querySelectorAll('.container a');

  // Generate a random index
  var randomIndex = Math.floor(Math.random() * containerElements.length);

  // Get the href value at the random index
  var randomHref = containerElements[randomIndex].href;

  // Open the random href in a new tab or window
  window.open(randomHref, '_blank');
}

// Attach the function to the button click event
document.getElementById('randomHrefButton').addEventListener('click', openRandomHref);
