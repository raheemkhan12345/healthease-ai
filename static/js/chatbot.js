document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.querySelector('.chatbot-toggle');
    const chatWindow = document.querySelector('.chatbot-window');
    const closeBtn = document.querySelector('.chatbot-window .btn-close');
    const sendBtn = document.querySelector('.chatbot-input button');
    const inputField = document.querySelector('.chatbot-input input');
    const messagesContainer = document.querySelector('.chatbot-messages');
    
    // Toggle chat window
    toggleBtn.addEventListener('click', function() {
        chatWindow.classList.toggle('show');
    });
    
    // Close chat window
    closeBtn.addEventListener('click', function() {
        chatWindow.classList.remove('show');
    });
    
    // Send message
    function sendMessage() {
        const message = inputField.value.trim();
        if (message) {
            // Add user message
            addMessage('user', message);
            inputField.value = '';
            
            // Show typing indicator
            addMessage('bot', '...', true);
            
            // Send to server
            fetch('/chatbot/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({message: message})
            })
            .then(response => response.json())
            .then(data => {
                // Remove typing indicator
                const typing = document.querySelector('.typing');
                if (typing) typing.remove();
                
                if (data.response) {
                    addMessage('bot', data.response);
                } else if (data.error) {
                    addMessage('bot', 'Sorry, I encountered an error. Please try again later.');
                }
            })
            .catch(error => {
                const typing = document.querySelector('.typing');
                if (typing) typing.remove();
                addMessage('bot', 'Sorry, I encountered an error. Please try again later.');
            });
        }
    }
    
    // Send message on button click or Enter key
    sendBtn.addEventListener('click', sendMessage);
    inputField.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') sendMessage();
    });
    
    // Add message to chat
    function addMessage(sender, text, isTyping = false) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);
        if (isTyping) messageDiv.classList.add('typing');
        
        const bubble = document.createElement('div');
        bubble.classList.add('bubble');
        bubble.textContent = text;
        
        messageDiv.appendChild(bubble);
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    // Initial greeting
    addMessage('bot', 'Hello! I\'m HealthEase AI. How can I assist you with your health questions today?');
    
    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});