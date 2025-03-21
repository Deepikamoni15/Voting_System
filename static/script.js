document.addEventListener("DOMContentLoaded", () => {
    const buttons = document.querySelectorAll(".vote-button");
    const message = document.getElementById("message");

    buttons.forEach(button => {
        button.addEventListener("click", () => {
            const candidate = button.getAttribute("data-candidate");

            fetch("/vote", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ candidate })
            })
            .then(response => response.json())
            .then(data => {
                message.textContent = data.message;
                message.style.color = data.status === "success" ? "green" : "red";
            });
        });
    });
});