console.log("modal.js loaded");

document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("painting-modal");
    const modalImg = document.getElementById("modal-painting-img");
    const modalTitle = document.getElementById("modal-title");
    const modalDescription = document.getElementById("modal-description");
    const modalPrice = document.getElementById("modal-price");
    const closeButton = document.querySelector(".close-button");
    const viewInGalleryBtn = document.getElementById("view-in-gallery");

    // Test server domain (Change during production to the IP or port on which the server is listening)
    const djangoBaseUrl = "http://127.0.0.1:8000";
    const vueAppUrl = "http://192.168.0.157:8080";

    // Production server domain on Render (https://render.com)
    // const djangoBaseUrl = "https://artist-portfolio-fquo.onrender.com";
    // const vueAppUrl = "https://artist-portfolio.onrender.com";

    document.querySelectorAll(".featured-work").forEach((item) => {
        item.addEventListener("click", () => {
            const imgSrc = item.getAttribute("data-image"); // "/media/gallery/<image_file.jpg>"
            const fullImgSrc = `${djangoBaseUrl}${imgSrc}`;
            const encodedImgSrc = encodeURIComponent(fullImgSrc);

            modalImg.src = fullImgSrc;
            modalTitle.textContent = item.getAttribute("data-title");
            modalDescription.textContent =
                item.getAttribute("data-description");
            modalPrice.textContent = `Price: ${item.getAttribute(
                "data-price"
            )}`;

            viewInGalleryBtn.href = `${vueAppUrl}/?image=${encodedImgSrc}`;

            console.log("Оновлений href:", viewInGalleryBtn.href);

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
