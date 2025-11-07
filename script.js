// Chatbot functionality
const chatbotFloatBtn = document.getElementById('chatbotFloatBtn');
const chatbotContainer = document.getElementById('chatbotContainer');
const chatbotToggle = document.getElementById('chatbotToggle');
const chatbotInput = document.getElementById('chatbotInput');
const chatbotSend = document.getElementById('chatbotSend');
const chatbotMessages = document.getElementById('chatbotMessages');

// Toggle chatbot
chatbotFloatBtn.addEventListener('click', () => {
    chatbotContainer.classList.add('active');
    chatbotFloatBtn.style.display = 'none';
    chatbotInput.focus();
});

chatbotToggle.addEventListener('click', () => {
    chatbotContainer.classList.remove('active');
    chatbotFloatBtn.style.display = 'flex';
});

// Send message
function sendMessage() {
    const message = chatbotInput.value.trim();
    if (!message) return;

    // Add user message to chat
    addMessage(message, 'user');
    chatbotInput.value = '';

    // Show typing indicator
    showTypingIndicator();

    // Send to backend
    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: message }),
    })
    .then(response => response.json())
    .then(data => {
        removeTypingIndicator();
        addMessage(data.response, 'bot');
    })
    .catch(error => {
        console.error('Error:', error);
        removeTypingIndicator();
        addMessage('Sorry, I encountered an error. Please make sure the backend server is running.', 'bot');
    });
}

chatbotSend.addEventListener('click', sendMessage);
chatbotInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Add message to chat
function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;

    const icon = document.createElement('i');
    icon.className = sender === 'bot' ? 'fas fa-robot' : 'fas fa-user';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const p = document.createElement('p');
    p.textContent = text;

    contentDiv.appendChild(p);
    messageDiv.appendChild(icon);
    messageDiv.appendChild(contentDiv);

    chatbotMessages.appendChild(messageDiv);
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
}

// Typing indicator
function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message typing-message';
    typingDiv.id = 'typingIndicator';

    const icon = document.createElement('i');
    icon.className = 'fas fa-robot';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';
    typingIndicator.innerHTML = '<span></span><span></span><span></span>';

    contentDiv.appendChild(typingIndicator);
    typingDiv.appendChild(icon);
    typingDiv.appendChild(contentDiv);

    chatbotMessages.appendChild(typingDiv);
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
}

function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Smooth scrolling for navigation
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});
