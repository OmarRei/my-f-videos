let videoUrls = [];
let currentVideoIndex = 0;

function loadPlaylist(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(event) {
        const playlistContent = event.target.result;
        const playlistItems = parsePlaylist(playlistContent);
        videoUrls = playlistItems.map(item => item.url);
        renderVideoList(playlistItems);
        playVideo(currentVideoIndex);
    };
    reader.readAsText(file);
}

function parsePlaylist(playlistContent) {
    const lines = playlistContent.split('\n');
    const playlistItems = [];
    let currentUrl = '';
    let currentName = '';

    for (const line of lines) {
        if (line.startsWith('#EXTINF:')) {
            currentName = line.substring(8).trim();
        } else if (line.trim().startsWith('http')) {
            currentUrl = line.trim();
            playlistItems.push({ name: currentName, url: currentUrl });
        }
    }

    return playlistItems;
}

function renderVideoList(playlistItems) {
    const videoListContainer = document.getElementById('videoList');
    videoListContainer.innerHTML = '';

    playlistItems.forEach((item, index) => {
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
    const videoPlayer = document.getElementById('videoPlayer');
    videoPlayer.innerHTML = '';

    const source = document.createElement('source');
    source.src = videoUrls[index];
    videoPlayer.appendChild(source);

    videoPlayer.load();
    videoPlayer.play();
    currentVideoIndex = index;
}

function playPreviousVideo() {
    if (currentVideoIndex > 0) {
        playVideo(currentVideoIndex - 1);
    } else {
        playVideo(videoUrls.length - 1);
    }
}

function playNextVideo() {
    if (currentVideoIndex < videoUrls.length - 1) {
        playVideo(currentVideoIndex + 1);
    } else {
        playVideo(0);
    }
}

function playRandomVideo() {
    const randomIndex = Math.floor(Math.random() * videoUrls.length);
    playVideo(randomIndex);
}
