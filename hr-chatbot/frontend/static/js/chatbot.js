// static/js/chatbot.js
document.addEventListener('DOMContentLoaded', () => {
    const chatbotToggle = document.getElementById('chatbot-toggle');
    const chatbotContainer = document.getElementById('chatbot-container');
    const chatbotClose = document.getElementById('chatbot-close');
    const chatbotInput = document.getElementById('chatbot-input');
    const chatbotSend = document.getElementById('chatbot-send');
    const chatbotMessages = document.getElementById('chatbot-messages');

    // Toggle chatbot visibility
    chatbotToggle.addEventListener('click', () => {
        chatbotContainer.classList.toggle('open');
    });

    // Close chatbot
    chatbotClose.addEventListener('click', () => {
        chatbotContainer.classList.remove('open');
    });

    // Send message function
    function sendMessage() {
        const messageText = chatbotInput.value.trim();
        if (messageText === '') return;

        // Add user message to chat
        addMessage(messageText, 'user');
        chatbotInput.value = '';

        // Simulate bot response (replace with actual Rasa API call)
        setTimeout(() => {
            simulateBotResponse(messageText);
        }, 500);
    }

    // Add message to chat
    function addMessage(text, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);
        messageElement.textContent = text;
        chatbotMessages.appendChild(messageElement);
        
        // Scroll to bottom
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    // Simulate bot response (placeholder for Rasa integration)
    function simulateBotResponse(userMessage) {
        let responses = {
            'hello': "Hi there! Welcome to Faith HR. How can I help you today?",
            'jobs': "We have several open positions in Engineering and HR. Would you like to know more?",
            'apply': "To apply, you can visit our careers page or ask me about specific job openings.",
            'default': "I'm here to help you with job inquiries. What would you like to know?"
        };

        // Simple keyword matching for demo
        const lowercaseMessage = userMessage.toLowerCase();
        let botResponse = responses['default'];

        if (lowercaseMessage.includes('hello') || lowercaseMessage.includes('hi')) {
            botResponse = responses['hello'];
        } else if (lowercaseMessage.includes('job') || lowercaseMessage.includes('career')) {
            botResponse = responses['jobs'];
        } else if (lowercaseMessage.includes('apply')) {
            botResponse = responses['apply'];
        }

        addMessage(botResponse, 'bot');
    }

    // Event listeners for sending messages
    chatbotSend.addEventListener('click', sendMessage);
    chatbotInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});