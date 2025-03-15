document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("profile-form");
    const messagesContainer = document.getElementById("messages-container");

    form.addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent page reloads

        const formData = new FormData(form);

        fetch(form.action, {
            method: "POST",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
            body: formData,
        })
            .then((response) => response.json())
            .then((data) => {
                // Clean up the message container
                messagesContainer.innerHTML = "";

                // If there are messages, add them
                if (data.messages) {
                    data.messages.forEach((message) => {
                        const div = document.createElement("div");
                        div.className = `alert ${message.tags}`;
                        div.textContent = message.message;
                        messagesContainer.appendChild(div);
                    });
                }

                // If everything goes well, clear the form
                if (data.success) {
                    form.reset();
                }
            })
            .catch((error) => {
                console.error("Error:", error);
            });
    });
});