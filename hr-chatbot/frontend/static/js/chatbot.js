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

    // Send message to Rasa via Flask backend
    async function sendMessageToRasa(message) {
        try {
            const response = await fetch('/webhook', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            return data.response.text;
        } catch (error) {
            console.error('Error:', error);
            return "Sorry, I'm having trouble connecting to the server. Please try again later.";
        }
    }

    // Send message function
    async function sendMessage() {
        const messageText = chatbotInput.value.trim();
        if (messageText === '') return;

        // Add user message to chat
        addMessage(messageText, 'user');
        chatbotInput.value = '';

        // Show typing indicator
        const typingIndicator = document.createElement('div');
        typingIndicator.classList.add('message', 'bot-message');
        typingIndicator.textContent = '...';
        typingIndicator.id = 'typing-indicator';
        chatbotMessages.appendChild(typingIndicator);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;

        try {
            const response = await fetch('/webhook', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: messageText })
            });
            
            if (!response.ok) throw new Error('Network response was not ok');
            
            const data = await response.json();
            
            // Remove typing indicator
            document.getElementById('typing-indicator')?.remove();
            
            // Process all responses
            data.responses.forEach(response => {
                if (response.type === 'text') {
                    // Preserve newlines by converting them to <br>
                    const formattedText = response.content.replace(/\n/g, '<br>');
                    addMessage(formattedText, 'bot', true);
                } else if (response.type === 'buttons') {
                    addButtons(response.content);
                }
            });
        } catch (error) {
            console.error('Error:', error);
            document.getElementById('typing-indicator')?.remove();
            addMessage("Sorry, I'm having trouble connecting. Please try again.", 'bot');
        }
    }
    

    // Add message to chat
    function addMessage(text, sender, isHTML = false) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);
        
        if (isHTML) {
            messageElement.innerHTML = text;
        } else {
            messageElement.textContent = text;
        }
        
        chatbotMessages.appendChild(messageElement);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    function addButtons(buttons) {
        const buttonContainer = document.createElement('div');
        buttonContainer.classList.add('button-container');
        
        buttons.forEach(button => {
            const btn = document.createElement('button');
            btn.classList.add('chat-button');
            btn.textContent = button.title;
            btn.onclick = () => {
                addMessage(button.title, 'user');
                sendMessageToRasa(button.payload);
            };
            buttonContainer.appendChild(btn);
        });
        
        chatbotMessages.appendChild(buttonContainer);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    // Event listeners for sending messages
    chatbotSend.addEventListener('click', sendMessage);
    chatbotInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});