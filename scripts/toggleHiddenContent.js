document.addEventListener('DOMContentLoaded', function () {
  const hiddenContent = document.getElementById('hiddenContent');
  const showHiddenContentButton = document.getElementById('showHiddenContentButton');

  let passwordEntered = false;

  showHiddenContentButton.addEventListener('click', async function() {
    if (passwordEntered) {
      // If the password has already been entered, toggle the visibility of hidden content
      hiddenContent.style.display = hiddenContent.style.display === 'none' ? 'block' : 'none';
    } else {
      // Get the password from the user
      const password = prompt('Enter the password:');

      if (password !== null) {
        verifyPassword(password)
          .then(isCorrectPassword => {
            if (isCorrectPassword) {
              // If the password is correct, set the flag and toggle the visibility of hidden content
              passwordEntered = true;
              hiddenContent.style.display = 'block';
            } else {
              alert('Incorrect password. Please try again.');
            }
          })
          .catch(error => {
            console.error('Error verifying password:', error);
            alert('An error occurred while verifying the password.');
          });
      }
    }
  });

  // Function to hash a string using SHA-256
  async function sha256(str) {
    const encoder = new TextEncoder();
    const data = encoder.encode(str);
    return crypto.subtle.digest('SHA-256', data);
  }

  // Function to verify the entered password
  async function verifyPassword(enteredPassword) {
    try {
      // Fetch the hashed password from the external file (password.txt)
      const response = await fetch('./password.txt');
      if (!response.ok) {
        throw new Error('Error fetching password');
      }
      const hashedPasswordHex = await response.text();

      // Hash the entered password using SHA-256
      const hashedEnteredPassword = await sha256(enteredPassword);

      // Convert the hashed password to a hexadecimal string
      const hashedEnteredPasswordHex = Array.from(new Uint8Array(hashedEnteredPassword))
        .map(byte => byte.toString(16).padStart(2, '0'))
        .join('');

      // Check if the hashed entered password matches the hashed password from the file
      return hashedEnteredPasswordHex === hashedPasswordHex;
    } catch (error) {
      throw new Error('Error verifying password: ' + error.message);
    }
  }
});
