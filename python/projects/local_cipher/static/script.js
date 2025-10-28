const form = document.getElementById("cipher-form");
const resultDiv = document.getElementById("result");
const resultText = document.getElementById("result-text");

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const text = document.getElementById("text").value;
    const keyword = document.getElementById("keyword").value;
    const cipher_type = document.getElementById("cipher_type").value;
    const action_type = document.querySelector('input[name="action_type"]:checked').value;

    const payload = { text, cipher_type, action_type, keyword };

    try {
        const response = await fetch("/cipher", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        resultText.textContent = data.result;
        resultDiv.style.display = "block";
    } catch (err) {
        console.error(err);
        resultText.textContent = "Error contacting the API";
        resultDiv.style.display = "block";
    }
});
