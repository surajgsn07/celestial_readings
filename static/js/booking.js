/* ═══════════════════════════════════════════════════════════
   booking.js — Multi-step booking flow
   ═══════════════════════════════════════════════════════════ */

(function() {
    // ─── State ─────────────────────────────────────────────
    let currentStep = 1;
    let selectedService = null;
    let selectedDate = null;
    let selectedTime = null;
    let calendarMonth = new Date().getMonth();
    let calendarYear = new Date().getFullYear();

    // ─── Elements ──────────────────────────────────────────
    const steps = document.querySelectorAll('.step');
    const stepContents = document.querySelectorAll('.booking-step-content');

    // ─── Pre-select service if passed via URL ──────────────
    const preSelectedCard = document.querySelector('.service-select-card.selected');
    if (preSelectedCard) {
        selectedService = {
            id: parseInt(preSelectedCard.dataset.serviceId),
            name: preSelectedCard.dataset.serviceName,
            price: parseFloat(preSelectedCard.dataset.servicePrice),
            duration: parseInt(preSelectedCard.dataset.serviceDuration),
        };
        document.getElementById('toStep2').disabled = false;
    }

    // ─── Step Navigation ───────────────────────────────────
    function goToStep(step) {
        currentStep = step;

        // Update step indicators
        steps.forEach(s => {
            const stepNum = parseInt(s.dataset.step);
            s.classList.remove('active', 'completed');
            if (stepNum === currentStep) s.classList.add('active');
            else if (stepNum < currentStep) s.classList.add('completed');
        });

        // Show correct content
        stepContents.forEach((content, i) => {
            content.classList.remove('active');
            if (i === currentStep - 1) content.classList.add('active');
        });

        // Re-init lucide icons
        if (typeof lucide !== 'undefined') lucide.createIcons();

        // Scroll to top of booking section
        window.scrollTo({ top: 200, behavior: 'smooth' });
    }

    // ─── Service Selection ─────────────────────────────────
    document.querySelectorAll('.service-select-card').forEach(card => {
        card.addEventListener('click', () => {
            document.querySelectorAll('.service-select-card').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');

            selectedService = {
                id: parseInt(card.dataset.serviceId),
                name: card.dataset.serviceName,
                price: parseFloat(card.dataset.servicePrice),
                duration: parseInt(card.dataset.serviceDuration),
            };

            document.getElementById('toStep2').disabled = false;
        });
    });

    // ─── Step Buttons ──────────────────────────────────────
    document.getElementById('toStep2').addEventListener('click', () => {
        if (!selectedService) return;
        goToStep(2);
        renderCalendar();
    });

    document.getElementById('backToStep1').addEventListener('click', () => goToStep(1));

    document.getElementById('toStep3').addEventListener('click', () => {
        if (!selectedDate || !selectedTime) return;
        goToStep(3);
    });

    document.getElementById('backToStep2').addEventListener('click', () => goToStep(2));

    document.getElementById('toStep4').addEventListener('click', () => {
        // Validate form
        const name = document.getElementById('customerName').value.trim();
        const email = document.getElementById('customerEmail').value.trim();
        const phone = document.getElementById('customerPhone').value.trim();

        if (!name || !email || !phone) {
            showToast('Please fill in all required fields', 'error');
            return;
        }

        // Email validation
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            showToast('Please enter a valid email address', 'error');
            return;
        }

        // Populate review
        document.getElementById('reviewService').textContent = selectedService.name;
        document.getElementById('reviewDate').textContent = formatDate(selectedDate);
        document.getElementById('reviewTime').textContent = selectedTime.display;
        document.getElementById('reviewDuration').textContent = selectedService.duration + ' minutes';
        document.getElementById('reviewName').textContent = name;
        document.getElementById('reviewEmail').textContent = email;
        document.getElementById('reviewPhone').textContent = phone;
        document.getElementById('reviewTotal').textContent = '₹' + selectedService.price.toFixed(0);

        goToStep(4);
    });

    document.getElementById('backToStep3').addEventListener('click', () => goToStep(3));

    // ─── Calendar ──────────────────────────────────────────
    function renderCalendar() {
        const title = document.getElementById('calendarTitle');
        const daysContainer = document.getElementById('calendarDays');
        const months = ['January', 'February', 'March', 'April', 'May', 'June',
                        'July', 'August', 'September', 'October', 'November', 'December'];

        title.textContent = months[calendarMonth] + ' ' + calendarYear;

        const firstDay = new Date(calendarYear, calendarMonth, 1).getDay();
        const daysInMonth = new Date(calendarYear, calendarMonth + 1, 0).getDate();
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        let html = '';

        // Empty cells for days before the 1st
        for (let i = 0; i < firstDay; i++) {
            html += '<div class="calendar-day empty"></div>';
        }

        // Day cells
        for (let day = 1; day <= daysInMonth; day++) {
            const date = new Date(calendarYear, calendarMonth, day);
            const isPast = date < today;
            const isToday = date.getTime() === today.getTime();
            const isSelected = selectedDate &&
                selectedDate.getFullYear() === date.getFullYear() &&
                selectedDate.getMonth() === date.getMonth() &&
                selectedDate.getDate() === date.getDate();

            let classes = 'calendar-day';
            if (isPast) classes += ' disabled';
            if (isToday) classes += ' today';
            if (isSelected) classes += ' selected';

            html += `<div class="${classes}" data-date="${calendarYear}-${String(calendarMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}">${day}</div>`;
        }

        daysContainer.innerHTML = html;

        // Add click handlers
        daysContainer.querySelectorAll('.calendar-day:not(.disabled):not(.empty)').forEach(dayEl => {
            dayEl.addEventListener('click', () => {
                daysContainer.querySelectorAll('.calendar-day').forEach(d => d.classList.remove('selected'));
                dayEl.classList.add('selected');
                selectedDate = new Date(dayEl.dataset.date + 'T00:00:00');
                selectedTime = null;
                document.getElementById('toStep3').disabled = true;
                fetchTimeSlots(dayEl.dataset.date);
            });
        });
    }

    // Calendar navigation
    document.getElementById('prevMonth').addEventListener('click', () => {
        const now = new Date();
        if (calendarYear === now.getFullYear() && calendarMonth === now.getMonth()) return;
        calendarMonth--;
        if (calendarMonth < 0) { calendarMonth = 11; calendarYear--; }
        renderCalendar();
    });

    document.getElementById('nextMonth').addEventListener('click', () => {
        calendarMonth++;
        if (calendarMonth > 11) { calendarMonth = 0; calendarYear++; }
        renderCalendar();
    });

    // ─── Time Slots ────────────────────────────────────────
    async function fetchTimeSlots(dateStr) {
        const container = document.getElementById('timeSlotsContainer');
        const slotsDiv = document.getElementById('timeSlots');
        const noSlots = document.getElementById('noSlots');
        const dateDisplay = document.getElementById('selectedDateDisplay');

        container.style.display = 'block';
        dateDisplay.textContent = formatDate(new Date(dateStr + 'T00:00:00'));
        slotsDiv.innerHTML = '<div class="spinner"></div>';
        noSlots.style.display = 'none';

        try {
            const res = await fetch(`/api/available-slots?date=${dateStr}&service_id=${selectedService.id}`);
            const data = await res.json();

            if (data.slots && data.slots.length > 0) {
                slotsDiv.innerHTML = data.slots.map(slot => `
                    <div class="time-slot" data-time="${slot.time}" data-display="${slot.display}">
                        ${slot.display}
                    </div>
                `).join('');

                // Add click handlers
                slotsDiv.querySelectorAll('.time-slot').forEach(slotEl => {
                    slotEl.addEventListener('click', () => {
                        slotsDiv.querySelectorAll('.time-slot').forEach(s => s.classList.remove('selected'));
                        slotEl.classList.add('selected');
                        selectedTime = {
                            time: slotEl.dataset.time,
                            display: slotEl.dataset.display,
                        };
                        document.getElementById('toStep3').disabled = false;
                    });
                });
            } else {
                slotsDiv.innerHTML = '';
                noSlots.style.display = 'block';
            }
        } catch (err) {
            slotsDiv.innerHTML = '';
            showToast('Failed to load time slots', 'error');
        }
    }

    // ─── Submit Booking ────────────────────────────────────
    document.getElementById('submitBooking').addEventListener('click', async () => {
        const btn = document.getElementById('submitBooking');
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner" style="width:18px;height:18px;border-width:2px;margin:0;"></span> Processing...';

        const bookingData = {
            service_id: selectedService.id,
            customer_name: document.getElementById('customerName').value.trim(),
            email: document.getElementById('customerEmail').value.trim(),
            phone: document.getElementById('customerPhone').value.trim(),
            booking_date: selectedDate.toISOString().split('T')[0],
            time_slot: selectedTime.time,
            notes: document.getElementById('customerNotes').value.trim(),
        };

        try {
            const res = await fetch('/api/booking', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(bookingData),
            });

            const data = await res.json();

            if (res.ok) {
                // Redirect to confirmation/payment page
                window.location.href = `/booking/confirm/${data.booking_id}`;
            } else {
                showToast(data.error || 'Failed to create booking', 'error');
                btn.disabled = false;
                btn.innerHTML = '<i data-lucide="credit-card" style="width:18px;height:18px;"></i> Proceed to Payment';
                if (typeof lucide !== 'undefined') lucide.createIcons();
            }
        } catch (err) {
            showToast('Network error. Please try again.', 'error');
            btn.disabled = false;
            btn.innerHTML = '<i data-lucide="credit-card" style="width:18px;height:18px;"></i> Proceed to Payment';
            if (typeof lucide !== 'undefined') lucide.createIcons();
        }
    });

    // ─── Helpers ───────────────────────────────────────────
    function formatDate(date) {
        const months = ['January', 'February', 'March', 'April', 'May', 'June',
                        'July', 'August', 'September', 'October', 'November', 'December'];
        return months[date.getMonth()] + ' ' + date.getDate() + ', ' + date.getFullYear();
    }

})();
