document.addEventListener("DOMContentLoaded", function () {
    const aboutContainer = document.querySelector(".about-container");
    aboutContainer.style.opacity = "0";
    aboutContainer.style.transform = "translateY(30px)";

    setTimeout(() => {
        aboutContainer.style.transition = "all 1s ease-in-out";
        aboutContainer.style.opacity = "1";
        aboutContainer.style.transform = "translateY(0)";
    }, 300);
});
