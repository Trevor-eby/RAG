const chatBody = document.querySelector(".chat-body");
const messageInput = document.querySelector(".message-input");
const sendMessageButton = document.querySelector("#send-message");
const fileInput = document.querySelector("#file-input");

const BASE_URL = window.location.origin;

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
async function generateResponse(message) {
    try {
        const response = await fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query_text: message })
    });


    if (!response.ok) {
      const text = await response.text();  // Get plain text error
      throw new Error(`Server error: ${text}`);
    }

    const data = await response.json();
    return data.answer;

  } catch (error) {
    console.error("Error:", error.message);
    return "Sorry, something went wrong.";
  }
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

fileInput.addEventListener("change", async () => {
    const file = fileInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    console.log("Uploading file:", file.name);

    const fileMessageDiv = document.createElement("div");
    fileMessageDiv.classList.add("message", "user-message");

    const userMessageDiv = createMessageElement(`
        <div class="message-text">
            <i class="message-icon">
                <i class="material-symbols-rounded">file_present</i>
            </i>
            ${file.name}
        </div>`, "user-message");
    chatBody.appendChild(userMessageDiv);


    chatBody.appendChild(fileMessageDiv);
    chatBody.scrollTop = chatBody.scrollHeight;

    try {
        const response = await fetch(`${BASE_URL}/upload`, {
        method: "POST",
        body: formData,
    });

    console.log("Response status:", response.status);

    if (!response.ok) {
        let errorMsg = "Unknown error";
        try {
            const errorResult = await response.json();
            errorMsg = errorResult.detail || JSON.stringify(errorResult);
        } 
        catch {
            errorMsg = await response.text();
        }
        throw new Error(errorMsg);
    }

    const result = await response.json();
    console.log("Upload success:", result);
    alert(result.message || "File uploaded successfully!");

    const chatBox = document.querySelector(".chat-body");
    const userMessage = document.createElement("div");
    userMessage.className = "message user-message";

    } 
    catch (error) {
        console.error("Upload failed:", error);
        //alert("File upload failed: " + error.message);
    }
});

// Handle send button click
sendMessageButton.addEventListener("click", (e) => {
    handleOutgoingMessage(e);
});

document.querySelector("#file-upload").addEventListener("click", () => fileInput.click());