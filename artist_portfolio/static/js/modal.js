document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("painting-modal");
    const modalImg = document.getElementById("modal-painting-img");
    const modalTitle = document.getElementById("modal-title");
    const modalDescription = document.getElementById("modal-description");
    const modalPrice = document.getElementById("modal-price");
    const closeButton = document.querySelector(".close-button");
    const viewInGalleryBtn = document.getElementById("view-in-gallery");
    const purchaseBtn = document.querySelector(".purchase-btn");
    const lens = document.getElementById("magnifier-lens");
    const img = document.getElementById("modal-painting-img");

    img.addEventListener("mouseenter", () => {
        lens.style.display = "block";
        lens.style.backgroundImage = `url('${img.src}')`;
    });

    img.addEventListener("mouseleave", () => {
        lens.style.display = "none";
    });

    img.addEventListener("mousemove", moveLens);

    function moveLens(e) {
        const rect = img.getBoundingClientRect();
        const lensSize = 120;
        const zoom = 2;

        // координати курсора відносно картинки
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        // не виходити за межі картинки
        const boundedX = Math.max(Math.min(x, img.width), 0);
        const boundedY = Math.max(Math.min(y, img.height), 0);

        // позиція лінзи (центрована)
        lens.style.left = `${boundedX - lensSize / 2}px`;
        lens.style.top = `${boundedY - lensSize / 2}px`;

        // фон для лінзи (збільшена область)
        lens.style.backgroundSize = `${img.width * zoom}px ${
            img.height * zoom
        }px`;
        lens.style.backgroundPosition = `-${
            boundedX * zoom - lensSize / 2
        }px -${boundedY * zoom - lensSize / 2}px`;
    }
    
    

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
            // modalDescription.textContent = item.getAttribute("data-description");
            modalDescription.innerHTML = item
                .getAttribute("data-description")
                .replace(/\n/g, "<br>");

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
