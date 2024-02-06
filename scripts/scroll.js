document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('back-to-top-button').addEventListener('click', function() {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  
    document.getElementById('back-to-down-button').addEventListener('click', function() {
      window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    });
  });
  