function search() {
    const searchTerm = document.querySelector('.searchTerm').value.toLowerCase();

    fetch('./container.txt')
        .then(response => response.text())
        .then(htmlContent => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(htmlContent, 'text/html');

            const container = document.querySelector('.container');
            container.innerHTML = '';

            const divs = doc.querySelectorAll('div');
            divs.forEach(div => {
                const h2 = div.querySelector('h2');
                if (h2 && h2.textContent.toLowerCase().includes(searchTerm)) {
                    container.innerHTML += `<div class="video" onclick="scrollToElement('${div.id}')">${div.innerHTML}</div>`;
                }
            });
        })
        .catch(error => console.error('Error fetching container.txt:', error));
}

function scrollToElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}
