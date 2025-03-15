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
                },
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.message) {
                        document
                            .getElementById(`cart-item-${productId}`)
                            .remove(); // Remove a product from HTML
                        updateTotalPrice(data.total_price); // Update the amount
                    }
                })
                .catch((error) => console.error("Error:", error));
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


