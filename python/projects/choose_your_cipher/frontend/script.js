document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("cipherForm");
  const resultDiv = document.getElementById("result");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const text = document.getElementById("text").value;
    const keyword = document.getElementById("keyword").value;
    const cipher_type = form.cipher_type.value;
    const action_type = form.action_type.value;

    const payload = { text, keyword, cipher_type, action_type };

    try {
      const response = await fetch("http://127.0.0.1:8000/cipher", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await response.json();
      resultDiv.textContent = data.result;
    } catch (err) {
      resultDiv.textContent = "Error connecting to backend.";
      console.error(err);
    }
  });
});
