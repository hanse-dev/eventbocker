document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const dateInput = document.getElementById('date');
    const capacityInput = document.getElementById('capacity');
    const priceInput = document.getElementById('price');

    // Set min date to current date and time
    function updateMinDate() {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const minDateTime = `${year}-${month}-${day}T${hours}:${minutes}`;
        dateInput.min = minDateTime;
    }

    // Initial setup
    updateMinDate();
    // Update min date every minute
    setInterval(updateMinDate, 60000);

    // Format price to always show 2 decimal places
    priceInput.addEventListener('change', function() {
        const value = parseFloat(this.value);
        if (!isNaN(value)) {
            this.value = value.toFixed(2);
        }
    });

    // Form validation
    form.addEventListener('submit', function(event) {
        let isValid = true;
        const errors = [];

        // Validate date
        const selectedDate = new Date(dateInput.value);
        const now = new Date();
        if (selectedDate <= now) {
            errors.push('Das Datum muss in der Zukunft liegen.');
            isValid = false;
            dateInput.classList.add('is-invalid');
        } else {
            dateInput.classList.remove('is-invalid');
        }

        // Validate capacity
        const capacity = parseInt(capacityInput.value);
        if (isNaN(capacity) || capacity <= 0) {
            errors.push('Die Kapazität muss größer als 0 sein.');
            isValid = false;
            capacityInput.classList.add('is-invalid');
        } else {
            capacityInput.classList.remove('is-invalid');
        }

        // Validate price
        const price = parseFloat(priceInput.value);
        if (isNaN(price) || price < 0) {
            errors.push('Der Preis darf nicht negativ sein.');
            isValid = false;
            priceInput.classList.add('is-invalid');
        } else {
            priceInput.classList.remove('is-invalid');
        }

        // Show errors if any
        const errorContainer = document.getElementById('error-container');
        if (!isValid) {
            event.preventDefault();
            errorContainer.innerHTML = errors.map(error => `<div class="alert alert-danger">${error}</div>`).join('');
            errorContainer.style.display = 'block';
        } else {
            errorContainer.style.display = 'none';
        }
    });
});
