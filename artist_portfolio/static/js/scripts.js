document.addEventListener("DOMContentLoaded", () => {
  const swiper = new Swiper(".swiper-container", {
    slidesPerView: 3, // Кількість видимих слайдів
    spaceBetween: 20, // Відстань між слайдами
    centeredSlides: true, // Центральний слайд посередині
    loop: true, // Карусель циклічна
    effect: "coverflow", // Ефект 3D Coverflow
    coverflowEffect: {
      rotate: 50, // Кут повороту слайдів
      stretch: 0, // Розтягнення слайдів
      depth: 100, // Глибина в 3D-просторі
      modifier: 1, // Інтенсивність ефекту
      slideShadows: true, // Тіні для слайдів
    },
    navigation: {
      nextEl: ".swiper-button-next",
      prevEl: ".swiper-button-prev",
    },
  });
});

// Функція для показу спливаючого асистента
function showAssistantPopup() {
    const popup = document.getElementById('assistant-popup');
    popup.classList.remove('hidden');
}

// Функція для приховування спливаючого асистента
function closeAssistantPopup() {
    const popup = document.getElementById('assistant-popup');
    popup.classList.add('hidden');
}

// Показати асистента через 30 секунд
window.addEventListener('load', () => {
    setTimeout(showAssistantPopup, 30000);
});




// document.addEventListener("DOMContentLoaded", () => {
//   const swiper = new Swiper(".swiper-container", {
//     loop: true, // Enable looping
//     slidesPerView: 3, // Show 3 slides at a time
//     spaceBetween: 10, // Space between slides
//     navigation: {
//       nextEl: ".swiper-button-next",
//       prevEl: ".swiper-button-prev",
//     },
//     pagination: {
//       el: ".swiper-pagination",
//       clickable: true,
//     },
//   });
// });




// const canvas = document.getElementById("artCanvas");
// const ctx = canvas.getContext("2d");

// // Dynamically adjust the size of Canvas
// canvas.width = window.innerWidth;
// canvas.height = window.innerHeight;

// // Scaling when resizing a window
// window.addEventListener("resize", () => {
//   canvas.width = window.innerWidth;
//   canvas.height = window.innerHeight;
// });

// // Function for drawing random elements
// function draw() {
//   ctx.fillStyle = `rgba(${Math.random() * 255}, ${Math.random() * 255}, ${
//     Math.random() * 255
//   }, 0.5)`;
//   ctx.beginPath();
//   ctx.arc(
//     Math.random() * canvas.width,
//     Math.random() * canvas.height,
//     50,
//     0,
//     Math.PI * 2
//   );
//   ctx.fill();
// }

// // Animation
// setInterval(draw, 100);
