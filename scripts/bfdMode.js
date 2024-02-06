document.addEventListener('DOMContentLoaded', function () {
    document.querySelector('.searchButton').addEventListener('click', function() {
      const searchTerm = document.querySelector('.searchTerm');
      const searchTermValue = searchTerm.value.trim().replace(/\s/g, '%20');
      const link = 'https://noodlemagazine.com/video/' + searchTermValue;
      window.open(link, '_blank');
    });
  });
  