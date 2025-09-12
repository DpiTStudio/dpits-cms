// static/js/script.js

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    })
})

// Form validation
function validateForm(form) {
    var inputs = form.querySelectorAll('input[required], textarea[required]');
    var valid = true;
    
    inputs.forEach(function(input) {
        if (!input.value.trim()) {
            valid = false;
            input.classList.add('is-invalid');
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return valid;
}

// Image preview
function previewImage(input, previewId) {
    var preview = document.getElementById(previewId);
    var file = input.files[0];
    var reader = new FileReader();
    
    reader.onloadend = function() {
        preview.src = reader.result;
        preview.style.display = 'block';
    }
    
    if (file) {
        reader.readAsDataURL(file);
    } else {
        preview.src = '';
        preview.style.display = 'none';
    }
}

// Smooth scrolling
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});