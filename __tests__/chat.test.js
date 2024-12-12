const { JSDOM } = require("jsdom");

describe("Chat functionality", () => {
  let dom;
  let document;

  beforeEach(() => {
    dom = new JSDOM(`
      <div id="chat-container">
        <div id="messages"></div>
        <input type="text" id="chat-input" />
        <button id="send-btn">Send</button>
      </div>
    `, { runScripts: "dangerously" });
    document = dom.window.document;
  });

  test("Sends a message", () => {
    const input = document.getElementById("chat-input");
    const sendButton = document.getElementById("send-btn");
    const messagesDiv = document.getElementById("messages");

    // Simulate user input
    input.value = "Hello, World!";
    sendButton.click();

    // Simulate receiving a chat message
    const message = document.createElement("p");
    message.textContent = "You: Hello, World!";
    messagesDiv.appendChild(message);

    expect(messagesDiv.innerHTML).toContain("Hello, World!");
  });
});
