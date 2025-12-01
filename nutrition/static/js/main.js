// Theme Management
function toggleTheme() {
  const html = document.documentElement
  const currentTheme = html.getAttribute("data-theme")
  const newTheme = currentTheme === "dark" ? "light" : "dark"

  html.setAttribute("data-theme", newTheme)

  // Save to localStorage
  localStorage.setItem("theme", newTheme)
}

// Initialize theme on page load
document.addEventListener("DOMContentLoaded", () => {
  const html = document.documentElement
  const savedTheme = localStorage.getItem("theme")

  if (savedTheme) {
    html.setAttribute("data-theme", savedTheme)
  }

  // Auto-hide flash messages
  setTimeout(() => {
    const flashMessages = document.querySelectorAll(".flash")
    flashMessages.forEach((flash) => {
      flash.style.opacity = "0"
      setTimeout(() => flash.remove(), 300)
    })
  }, 5000)
})

// Mobile menu toggle
function toggleMobileMenu() {
  const menu = document.getElementById("nav-menu")
  const toggle = document.querySelector(".mobile-menu-toggle")

  if (menu && toggle) {
    menu.classList.toggle("active")
    const isExpanded = menu.classList.contains("active")
    toggle.setAttribute("aria-expanded", isExpanded)
  }
}

// Profile menu toggle
function toggleProfileMenu() {
  const dropdown = document.querySelector(".dropdown-menu")
  const button = document.querySelector(".nav-profile")

  if (dropdown && button) {
    dropdown.classList.toggle("active")
    const isExpanded = dropdown.classList.contains("active")
    button.setAttribute("aria-expanded", isExpanded)
  }
}

// Flash message dismiss
function dismissFlash(button) {
  const flash = button.closest(".flash")
  if (flash) {
    flash.style.opacity = "0"
    setTimeout(() => flash.remove(), 300)
  }
}

// Simple form enhancement
document.addEventListener("DOMContentLoaded", () => {
  const forms = document.querySelectorAll("form")
  forms.forEach((form) => {
    form.addEventListener("submit", () => {
      const submitBtn = form.querySelector('button[type="submit"]')
      if (submitBtn) {
        submitBtn.disabled = true
        submitBtn.textContent = "Loading..."
      }
    })
  })
})
