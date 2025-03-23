let searchTimeout;

document.querySelector('.searchTerm').addEventListener('input', function(e) {
    // Clear the existing timeout
    clearTimeout(searchTimeout);
    
    // Set a new timeout
    searchTimeout = setTimeout(() => {
        const searchTerm = e.target.value.toLowerCase();
        const videos = document.querySelectorAll('.video');
        
        videos.forEach(video => {
            const title = video.querySelector('.video-title')?.textContent.toLowerCase() || '';
            const keywords = video.querySelector('.keywords')?.textContent.toLowerCase() || '';
            
            if (title.includes(searchTerm) || keywords.includes(searchTerm)) {
                video.style.display = '';
            } else {
                video.style.display = 'none';
            }
        });
    }, 2000); // 2 second delay
});

function search() {
    const searchTerms = document.querySelector('.searchTerm').value.toLowerCase().split(' ').filter(term => term.length > 0);
    if (searchTerms.length === 0) return;

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
                const keywords = div.querySelector('.keywords');
                const keywordsText = keywords ? keywords.textContent.toLowerCase() : '';
                
                const titleMatch = h2 && searchTerms.some(term => h2.textContent.toLowerCase().includes(term));
                const keywordMatch = keywords && searchTerms.some(term => keywordsText.includes(term));

                if (titleMatch || keywordMatch) {
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
