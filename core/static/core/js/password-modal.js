document.addEventListener('DOMContentLoaded', function() {
  // Elements
  const modal = document.getElementById('passwordChangeModal');
  const openModalBtn = document.getElementById('openPasswordChangeModal');
  const closeModalBtn = document.getElementById('closePasswordModal');
  const cancelBtn = document.getElementById('cancelPasswordChange');
  const form = document.getElementById('passwordChangeForm');
  const messageContainer = document.getElementById('passwordModalMessages');
  
  // Open modal
  if (openModalBtn) {
    openModalBtn.addEventListener('click', function(e) {
      e.preventDefault();
      modal.classList.remove('hidden');
      document.body.classList.add('overflow-hidden');
      // Clear previous form inputs and errors
      if (form){ 
        form.reset();
      }
        clearErrors();
        
    });
  }
  
  // Close modal functions
  function closeModal() {
    modal.classList.add('hidden');
    document.body.classList.remove('overflow-hidden');
    // Reset form and errors
    if (form){
        form.reset();   
    } 
    clearErrors();
  }
  
  function clearErrors() {
    document.querySelectorAll('.error-message').forEach(el => {
      el.classList.add('hidden');
      el.textContent = '';
    });
    messageContainer.classList.add('hidden');
    messageContainer.textContent = '';
    
    // Clear any highlighted fields
    document.querySelectorAll('input').forEach(input => {
      input.classList.remove('border-red-500');
    });
  }
  
  // Close modal events
  if (closeModalBtn){
    closeModalBtn.addEventListener('click', closeModal);
  } 
  if (cancelBtn){
    cancelBtn.addEventListener('click', closeModal);
  } 
  
  // Close when clicking outside the modal
  window.addEventListener('click', function(e) {
    if (e.target === modal) {
      closeModal();
    }
  });
  
  // Handle form submission
  if (form) {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      clearErrors();
      
      // Get form data
      const formData = new FormData(form);
      
      // Submit form via fetch
      fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'same-origin'
      })
      .then(response => {
        // Debug: log the entire response
        const clone = response.clone();
        clone.text().then(text => console.log('Response:', text));
        return response.json();
      })
      .then(data => {
        if (data.success) {
          // Show success message
          messageContainer.classList.remove('hidden', 'bg-red-100', 'text-red-700');
          messageContainer.classList.add('bg-green-100', 'text-green-700', 'p-4', 'rounded-md');
          messageContainer.textContent = data.message || "Your password has been successfully changed!";
          
          // Close modal after delay
          setTimeout(() => {
            closeModal();
            // Reload page to reflect changes
            window.location.reload();
          }, 2000);
        } else {
          // Show error message
          messageContainer.classList.remove('hidden', 'bg-green-100', 'text-green-700');
          messageContainer.classList.add('bg-red-100', 'text-red-700', 'p-4', 'rounded-md');
          messageContainer.textContent = data.message || 'Please correct the errors below.';
          
          // Display field errors
          if (data.errors) {
            Object.keys(data.errors).forEach(field => {
              const errorEl = document.getElementById(`error_${field}`);
              if (errorEl) {
                errorEl.textContent = data.errors[field][0];
                errorEl.classList.remove('hidden');
                
                // Highlight the field
                const inputEl = document.getElementById(`id_${field}`);
                if (inputEl){
                    inputEl.classList.add('border-red-500');
                    
                } 
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