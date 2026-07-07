(function () {
  const phrases = [
    "Your employee records, clarified.",
    "Self-service for every update.",
    "Built for people operations.",
  ];

  let phraseIndex = 0;
  let charIndex = 0;
  let isDeleting = false;
  let tagline = null;

  function typewriter() {
    const currentPhrase = phrases[phraseIndex];
    tagline.textContent = currentPhrase.slice(0, charIndex);

    if (!isDeleting) {
      if (charIndex < currentPhrase.length) {
        charIndex += 1;
        setTimeout(typewriter, 40);
      } else {
        isDeleting = true;
        setTimeout(typewriter, 500);
      }
    } else if (charIndex > 0) {
      charIndex -= 1;
      setTimeout(typewriter, 40);
    } else {
      isDeleting = false;
      phraseIndex = (phraseIndex + 1) % phrases.length;
      setTimeout(typewriter, 50);
    }
  }

  function toggleNotificationBox() {
    const notificationBox = document.getElementById("notificationBox");
    if (notificationBox) {
      notificationBox.classList.toggle("hidden");
    }
  }

  function toggleReminderBox() {
    const reminderBox = document.getElementById("newReminderBox");
    if (reminderBox) {
      reminderBox.classList.toggle("hidden");
    }
  }

  function togglePortalTheme() {
    document.documentElement.classList.toggle("dark");
  }

  window.addEventListener("load", () => {
    const loader = document.getElementById("loader");
    const main = document.getElementById("main-content");
    tagline = document.getElementById("typewriter");

    if (tagline) {
      tagline.style.display = "inline";
      typewriter();
    }

    setTimeout(() => {
      loader.style.opacity = "0";
      loader.style.transform = "scale(0.95)";

      setTimeout(() => {
        loader.style.display = "none";
        main.classList.remove("hidden");
        main.style.animation = "fadeIn 1s ease-in-out";
      }, 400);
    }, 2000);
  });

  document.addEventListener("DOMContentLoaded", () => {
    const toggleNotificationBtn = document.getElementById("toggleNotificationBtn");
    if (toggleNotificationBtn) {
      toggleNotificationBtn.addEventListener("click", toggleNotificationBox);
    }

    const toggleReminderBtn = document.getElementById("toggleReminderBtn");
    const closeReminderBtn = document.getElementById("closeReminderBtn");
    const cancelReminderBtn = document.getElementById("cancelReminderBtn");

    if (toggleReminderBtn) {
      toggleReminderBtn.addEventListener("click", toggleReminderBox);
    }
    if (closeReminderBtn) {
      closeReminderBtn.addEventListener("click", toggleReminderBox);
    }
    if (cancelReminderBtn) {
      cancelReminderBtn.addEventListener("click", toggleReminderBox);
    }
  });

  window.togglePortalTheme = togglePortalTheme;
})();
