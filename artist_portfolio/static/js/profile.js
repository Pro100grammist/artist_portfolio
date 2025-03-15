// Adds a click event handler for the avatar change button
document.getElementById("avatar-btn").addEventListener("click", function () {
    document.getElementById("avatar-upload").click(); // Causes a click on the hidden file upload inlay
});

// Adds a file change event handler for the avatar upload inlet
document
    .getElementById("avatar-upload")
    .addEventListener("change", function (event) {
        let formData = new FormData(document.getElementById("avatar-form")); // Creates a FormData obj from the form
        let url = document // Gets the URL for downloading an avatar from the data-url attribute
            .getElementById("avatar-btn")
            .getAttribute("data-url");

        // Sends a file to the server via the fetch API
        fetch(url, {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": document.querySelector(
                    "[name=csrfmiddlewaretoken]"
                ).value, // Adds CSRF token for security
            },
        })
            .then((response) => response.json()) // Convert the response to JSON
            .then((data) => {
                if (data.success) {
                    // Updates the avatar on the page if the upload is successful
                    document.getElementById("profile-avatar").src =
                        data.avatar_url;
                }
            });
    });

let formChanged = false; // Flag to track changes in the form

// Makes text elements editable on click
document.querySelectorAll(".editable-text").forEach((span) => {
    span.addEventListener("click", function () {
        let input = this.nextElementSibling; // Gets the corresponding input

        // Close all other open input-fields
        document.querySelectorAll(".editable-text + input").forEach((inp) => {
            inp.classList.remove("active");
            inp.previousElementSibling.classList.remove("active");
        });

        this.classList.add("active"); // Adds an activity class to display
        input.classList.add("active");
        input.focus(); // Moves the focus to the input field
    });
});

// Loss of focus handler for edit inputs
document.querySelectorAll(".editable-text + input").forEach((input) => {
    input.addEventListener("blur", function () {
        if (!this.value.trim()) return; // Ignores if the field is empty
        let span = this.previousElementSibling;
        span.textContent = this.value; // Updates text in the appropriate span
        span.classList.remove("active");
        this.classList.remove("active");
    });
});

// Hides notifications after 3 seconds when the page loads
document.addEventListener("DOMContentLoaded", function () {
    setTimeout(() => {
        let msg = document.getElementById("message-container");
        if (msg) msg.style.display = "none";
    }, 3000);
});

// Warn the user before logging out if there have been changes to the form
window.addEventListener("beforeunload", (event) => {
    if (formChanged) {
        event.preventDefault();
    }
});
