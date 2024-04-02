document.getElementById('showButton').addEventListener('click', function(event) {
    event.preventDefault();
    var videoLink = document.getElementById('videoURL').value;
    var videoId = getYouTubeVideoId(videoLink);
    if (videoId) {
        var embedCode = '<iframe width="560" height="315" src="https://www.youtube.com/embed/' + videoId + '" frameborder="0" allowfullscreen></iframe>';
        document.getElementById('videoPlayer').innerHTML = embedCode;
    } else {
        alert('Invalid YouTube video link. Please provide a valid link.');
    }
});

function getYouTubeVideoId(url) {
    var videoId = null;
    if (typeof url === 'string') {
        var regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
        var match = url.match(regExp);
        if (match && match[2].length === 11) {
            videoId = match[2];
        }
    }
    return videoId;
}
