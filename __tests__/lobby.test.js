const { JSDOM } = require("jsdom");

describe("Lobby functionality", () => {
  let dom;
  let document;

  beforeEach(() => {
    dom = new JSDOM(`
      <span id="gameKey">ABC123</span>
      <button id="copyKey">Copy</button>
      <p id="copyStatus"></p>
    `, { runScripts: "dangerously" });
    document = dom.window.document;

    // Mock global.navigator.clipboard
    global.navigator = {
      clipboard: {
        writeText: jest.fn(() => Promise.resolve()),
      },
    };
  });

  test("Copies game key to clipboard", async () => {
    const copyButton = document.getElementById("copyKey");
    const status = document.getElementById("copyStatus");

    copyButton.addEventListener("click", async () => {
      const gameKey = document.getElementById("gameKey").textContent;
      await navigator.clipboard.writeText(gameKey);
      status.textContent = "Key copied!";
    });

    // Simulate button click
    copyButton.click();

    // Wait for clipboard operation to complete
    await new Promise((resolve) => setImmediate(resolve));

    // Assertions
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith("ABC123");
    expect(status.textContent).toBe("Key copied!");
  });
});
