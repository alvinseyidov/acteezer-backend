// Main JavaScript for Acteezer

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initImageUpload();
    initSelectionItems();
    initFormValidation();
    initStepIndicator();
    initMap();
    initScrollToTop();
    initCategorySlider();
});

// Image Upload Functionality
function initImageUpload() {
    const uploadArea = document.querySelector('.image-upload-area');
    const fileInput = document.querySelector('#image-upload-input');
    const previewContainer = document.querySelector('.image-preview');
    
    if (!uploadArea || !fileInput) return;
    
    let selectedFiles = [];
    
    // Click to upload
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });
    
    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = Array.from(e.dataTransfer.files);
        handleFiles(files);
    });
    
    // File input change
    fileInput.addEventListener('change', (e) => {
        const files = Array.from(e.target.files);
        handleFiles(files);
    });
    
    function handleFiles(files) {
        const imageFiles = files.filter(file => file.type.startsWith('image/'));
        
        imageFiles.forEach(file => {
            if (selectedFiles.length < 5) { // Max 5 images
                selectedFiles.push(file);
                displayImagePreview(file, selectedFiles.length - 1);
            }
        });
        
        updateFileInput();
        updateUploadAreaText();
    }
    
    function displayImagePreview(file, index) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const previewItem = document.createElement('div');
            previewItem.className = 'image-preview-item fade-in-up';
            previewItem.innerHTML = `
                <img src="${e.target.result}" alt="Preview">
                <button type="button" class="image-remove-btn" onclick="removeImage(${index})">
                    <i class="fas fa-times"></i>
                </button>
            `;
            previewContainer.appendChild(previewItem);
        };
        reader.readAsDataURL(file);
    }
    
    function updateFileInput() {
        const dt = new DataTransfer();
        selectedFiles.forEach(file => dt.items.add(file));
        fileInput.files = dt.files;
    }
    
    function updateUploadAreaText() {
        const text = uploadArea.querySelector('p');
        if (text) {
            if (selectedFiles.length === 0) {
                text.textContent = 'Drag & drop images here or click to browse (minimum 2 required)';
            } else {
                text.textContent = `${selectedFiles.length} image(s) selected. ${selectedFiles.length < 2 ? 'Add at least ' + (2 - selectedFiles.length) + ' more.' : 'You can add up to ' + (5 - selectedFiles.length) + ' more.'}`;
            }
        }
    }
    
    // Global function for removing images
    window.removeImage = function(index) {
        selectedFiles.splice(index, 1);
        updateFileInput();
        updateUploadAreaText();
        
        // Remove preview
        const previewItems = previewContainer.querySelectorAll('.image-preview-item');
        previewItems[index].remove();
        
        // Update remaining indices
        previewContainer.innerHTML = '';
        selectedFiles.forEach((file, i) => {
            displayImagePreview(file, i);
        });
    };
}

// Selection Items (Languages, Interests)
function initSelectionItems() {
    const selectionItems = document.querySelectorAll('.selection-item');
    
    selectionItems.forEach(item => {
        const checkbox = item.querySelector('input[type="checkbox"]');
        
        item.addEventListener('click', () => {
            checkbox.checked = !checkbox.checked;
            item.classList.toggle('selected', checkbox.checked);
        });
        
        // Initialize state
        if (checkbox.checked) {
            item.classList.add('selected');
        }
    });
}

// Form Validation
function initFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const isValid = validateForm(form);
            if (!isValid) {
                e.preventDefault();
            }
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', () => validateField(input));
            input.addEventListener('input', () => clearFieldError(input));
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    
    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });
    
    // Custom validations
    if (form.id === 'images-form') {
        const fileInput = form.querySelector('input[type="file"]');
        if (fileInput && fileInput.files.length < 2) {
            showFieldError(fileInput, 'Please upload at least 2 images');
            isValid = false;
        }
    }
    
    if (form.id === 'languages-form') {
        const checkedBoxes = form.querySelectorAll('input[type="checkbox"]:checked');
        if (checkedBoxes.length === 0) {
            showFormError('Please select at least one language');
            isValid = false;
        }
    }
    
    if (form.id === 'interests-form') {
        const checkedBoxes = form.querySelectorAll('input[type="checkbox"]:checked');
        if (checkedBoxes.length === 0) {
            showFormError('Please select at least one interest');
            isValid = false;
        }
    }
    
    return isValid;
}

function validateField(input) {
    const value = input.value.trim();
    let isValid = true;
    
    // Required field validation
    if (input.hasAttribute('required') && !value) {
        showFieldError(input, 'This field is required');
        isValid = false;
    }
    
    // Phone validation
    if (input.type === 'tel' && value) {
        const phoneRegex = /^\+?[1-9]\d{1,14}$/;
        if (!phoneRegex.test(value.replace(/\s/g, ''))) {
            showFieldError(input, 'Please enter a valid phone number');
            isValid = false;
        }
    }
    
    // Email validation
    if (input.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            showFieldError(input, 'Please enter a valid email address');
            isValid = false;
        }
    }
    
    // Date validation (age check - only for birthday fields)
    if (input.type === 'date' && value && (input.name === 'birthday' || input.id === 'birthday')) {
        const birthDate = new Date(value);
        const today = new Date();
        const age = today.getFullYear() - birthDate.getFullYear();
        
        if (age < 16 || age > 100) {
            showFieldError(input, 'You must be between 16 and 100 years old');
            isValid = false;
        }
    }
    
    if (isValid) {
        clearFieldError(input);
    }
    
    return isValid;
}

function showFieldError(input, message) {
    clearFieldError(input);
    
    input.classList.add('is-invalid');
    const errorElement = document.createElement('div');
    errorElement.className = 'invalid-feedback';
    errorElement.textContent = message;
    input.parentNode.appendChild(errorElement);
}

function clearFieldError(input) {
    input.classList.remove('is-invalid');
    const errorElement = input.parentNode.querySelector('.invalid-feedback');
    if (errorElement) {
        errorElement.remove();
    }
}

function showFormError(message) {
    const alertElement = document.createElement('div');
    alertElement.className = 'alert alert-danger fade-in-up';
    alertElement.innerHTML = `
        <i class="fas fa-exclamation-triangle me-2"></i>
        ${message}
    `;
    
    const form = document.querySelector('form');
    form.insertBefore(alertElement, form.firstChild);
    
    setTimeout(() => {
        alertElement.remove();
    }, 5000);
}

// Step Indicator
function initStepIndicator() {
    const steps = document.querySelectorAll('.step');
    const currentStep = getCurrentStep();
    
    steps.forEach((step, index) => {
        if (index < currentStep) {
            step.classList.add('completed');
        } else if (index === currentStep) {
            step.classList.add('active');
        }
    });
}

function getCurrentStep() {
    const path = window.location.pathname;
    const stepMap = {
        '/accounts/register/': 0,
        '/accounts/register/otp/': 1,
        '/accounts/register/name/': 2,
        '/accounts/register/languages/': 3,
        '/accounts/register/birthday/': 4,
        '/accounts/register/images/': 5,
        '/accounts/register/bio/': 6,
        '/accounts/register/interests/': 7,
        '/accounts/register/location/': 8,
        '/accounts/register/complete/': 9
    };
    
    return stepMap[path] || 0;
}

// Map Initialization
function initMap() {
    const mapContainer = document.getElementById('map');
    if (!mapContainer) return;
    
    // This would integrate with a mapping service like Google Maps or Mapbox
    // For now, we'll create a placeholder
    mapContainer.innerHTML = `
        <div class="d-flex align-items-center justify-content-center h-100 bg-light">
            <div class="text-center">
                <i class="fas fa-map-marked-alt fa-3x text-primary mb-3"></i>
                <h5>Interactive Map</h5>
                <p class="text-muted">Click to select your location</p>
                <button type="button" class="btn btn-primary" onclick="openMapSelector()">
                    <i class="fas fa-map-pin me-2"></i>
                    Select Location
                </button>
            </div>
        </div>
    `;
}

// Map selector (placeholder)
function openMapSelector() {
    // This would open a map modal or redirect to map selection
    alert('Map selector would open here. For demo purposes, we\'ll set default coordinates.');
    
    // Set default coordinates (example: New York)
    document.getElementById('latitude').value = '40.7128';
    document.getElementById('longitude').value = '-74.0060';
    document.getElementById('city').value = 'New York';
    
    // Show success message
    const mapContainer = document.getElementById('map');
    mapContainer.innerHTML = `
        <div class="d-flex align-items-center justify-content-center h-100 bg-success text-white">
            <div class="text-center">
                <i class="fas fa-check-circle fa-3x mb-3"></i>
                <h5>Location Selected!</h5>
                <p>New York, USA</p>
            </div>
        </div>
    `;
}

// Utility functions
function showLoading(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
    button.disabled = true;
    
    return function hideLoading() {
        button.innerHTML = originalText;
        button.disabled = false;
    };
}

// Phone number formatting
function formatPhoneNumber(input) {
    let value = input.value.replace(/\D/g, '');
    
    if (value.length > 0 && !value.startsWith('+')) {
        value = '+' + value;
    }
    
    input.value = value;
}

// Auto-resize textarea
function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

// Scroll to Top functionality
function initScrollToTop() {
    const scrollButton = document.getElementById('scrollToTop');
    if (!scrollButton) return;
    
    // Show/hide button on scroll
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            scrollButton.classList.add('show');
        } else {
            scrollButton.classList.remove('show');
        }
    });
    
    // Smooth scroll to top
    scrollButton.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Category Slider functionality
function initCategorySlider() {
    const slider = document.querySelector('.category-slider');
    const prevBtn = document.querySelector('.slider-btn-prev');
    const nextBtn = document.querySelector('.slider-btn-next');
    
    if (!slider || !prevBtn || !nextBtn) return;
    
    const slideWidth = 160; // slide width + gap
    
    prevBtn.addEventListener('click', () => {
        slider.scrollBy({
            left: -slideWidth * 2,
            behavior: 'smooth'
        });
    });
    
    nextBtn.addEventListener('click', () => {
        slider.scrollBy({
            left: slideWidth * 2,
            behavior: 'smooth'
        });
    });
    
    // Auto-scroll functionality disabled
    // The auto slide functionality has been turned off for better user control
}

// Initialize auto-resize for all textareas
document.addEventListener('DOMContentLoaded', function() {
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', () => autoResizeTextarea(textarea));
        autoResizeTextarea(textarea); // Initial resize
    });
});
