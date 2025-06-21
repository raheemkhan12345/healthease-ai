// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    // Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    })
    
    // Form validation
    const forms = document.querySelectorAll('.needs-validation')
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault()
                event.stopPropagation()
            }
            form.classList.add('was-validated')
        }, false)
    })
    
    // Date picker initialization
    if (typeof flatpickr !== 'undefined') {
        flatpickr('.datepicker', {
            dateFormat: "Y-m-d",
            minDate: "today"
        })
        
        flatpickr('.timepicker', {
            enableTime: true,
            noCalendar: true,
            dateFormat: "H:i",
            minuteIncrement: 15
        })
    }
    
    // Appointment calendar
    if (document.getElementById('appointmentCalendar')) {
        const calendarEl = document.getElementById('appointmentCalendar')
        const calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,timeGridDay'
            },
            events: JSON.parse(document.getElementById('appointmentData').textContent),
            eventClick: function(info) {
                window.location.href = `/appointments/${info.event.id}/`
            }
        })
        calendar.render()
    }
})