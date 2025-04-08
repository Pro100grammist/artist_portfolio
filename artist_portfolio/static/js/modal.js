document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("painting-modal");
    const modalImg = document.getElementById("modal-painting-img");
    const modalTitle = document.getElementById("modal-title");
    const modalDescription = document.getElementById("modal-description");
    const modalPrice = document.getElementById("modal-price");
    const closeButton = document.querySelector(".close-button");
    const viewInGalleryBtn = document.getElementById("view-in-gallery");
    const purchaseBtn = document.querySelector(".purchase-btn");

    // define the URL
    let djangoBaseUrl, vueAppUrl;

    if (
        window.location.hostname === "127.0.0.1" ||
        window.location.hostname === "localhost"
    ) {
        // Local development
        djangoBaseUrl = "http://127.0.0.1:8000";
        vueAppUrl = "http://192.168.0.157:8080";
    } else {
        // Production on Render
        djangoBaseUrl = ""; // don't add anything in prod, cause image.url already has the full path
        vueAppUrl = "https://artist-portfolio-3d-gallery.onrender.com";
    }

    // Check if the current page is the store page
    const isStorePage = window.location.pathname.includes("/store");

    document.querySelectorAll(".featured-work").forEach((item) => {
        item.addEventListener("click", () => {
            let fullImgSrc = item.getAttribute("data-image");

            // Check if the image source is a relative path
            if (fullImgSrc && fullImgSrc.startsWith("/")) {
                fullImgSrc = `${djangoBaseUrl}${fullImgSrc}`;
            }

            modalImg.src = fullImgSrc;
            modalTitle.textContent = item.getAttribute("data-title");
            modalDescription.textContent = item.getAttribute("data-description");
            modalPrice.textContent = `Price: ${item.getAttribute("data-price")}`;

            const encodedImgSrc = encodeURIComponent(fullImgSrc);

            if (viewInGalleryBtn) {
                viewInGalleryBtn.href = `${vueAppUrl}/?image=${encodedImgSrc}`;
            }

            // --- PURCHASE BUTTON LOGIC ---
            if (isStorePage && purchaseBtn) {
                const productId = item.getAttribute("data-id");

                purchaseBtn.removeAttribute("href");
                purchaseBtn.onclick = function () {
                    addToCart(productId);
                    modal.classList.remove("visible");
                };
            } else if (purchaseBtn) {
                purchaseBtn.href = "/store/";
                purchaseBtn.onclick = null;
            }

            modal.classList.add("visible");
        });
    });

    closeButton.addEventListener("click", () => {
        modal.classList.remove("visible");
    });

    modal.addEventListener("click", (e) => {
        if (e.target === modal) {
            modal.classList.remove("visible");
        }
    });
});
