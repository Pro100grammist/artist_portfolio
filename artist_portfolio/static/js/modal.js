document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("painting-modal");
    const modalImg = document.getElementById("modal-painting-img");
    const modalTitle = document.getElementById("modal-title");
    const modalDescription = document.getElementById("modal-description");
    // const modalPrice = document.getElementById("modal-price");
    const closeButton = document.querySelector(".close-button");
    const viewInGalleryBtn = document.getElementById("view-in-gallery");
    const purchaseBtn = document.querySelector(".purchase-btn");
    const lens = document.getElementById("magnifier-lens");
    const img = document.getElementById("modal-painting-img");

    // Detect touch devices (mobile/tablet) and disable magnifier there
    const isTouchDevice =
        window.matchMedia && window.matchMedia("(pointer: coarse)").matches ||
        "ontouchstart" in window ||
        (navigator.maxTouchPoints && navigator.maxTouchPoints > 0);

    if (!isTouchDevice) {
        img.addEventListener("mouseenter", () => {
            lens.style.display = "block";
            lens.style.backgroundImage = `url('${img.src}')`;
        });

        img.addEventListener("mouseleave", () => {
            lens.style.display = "none";
        });

        img.addEventListener("mousemove", moveLens);
    } else {
        // Ensure lens is hidden on touch devices
        lens.style.display = "none";
    }

    function moveLens(e) {
        const rect = img.getBoundingClientRect();
        const lensSize = 120;
        const zoom = 2;

        // coordinates of the cursor relative to the picture
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        // do not go beyond the picture
        const boundedX = Math.max(Math.min(x, img.width), 0);
        const boundedY = Math.max(Math.min(y, img.height), 0);
        // lens position (centered)
        lens.style.left = `${boundedX - lensSize / 2}px`;
        lens.style.top = `${boundedY - lensSize / 2}px`;

        // background for the lens (enlarged area)
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

    // helpers to lock/unlock body scroll to prevent background scrolling
    const body = document.body;
    let savedScrollY = 0;

    function lockBodyScroll() {
        savedScrollY = window.scrollY || document.documentElement.scrollTop || 0;
        body.classList.add("body--modal-open");
        body.style.top = `-${savedScrollY}px`;
    }

    function unlockBodyScroll() {
        body.classList.remove("body--modal-open");
        body.style.top = "";
        window.scrollTo(0, savedScrollY);
    }

    // Collapse/expand description on mobile with "Read more >>"
    function applyCollapsibleDescription(fullText) {
        const isSmallScreen = window.matchMedia && window.matchMedia("(max-width: 768px)").matches;
        if (!isSmallScreen) {
            modalDescription.innerHTML = fullText.replace(/\n/g, "<br>");
            return;
        }

        const WORD_LIMIT = 40; // preview words
        const words = (fullText || "").split(/\s+/).filter(Boolean);

        // If short enough, show full text
        if (words.length <= WORD_LIMIT) {
            modalDescription.innerHTML = fullText.replace(/\n/g, "<br>");
            return;
        }

        const preview = words.slice(0, WORD_LIMIT).join(" ") + "... ";
        modalDescription.innerHTML = preview;

        const readMore = document.createElement("a");
        readMore.href = "#";
        readMore.className = "read-more";
        readMore.textContent = "Read more >>";
        readMore.addEventListener("click", (e) => {
            e.preventDefault();
            modalDescription.innerHTML = fullText.replace(/\n/g, "<br>");
        });

        modalDescription.appendChild(readMore);
    }

    document.querySelectorAll(".featured-work").forEach((item) => {
        item.addEventListener("click", () => {
            let fullImgSrc = item.getAttribute("data-image");

            // Check if the image source is a relative path
            if (fullImgSrc && fullImgSrc.startsWith("/")) {
                fullImgSrc = `${djangoBaseUrl}${fullImgSrc}`;
            }

            modalImg.src = fullImgSrc;
            modalTitle.textContent = item.getAttribute("data-title");
            // Prepare description: collapsible preview on mobile
            const fullDescription = item.getAttribute("data-description") || "";
            applyCollapsibleDescription(fullDescription);

            // if (modalPrice) {
            //     modalPrice.textContent = `Price: ${item.getAttribute(
            //         "data-price"
            //     )}`;
            // }

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
            lockBodyScroll();
        });
    });

    closeButton.addEventListener("click", () => {
        modal.classList.remove("visible");
        unlockBodyScroll();
    });

    modal.addEventListener("click", (e) => {
        if (e.target === modal) {
            modal.classList.remove("visible");
            unlockBodyScroll();
        }
    });
});
