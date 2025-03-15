// shopping cart update
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;


document.addEventListener("DOMContentLoaded", updateCartCount);

function updateCartCount() {
    fetch("/cart/count/", {
        method: "GET",
        headers: {
            "X-CSRFToken": csrfToken,
        },
    })
        .then((response) => response.json())
        .then((data) => {
            const cartCountElement = document.getElementById("cart-count");
            cartCountElement.textContent = data.count; // Update the number of items in the cart
            if (data.count > 0) {
                cartCountElement.style.display = "inline-block"; // Show number if there are products in the cart
            } else {
                cartCountElement.style.display = "none"; // Hide if the cart is empty
            }
        })
        .catch((error) => console.error("Error updating cart count:", error));
}

function addToCart(productId) {
    fetch(`/cart/add-to-cart/${productId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Content-Type": "application/json",
        },
    })
        .then((response) => response.json())
        .then((data) => {
            showToast(data.message); // Display a pop-up message
            updateCartCount(); // Update the number of products
        })
        .catch((error) => console.error("Error adding to cart:", error));
}

// Function for displaying a message
function showToast(message) {
    const toast = document.createElement("div");
    toast.className = "toast";
    toast.innerText = message;
    document.body.appendChild(toast);

    // Show message
    setTimeout(() => toast.classList.add("show"), 100);

    // Automatic vidaliti in 3 seconds
    setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
                break;
            }
        }
    }
    return cookieValue;
}
