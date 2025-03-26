document.addEventListener('DOMContentLoaded', function() {
  // Elements
  const modal = document.getElementById('profileEditModal');
  const openModalBtn = document.getElementById('openProfileEditModal');
  const closeModalBtn = document.getElementById('closeProfileModal');
  const cancelBtn = document.getElementById('cancelEditProfile');
  const form = document.getElementById('profileEditForm');
  const messageContainer = document.getElementById('modalMessages');
  
  // Open modal
  if (openModalBtn) {
    openModalBtn.addEventListener('click', function() {
      modal.classList.remove('hidden');
      document.body.classList.add('overflow-hidden');
    });
  }
  
  // Close modal functions
// sourcery skip: avoid-function-declarations-in-blocks
function closeModal() {
    modal.classList.add('hidden');
    document.body.classList.remove('overflow-hidden');
    // Reset form and errors
    if (form) {
      form.reset();
    }
    document.querySelectorAll('.error-message').forEach(el => {
    el.classList.add('hidden');
    el.textContent = '';
    });
    messageContainer.classList.add('hidden');
    messageContainer.textContent = '';
  }
  
  // Close modal events
  if (closeModalBtn) {
    closeModalBtn.addEventListener('click', closeModal);
  }

  if (cancelBtn) {
    cancelBtn.addEventListener('click', closeModal);
  }
  
  // Close when clicking outside the modal
  modal.addEventListener('click', function(e) {
    if (e.target === modal) {
      closeModal();
    }
  });
  
  // Handle form submission
  if (form) {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      
      // Clear previous errors
      document.querySelectorAll('.error-message').forEach(el => {
        el.classList.add('hidden');
        el.textContent = '';
      });
      
      // Get form data
      const formData = new FormData(form);
      
      // Submit form via fetch
      fetch('/profile/edit/', {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'same-origin'
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          // Show success message
          messageContainer.classList.remove('hidden', 'bg-red-100', 'text-red-700');
          messageContainer.classList.add('bg-green-100', 'text-green-700', 'p-4', 'rounded-md');
          messageContainer.textContent = data.message;
          
          // Close modal after delay
          setTimeout(() => {
            closeModal();
            // Refresh page to show updated profile
            window.location.reload();
          }, 1500);
        } else {
          // Show error message
          messageContainer.classList.remove('hidden', 'bg-green-100', 'text-green-700');
          messageContainer.classList.add('bg-red-100', 'text-red-700', 'p-4', 'rounded-md');
          messageContainer.textContent = data.message || 'An error occurred. Please try again.';
          
          // Display field errors
          if (data.errors) {
            Object.keys(data.errors).forEach(field => {
              const errorEl = document.getElementById(`error_${field}`);
              if (errorEl) {
                errorEl.textContent = data.errors[field][0];
                errorEl.classList.remove('hidden');
              }
            });
          }
        }
      })
      .catch(error => {
        console.error('Error:', error);
        messageContainer.classList.remove('hidden', 'bg-green-100', 'text-green-700');
        messageContainer.classList.add('bg-red-100', 'text-red-700', 'p-4', 'rounded-md');
        messageContainer.textContent = 'Network error. Please try again.';
      });
    });
  }
});