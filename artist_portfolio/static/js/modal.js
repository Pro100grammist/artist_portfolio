document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("painting-modal");
    const modalImg = document.getElementById("modal-painting-img");
    const modalTitle = document.getElementById("modal-title");
    const modalDescription = document.getElementById("modal-description");
    const modalPrice = document.getElementById("modal-price");
    const closeButton = document.querySelector(".close-button");
    const viewInGalleryBtn = document.getElementById("view-in-gallery");

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
        djangoBaseUrl = "https://artist-portfolio-fquo.onrender.com";
        vueAppUrl = "https://artist-portfolio-3d-gallery.onrender.com";
    }

    document.querySelectorAll(".featured-work").forEach((item) => {
        item.addEventListener("click", () => {
            const fullImgSrc = item.getAttribute("data-image");

            modalImg.src = fullImgSrc;
            modalTitle.textContent = item.getAttribute("data-title");
            modalDescription.textContent =
                item.getAttribute("data-description");
            modalPrice.textContent = `Price: ${item.getAttribute(
                "data-price"
            )}`;

            const encodedImgSrc = encodeURIComponent(fullImgSrc);
            viewInGalleryBtn.href = `${vueAppUrl}/?image=${encodedImgSrc}`;

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
