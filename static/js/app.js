// Telegram Web App Integration
let tg = window.Telegram.WebApp;

// Initialize Telegram Web App
tg.ready();
tg.expand();

// Set main button
tg.MainButton.text = "Close";
tg.MainButton.show();
tg.MainButton.onClick(() => {
    tg.close();
});

// Chat functionality
let messageCount = 0;
const adFrequency = 3; // Show ad every 3 messages

document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');
    const chatContainer = document.getElementById('chat-container');
    
    // Initialize RichAds after page load
    initializeRichAds();
    
    // Send message functionality
    sendBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    async function sendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        addMessage(message, 'user');
        messageInput.value = '';
        messageCount++;
        
        // Show loading
        const loadingDiv = addMessage('Thinking...', 'ai', true);
        
        try {
            // Send to bot API
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    user_id: tg.initDataUnsafe?.user?.id || 'web_user'
                })
            });
            
            const data = await response.json();
            
            // Remove loading message
            loadingDiv.remove();
            
            // Add AI response
            addMessage(data.response, 'ai');
            
            // Show ads based on frequency
            if (messageCount % adFrequency === 0) {
                showRandomAd();
            }
            
        } catch (error) {
            loadingDiv.remove();
            addMessage('Sorry, there was an error processing your request.', 'ai');
        }
    }
    
    function addMessage(text, type, isLoading = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        if (type === 'user') {
            messageDiv.innerHTML = `<strong>You:</strong> ${text}`;
        } else {
            messageDiv.innerHTML = isLoading ? 
                `<div class="loading">${text}</div>` : 
                `<strong>Gemini AI:</strong> ${text}`;
        }
        
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        return messageDiv;
    }
});

// RichAds Integration Functions
function initializeRichAds() {
    // Initialize embedded banner
    if (typeof richads !== 'undefined') {
        // Load embedded banner ad
        richads('show', {
            type: 'banner',
            id: richAdsConfig.embeddedBanner,
            container: 'embedded-banner'
        });
        
        // Initialize push notifications (if configured)
        richads('push', {
            id: richAdsConfig.pushStyle
        });
    }
}

function showRandomAd() {
    const adTypes = ['interstitial', 'video'];
    const randomType = adTypes[Math.floor(Math.random() * adTypes.length)];
    
    if (randomType === 'interstitial') {
        showInterstitialAd();
    } else {
        showVideoAd();
    }
}

function showInterstitialAd() {
    if (typeof richads !== 'undefined') {
        richads('show', {
            type: 'interstitial',
            id: richAdsConfig.interstitialBanner,
            onClose: function() {
                console.log('Interstitial ad closed');
            },
            onError: function(error) {
                console.log('Interstitial ad error:', error);
            }
        });
    }
}

function showVideoAd() {
    if (typeof richads !== 'undefined') {
        richads('show', {
            type: 'video',
            id: richAdsConfig.interstitialVideo,
            onComplete: function() {
                console.log('Video ad completed');
                // Optional: Give user reward for watching video
                tg.showAlert('Thanks for watching! You support our free service.');
            },
            onError: function(error) {
                console.log('Video ad error:', error);
            }
        });
    }
}

// Telegram Web App event handlers
tg.onEvent('mainButtonClicked', function() {
    tg.close();
});

// Handle back button
tg.onEvent('backButtonClicked', function() {
    tg.close();
});

// Send data back to bot when closing
window.addEventListener('beforeunload', function() {
    tg.sendData(JSON.stringify({
        action: 'close',
        messages_sent: messageCount
    }));
});
