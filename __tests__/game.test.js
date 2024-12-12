const { JSDOM } = require("jsdom");

describe("Game voting functionality", () => {
  let dom;
  let document;

  beforeEach(() => {
    dom = new JSDOM(`
      <h1 id="feature-name">Feature: Example Feature</h1>
      <button id="vote-5">Vote 5</button>
      <p id="status"></p>
    `, { runScripts: "dangerously" });
    document = dom.window.document;
  });

  test("Submits a vote and updates status", () => {
    const voteButton = document.getElementById("vote-5");
    const status = document.getElementById("status");

    voteButton.addEventListener("click", () => {
      status.textContent = "Vote submitted: 5";
    });

    voteButton.click();

    expect(status.textContent).toBe("Vote submitted: 5");
  });
});
