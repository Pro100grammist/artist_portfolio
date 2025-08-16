document.addEventListener("DOMContentLoaded", () => {
    const swiper = new Swiper(".swiper-container", {
        slidesPerView: 3, // Number of visible slides
        spaceBetween: 20, // Distance between slides
        centeredSlides: true, // Center slide in the middle
        loop: true, // Cyclic carousel
        effect: "coverflow", // 3D Coverflow effect
        coverflowEffect: {
            rotate: 50, // Slide rotation angle
            stretch: 0, // Stretch slides
            depth: 100, // Depth in 3D space
            modifier: 1, // Intensity of the effect
            slideShadows: true, // Shadows for slides
        },
        navigation: {
            nextEl: ".swiper-button-next",
            prevEl: ".swiper-button-prev",
        },
    });

    const burger = document.querySelector(".burger");
    const nav = document.querySelector("header nav");
    const auth = document.querySelector("header .auth-links");

    if (burger && nav && auth) {
        burger.addEventListener("click", () => {
            nav.classList.toggle("active");
            auth.classList.toggle("active");
        });
    }
});

document.querySelectorAll(".glow-button").forEach((button) => {
    button.addEventListener("mousemove", (e) => {
        const rect = button.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        button.style.setProperty("--pointer-x", `${x}px`);
        button.style.setProperty("--pointer-y", `${y}px`);
    });
});

// Function to show a pop-up assistant
function showAssistantPopup() {
    const popup = document.getElementById("assistant-popup");
    popup.classList.remove("hidden");
}

// Function to hide the pop-up assistant
function closeAssistantPopup() {
    const popup = document.getElementById("assistant-popup");
    popup.classList.add("hidden");
}

// Assistant readings in 30 seconds
window.addEventListener("load", () => {
    setTimeout(showAssistantPopup, 30000);
});

// Connecting and rendering Lottie icons
document.addEventListener("DOMContentLoaded", function () {
    // General parameters
    const socialIcons = [
        {
            id: "facebook-icon",
            path: "/static/animations/social-icons/facebook.json",
        },
        {
            id: "instagram-icon",
            path: "/static/animations/social-icons/instagram.json",
        },
        {
            id: "linkedin-icon",
            path: "/static/animations/social-icons/linkedin.json",
        },
    ];

    // Initialize animation for each icon
    socialIcons.forEach((icon) => {
        const element = document.getElementById(icon.id);
        if (element) {
            // Initialize the Lottie animation if the element exists
            lottie.loadAnimation({
                container: element, // container for animation
                renderer: "svg", // rendering format
                loop: true, // animation in a loop
                autoplay: true, // automatic start
                path: icon.path, // path to the JSON file of the animation
            });
        } else {
            console.warn(`Element with id '${icon.id}' not found in DOM.`);
        }
    });
});

// === DEBUG MODE ===
(function debugMode() {
    console.log("✅ Debug mode activated");

    // Перевірка ширини вікна
    const width = window.innerWidth;
    console.log(`📱 Window width: ${width}px`);

    // Перевірка активного стану бургера та меню
    const nav = document.querySelector("header nav");
    const auth = document.querySelector("header .auth-links");

    if (nav && auth) {
        console.log("✅ nav і auth-links знайдені");

        const navVisible = window.getComputedStyle(nav).display;
        const authVisible = window.getComputedStyle(auth).display;
        console.log(`📦 nav display: ${navVisible}`);
        console.log(`🔒 auth-links display: ${authVisible}`);
    } else {
        console.warn("❌ nav або auth-links не знайдені в DOM");
    }

    // Перевірка чи стиль style.css був підключений
    const foundStyle = [...document.styleSheets].some(sheet => sheet.href && sheet.href.includes("style.css"));
    if (foundStyle) {
        console.log("🎨 style.css успішно підключений");
    } else {
        console.warn("❌ style.css не знайдено — можливо кеш або помилка шляху");
    }

    // Перевірка font-size заголовку
    const welcome = document.querySelector(".welcome-text");
    if (welcome) {
        const size = window.getComputedStyle(welcome).fontSize;
        console.log(`📝 .welcome-text font-size: ${size}`);
    }
})();
