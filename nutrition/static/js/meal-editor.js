// Meal Editor JavaScript - Simplified version

// mealId is set in the template

function saveMeal() {
  console.log('Save meal clicked')
  showToast("Saving meal...", "info")
  
  // Simply redirect to history - meal is already saved in database
  setTimeout(() => {
    window.location.href = "/meals/history"
  }, 500)
}



// Enhanced showToast function
function showToast(message, type) {
  // Create toast element
  const toast = document.createElement('div')
  toast.className = `toast toast-${type}`
  toast.textContent = message
  
  // Add toast styles
  toast.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 12px 24px;
    border-radius: 8px;
    color: white;
    font-weight: 500;
    z-index: 10000;
    opacity: 0;
    transform: translateX(100%);
    transition: all 0.3s ease;
  `
  
  // Set background color based on type
  if (type === 'success') {
    toast.style.backgroundColor = '#10b981'
  } else if (type === 'error') {
    toast.style.backgroundColor = '#ef4444'
  } else {
    toast.style.backgroundColor = '#3b82f6'
  }
  
  // Add to page
  document.body.appendChild(toast)
  
  // Animate in
  setTimeout(() => {
    toast.style.opacity = '1'
    toast.style.transform = 'translateX(0)'
  }, 100)
  
  // Remove after 3 seconds
  setTimeout(() => {
    toast.style.opacity = '0'
    toast.style.transform = 'translateX(100%)'
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast)
      }
    }, 300)
  }, 3000)
}