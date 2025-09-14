document.addEventListener("DOMContentLoaded", function () {
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");
    const sendButton = document.querySelector(".chat-input button");
    const typingIndicator = document.getElementById("typing-indicator");

    // Açılış mesajı
    appendMessage("bot", "🤖 Hi, I'm TripMate! How can I help you? Are you looking for information about a specific destination or just want some general travel advice?");

    sendButton.addEventListener("click", sendMessage);
    userInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    });

    async function sendMessage() {
        let message = userInput.value.trim();
        if (message === "") return;

        // Kullanıcının mesajını ekle
        appendMessage("user", message);
        userInput.value = "";

        // Typing animasyonu göster
        typingIndicator.style.display = "block";

        try {
            const response = await fetch("/chat_bot/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ message: message }),
            });

            const data = await response.json();

            // Typing gizle
            typingIndicator.style.display = "none";

            if (data.error) {
                appendMessage("bot", `❌ Error: ${data.error}`);
            } else {
                appendMessage("bot", `🤖 ${data.reply}`);
            }

        } catch (error) {
            typingIndicator.style.display = "none";
            appendMessage("bot", `❌ Connection error: ${error.message}`);
        }
    }

    function appendMessage(sender, text) {
        const messageElement = document.createElement("p");
        messageElement.classList.add("chat-message");

        if (sender === "user") {
            messageElement.classList.add("user-message");
        } else {
            messageElement.classList.add("bot-message");
        }

        messageElement.textContent = text;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    }
});
