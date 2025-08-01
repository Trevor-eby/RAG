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
};

//Generate response
async function generateResponse(question) {
    const response = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json"},
        body: JSON.stringify({ query_text: question }),
    });

    const data = await response.json();
    return data.response;
}

//Handle outgoing user messages
const handleOutgoingMessage = async (e) => {
    e.preventDefault();
    const message = messageInput.value.trim();
    //userData.message = messageInput.value.trim();
    if(!message) return;

    //Clears input
    messageInput.value = "";

    // Show user message immediately
    const userMessageDiv = createMessageElement(`<div class="message-text">${message}</div>`, "user-message");
    chatBody.appendChild(userMessageDiv);

    // Add loading indicator (thinking...)
    const loadingDiv = createMessageElement(
        `<i class="message-icon">
            <i class="material-symbols-rounded">sentiment_satisfied</i>
        </i>
        <div class="message-text">
            <div class="thinking-indicator">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
        </div>`,
        "response-message",
        "thinking"
    );
    chatBody.appendChild(loadingDiv);

    //Await the actual response
    const responseText = await generateResponse(message);

    // Scroll to bottom
    chatBody.scrollTop = chatBody.scrollHeight;

    try {
        // Replace loading indicator with response
        loadingDiv.classList.remove("thinking");
        loadingDiv.innerHTML = `<div class="message-text">${responseText}</div>`;

        // Scroll to bottom again after response
        chatBody.scrollTop = chatBody.scrollHeight;
    }
    catch (error) {
        loadingDiv.classList.remove("thinking");
        loadingDiv.innerHTML = `<div class="message-text">Error getting response.</div>`;
        console.error("Error:", error);
    }

    // Scroll to bottom again
    chatBody.scrollTop = chatBody.scrollHeight;
}

//Handle Enter key press for sending messages
messageInput.addEventListener("keydown", (e) => {
    const userMessage = e.target.value.trim();
    if(e.key === "Enter" && userMessage) {
        handleOutgoingMessage(e);
    }
});

// Handle send button click
sendMessageButton.addEventListener("click", (e) => {
    handleOutgoingMessage(e);
});