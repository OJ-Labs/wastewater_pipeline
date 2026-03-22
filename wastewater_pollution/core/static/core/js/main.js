document.addEventListener("DOMContentLoaded", () => {
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("overlay");
    const toggleBtn = document.querySelector(".openbtn");
    const closeBtn = document.querySelector(".closebtn");

    function isMobile() {
        return window.innerWidth <= 768;
    }

    function updateIcon() {
        if (isMobile()) {
            toggleBtn.innerHTML = sidebar.classList.contains("open") ? "✖" : "☰";
        } else {
            toggleBtn.innerHTML = sidebar.classList.contains("collapsed") ? "☰" : "✖";
        }
    }

    function openMobile() {
        sidebar.classList.add("open");
        overlay.classList.add("active");
    }

    function closeMobile() {
        sidebar.classList.remove("open");
        overlay.classList.remove("active");
    }

    toggleBtn.addEventListener("click", () => {
        if (isMobile()) {
            sidebar.classList.toggle("open");
            overlay.classList.toggle("active");
        } else {
            sidebar.classList.toggle("collapsed");

            localStorage.setItem(
                "sidebar-state",
                sidebar.classList.contains("collapsed") ? "collapsed" : "expanded"
            );
        }

        updateIcon();
    });

    closeBtn.addEventListener("click", () => {
        if (isMobile()) {
            closeMobile();
        } else {
            sidebar.classList.add("collapsed");
        }
        updateIcon();
    });

    overlay.addEventListener("click", () => {
        closeMobile();
        updateIcon();
    });

    // Restore state
    if (localStorage.getItem("sidebar-state") === "collapsed") {
        sidebar.classList.add("collapsed");
    }

    updateIcon();
});



let lastScroll = 0;

window.addEventListener("scroll", () => {
    const currentScroll = window.scrollY;

    if (currentScroll > lastScroll && currentScroll > 100) {
        bottomNav.classList.add("show");   // scrolling down
    } else {
        bottomNav.classList.remove("show"); // scrolling up
    }

    lastScroll = currentScroll;
});



const dropdown = document.getElementById("authDropdown");
const button = dropdown.querySelector(".dropbtn");

// Toggle dropdown
button.addEventListener("click", () => {
    dropdown.classList.toggle("active");
});

// Click outside to close
document.addEventListener("click", (e) => {
    if (!dropdown.contains(e.target)) {
        dropdown.classList.remove("active");
    }
});


function toggleForms(type) {
    const login = document.getElementById("loginForm");
    const signup = document.getElementById("signupForm");

    if (type === "signup") {
        login.style.display = "none";
        signup.style.display = "block";
    } else {
        login.style.display = "block";
        signup.style.display = "none";
    }
}