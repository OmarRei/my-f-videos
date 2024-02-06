document.addEventListener('DOMContentLoaded', function () {
  const container = document.querySelector('.container');
  const check24 = document.getElementById('check-24');
  const updateContainerButton = document.getElementById('updateContainerButton');

  function shuffle(array) {
    for (let i = array.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [array[i], array[j]] = [array[j], array[i]];
    }
  }

  function randomizeElements() {
    const elements = Array.from(container.children);
    shuffle(elements);
    container.innerHTML = '';
    elements.forEach(element => {
      container.appendChild(element);
    });
  }

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

  if (updateContainerButton) {
    updateContainerButton.addEventListener('click', function () {
      // Call the randomizeElements function to update the container
      randomizeElements();
    });
  }
});
