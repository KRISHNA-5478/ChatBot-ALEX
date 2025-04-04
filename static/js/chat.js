document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const clearChatBtn = document.getElementById('clearChatBtn');
    const emotionBadge = document.getElementById('emotion-badge');
    const recommendationsContainer = document.getElementById('recommendations-container');
    const hindiSearchInput = document.getElementById('hindi-search-input');
    const hindiSearchButton = document.getElementById('hindi-search-button');
    const hindiSearchResults = document.getElementById('hindi-search-results');
    const hindiMoodButtons = document.querySelectorAll('.hindi-mood-btn');
    
    // Event Listeners
    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => e.key === 'Enter' && sendMessage());
    clearChatBtn.addEventListener('click', clearChat);
    hindiSearchButton.addEventListener('click', searchHindiSongs);
    hindiSearchInput.addEventListener('keypress', (e) => e.key === 'Enter' && searchHindiSongs());
    hindiMoodButtons.forEach(button => button.addEventListener('click', () => getHindiRecommendations(button.getAttribute('data-mood'))));
    
    function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;
        
        addUserMessage(message);
        userInput.value = '';
        showLoading();
        
        fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            data.error ? addBotMessage(`Sorry, an error occurred: ${data.error}`) : processResponse(data);
        })
        .catch(() => {
            hideLoading();
            addBotMessage("Sorry, Alex encountered an error. Please try again.");
        });
    }

    function processResponse(data) {
        addBotMessage(data.message);
        if (data.emotion) updateEmotionDisplay(data.emotion);
        if (data.songs) updateSongRecommendations(data.songs);
        scrollToBottom();
    }

    function addUserMessage(message) {
        addMessage(message, 'user-message');
    }

    function addBotMessage(message) {
        addMessage(message, 'bot-message');
    }

    function addMessage(content, type) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${type}`;
        
        messageElement.innerHTML = `
            <div class="message-content">${escapeHtml(content).replace(/\n/g, '<br>')}</div>
            <span class="message-time">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
        `;
        
        chatMessages.appendChild(messageElement);
        scrollToBottom();
    }

    function showLoading() {
        const loadingElement = document.createElement('div');
        loadingElement.className = 'message bot-message';
        loadingElement.id = 'loading-message';
        loadingElement.innerHTML = '<div class="loading">' + '.'.repeat(3).split('').map(() => '<div class="loading-dot"></div>').join('') + '</div>';
        chatMessages.appendChild(loadingElement);
        scrollToBottom();
    }

    function hideLoading() {
        document.getElementById('loading-message')?.remove();
    }

    function updateEmotionDisplay(emotion) {
        emotionBadge.textContent = capitalizeFirstLetter(emotion.name);
        emotionBadge.className = `badge emotion-${emotion.name}`;
    }

    function updateSongRecommendations(songs) {
        recommendationsContainer.innerHTML = songs?.length ? songs.map(song => `
            <div class="song-item">
                <div class="song-title"><a href="${song.url}" target="_blank">${song.name}</a></div>
                <div class="song-artist">${song.artist}</div>
            </div>`).join('') : '<p class="text-muted">No recommendations available.</p>';
    }

    function clearChat() {
        if (!confirm('Clear chat history?')) return;
        
        fetch('/clear_chat', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                chatMessages.innerHTML = '';
                addBotMessage("Hello! I'm Alex, your Emotion Music Recommender. How are you feeling today?");
                emotionBadge.textContent = 'Neutral';
                emotionBadge.className = 'badge bg-secondary';
                recommendationsContainer.innerHTML = '<p class="text-muted">Start chatting to get music suggestions.</p>';
            }
        })
        .catch(console.error);
    }

    function searchHindiSongs() {
        const query = hindiSearchInput.value.trim();
        if (!query) return;
        
        hindiSearchResults.innerHTML = '<p class="text-center"><i class="fas fa-spinner fa-spin"></i> Searching...</p>';
        fetch('/search_hindi_songs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        })
        .then(response => response.json())
        .then(data => displayHindiSearchResults(data, query))
        .catch(() => hindiSearchResults.innerHTML = '<p class="text-danger">Error searching. Try again.</p>');
    }

    function displayHindiSearchResults(data, query) {
        hindiSearchResults.innerHTML = data.songs?.length ? 
            `<h6><i class="fas fa-search"></i> Results for "${query}"</h6>` + 
            data.songs.map(song => `
                <div class="song-item">
                    <div class="song-title"><a href="${song.url}" target="_blank">${song.name}</a></div>
                    <div class="song-artist">${song.artist}</div>
                </div>`).join('') : '<p class="text-muted">No results found.</p>';
    }

    function getHindiRecommendations(mood) {
        hindiSearchResults.innerHTML = '<p class="text-center"><i class="fas fa-spinner fa-spin"></i> Finding songs...</p>';
        fetch(`/hindi_recommendations/${mood}`)
        .then(response => response.json())
        .then(data => displayHindiSearchResults(data, mood))
        .catch(() => hindiSearchResults.innerHTML = '<p class="text-danger">Error loading recommendations.</p>');
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function capitalizeFirstLetter(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    function escapeHtml(unsafe) {
        return unsafe.replace(/[&<>"]/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[char]));
    }

    scrollToBottom();
});
