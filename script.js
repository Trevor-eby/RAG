const chatBody = document.querySelector(".chat-body");
const messageInput = document.querySelector(".message-input");
const sendMessageButton = document.querySelector("#send-message");

const userData = {
    message: null
}


//Create message element with dynamic classes and return it
const createMessageElement = (content, ...classes) => {
    const div = document.createElement("div");
    div.classList.add("message", ...classes);
    div.innerHTML = content;
    return div;
}

//Handle outgoing user messages
const handleOutgoingMessage = (e) => {
    e.preventDefault();
    userData.message = messageInput.value.trim();
    messageInput.value = "";

    //Create and display user message
    const messageContent = `<div class="message-text"></div>`;

    const outgoingMessageDiv = createMessageElement(messageContent, "user-message");
    outgoingMessageDiv.querySelector(".message-text").textContent = userData.message;
    chatBody.appendChild(outgoingMessageDiv);

    //Simulate response with thinking indicator after a delay
    setTimeout(() => {
        const messageContent = `<i class="message-icon">
                    <i class="material-symbols-rounded">sentiment_satisfied</i>
                </i>
                <div class="message-text">
                    <div class="thinking-indicator">
                        <div class="dot"></div>
                        <div class="dot"></div>
                        <div class="dot"></div>
                    </div>
                </div>`;

        const incomingMessageDiv = createMessageElement(messageContent, "response-message", "thinking");
        chatBody.appendChild(incomingMessageDiv);
    }, 600);
}

//Handle Enter key press for sending messages
messageInput.addEventListener("keydown", (e) => {
    const userMessage = e.target.value.trim();
    if(e.key === "Enter" && userMessage) {
        handleOutgoingMessage(e);
    }
});

sendMessageButton.addEventListener("click", (e) => handleOutgoingMessage(e))