document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".delete-item").forEach((button) => {
        button.addEventListener("click", function (event) {
            event.preventDefault(); // Cancel the standard action

            let productId = this.getAttribute("data-product-id");
            let url = `/cart/remove-from-cart/${productId}/`;

            fetch(url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                    "Content-Type": "application/json",
                    Accept: "application/json",
                    "X-Requested-With": "XMLHttpRequest",
                },
            })
                .then(parseJsonResponse)
                .then((data) => {
                    if (data.message) {
                        const cartItem = document.getElementById(`cart-item-${productId}`);
                        if (cartItem) {
                            cartItem.remove(); // Remove a product from HTML
                        }
                        updateTotalPrice(data.total_price); // Update the amount
                    }
                })
                .catch((error) => showToast(error.message));
        });
    });
});


// Function to get CSRF token (required for Django)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        let cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
                break;
            }
        }
    }
    return cookieValue;
}

// Update the total amount in the cart
function updateTotalPrice(newPrice) {
    document.getElementById("total-price").textContent = `$${newPrice.toFixed(
        2
    )}`;
}

function showToast(message) {
    const toast = document.createElement("div");
    toast.className = "toast";
    toast.innerText = message;
    document.body.appendChild(toast);

    setTimeout(() => toast.classList.add("show"), 100);
    setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function parseJsonResponse(response) {
    return response.json().catch(() => ({})).then((data) => {
        if (!response.ok) {
            throw new Error(data.error || "Request failed.");
        }
        return data;
    });
}

