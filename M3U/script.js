let videoUrls = [];
let playlistItems = []; // Array to hold playlist items with name and URL
let currentVideoIndex = 0;

function loadPlaylist(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(event) {
        const playlistContent = event.target.result;
        playlistItems = parsePlaylist(playlistContent);
        renderVideoList(playlistItems);
        playVideo(currentVideoIndex);
    };
    reader.readAsText(file);
}

function parsePlaylist(playlistContent) {
    const lines = playlistContent.split('\n');
    const items = [];
    let currentName = '';

    for (const line of lines) {
        if (line.startsWith('#EXTINF:')) {
            currentName = line.substring(8).trim();
        } else if (line.trim().startsWith('http')) {
            const url = line.trim();
            items.push({ name: currentName, url });
        }
    }

    return items;
}

function renderVideoList(items) {
    const videoListContainer = document.getElementById('videoList');
    videoListContainer.innerHTML = '';

    items.forEach((item, index) => {
        const listItem = document.createElement('div');
        listItem.classList.add('videoListItem');

        const videoName = document.createElement('div');
        videoName.textContent = item.name || `Video ${index + 1}`;
        videoName.classList.add('videoName');

        listItem.appendChild(videoName);
        listItem.addEventListener('click', () => playVideo(index));
        videoListContainer.appendChild(listItem);
    });
}

function playVideo(index) {
    if (index < 0 || index >= playlistItems.length) return;

    const videoPlayer = document.getElementById('videoPlayer');
    videoPlayer.innerHTML = '';

    const source = document.createElement('source');
    source.src = playlistItems[index].url;
    videoPlayer.appendChild(source);

    videoPlayer.load();
    videoPlayer.play();
    currentVideoIndex = index;

    // Update video title (id="videoTitle") with the name of the current video
    const videoTitleContainer = document.getElementById('videoTitle');
    videoTitleContainer.textContent = `Video ${index + 1} is playing: ${playlistItems[index].name}`;
    
    // Update video name elements (class="videoName") with appropriate highlighting
    const videoNameElements = document.querySelectorAll('.videoName');
    videoNameElements.forEach((element, idx) => {
        if (idx === index) {
            element.classList.add('active'); // Apply active class to current video name
        } else {
            element.classList.remove('active'); // Remove active class from other video names
        }
    });
}

function playPreviousVideo() {
    const newIndex = (currentVideoIndex - 1 + playlistItems.length) % playlistItems.length;
    playVideo(newIndex);
}

function playNextVideo() {
    const newIndex = (currentVideoIndex + 1) % playlistItems.length;
    playVideo(newIndex);
}

function playRandomVideo() {
    const randomIndex = Math.floor(Math.random() * playlistItems.length);
    playVideo(randomIndex);
}
