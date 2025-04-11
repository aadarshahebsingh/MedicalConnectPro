document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Add animation to feature cards
    const featureCards = document.querySelectorAll('.feature-card');
    if (featureCards) {
        featureCards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.classList.add('shadow-lg');
            });
            card.addEventListener('mouseleave', () => {
                card.classList.remove('shadow-lg');
            });
        });
    }
    
    // Symptom input character counter
    const symptomsTextarea = document.getElementById('symptoms');
    const charCounter = document.getElementById('char-counter');
    
    if (symptomsTextarea && charCounter) {
        symptomsTextarea.addEventListener('input', function() {
            const currentLength = this.value.length;
            const maxLength = this.getAttribute('maxlength') || 500;
            charCounter.textContent = `${currentLength}/${maxLength}`;
            
            // Change color based on remaining characters
            if (currentLength > maxLength * 0.8) {
                charCounter.classList.add('text-warning');
            } else {
                charCounter.classList.remove('text-warning');
            }
            
            if (currentLength > maxLength * 0.95) {
                charCounter.classList.add('text-danger');
            } else {
                charCounter.classList.remove('text-danger');
            }
        });
        
        // Initialize counter
        symptomsTextarea.dispatchEvent(new Event('input'));
    }
    
    // Add confirmation for appointment status changes
    const statusForms = document.querySelectorAll('.appointment-status-form');
    if (statusForms) {
        statusForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                const status = this.querySelector('select[name="status"]').value;
                if (status === 'cancelled') {
                    if (!confirm('Are you sure you want to cancel this appointment?')) {
                        e.preventDefault();
                    }
                }
            });
        });
    }
});
