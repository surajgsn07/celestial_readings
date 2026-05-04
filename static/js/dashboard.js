/* ═══════════════════════════════════════════════════════════
   dashboard.js — Admin dashboard interactions
   ═══════════════════════════════════════════════════════════ */

// ─── Filter Bookings by Status ────────────────────────────
function filterBookings(status, btnEl) {
    // Update active tab
    document.querySelectorAll('.tab-filter').forEach(f => f.classList.remove('active'));
    btnEl.classList.add('active');

    // Filter table rows
    const rows = document.querySelectorAll('#bookingsTable tbody tr');
    rows.forEach(row => {
        if (status === 'all' || row.dataset.status === status) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}


// ─── Verify UPI Payment (Admin One-Click) ────────────────
async function verifyPayment(bookingId, btnEl) {
    if (!confirm('Verify this payment and confirm the booking?')) return;

    btnEl.disabled = true;
    btnEl.innerHTML = '<span class="spinner" style="width:14px;height:14px;border-width:2px;margin:0;"></span>';

    try {
        const res = await fetch(`/api/admin/booking/${bookingId}/verify-payment`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
        });

        if (res.ok) {
            const row = btnEl.closest('tr');
            // Update payment status badge
            const paymentCell = row.querySelector('td:nth-child(7)');
            paymentCell.innerHTML = '<span class="badge badge-paid">paid</span>';
            // Update status badge
            const statusCell = row.querySelector('td:nth-child(8)');
            statusCell.innerHTML = '<span class="badge badge-confirmed">confirmed</span>';
            // Update row data attribute
            row.dataset.status = 'confirmed';
            // Replace button with Complete button
            btnEl.parentElement.innerHTML = `
                <button class="btn btn-success btn-sm" onclick="markComplete(${bookingId}, this)">
                    <i data-lucide="check" style="width:12px;height:12px;"></i> Complete
                </button>
            `;
            if (typeof lucide !== 'undefined') lucide.createIcons();

            showToast('Payment verified & booking confirmed ✅', 'success');
        } else {
            throw new Error('Failed');
        }
    } catch (err) {
        showToast('Failed to verify payment', 'error');
        btnEl.disabled = false;
        btnEl.innerHTML = '<i data-lucide="check-circle" style="width:12px;height:12px;"></i> Verify Payment';
        if (typeof lucide !== 'undefined') lucide.createIcons();
    }
}


// ─── Mark Booking as Complete ─────────────────────────────
async function markComplete(bookingId, btnEl) {
    if (!confirm('Mark this booking as completed?')) return;

    btnEl.disabled = true;
    btnEl.innerHTML = '<span class="spinner" style="width:14px;height:14px;border-width:2px;margin:0;"></span>';

    try {
        const res = await fetch(`/api/admin/booking/${bookingId}/complete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
        });

        if (res.ok) {
            const row = btnEl.closest('tr');
            // Update status badge
            const statusCell = row.querySelector('td:nth-child(8)');
            statusCell.innerHTML = '<span class="badge badge-completed">completed</span>';
            // Update row data attribute
            row.dataset.status = 'completed';
            // Replace button
            btnEl.parentElement.innerHTML = '<span style="font-size:0.8rem;color:var(--text-muted);">Done</span>';

            showToast('Booking marked as completed ✨', 'success');
        } else {
            throw new Error('Failed');
        }
    } catch (err) {
        showToast('Failed to update booking', 'error');
        btnEl.disabled = false;
        btnEl.innerHTML = '<i data-lucide="check" style="width:12px;height:12px;"></i> Complete';
        if (typeof lucide !== 'undefined') lucide.createIcons();
    }
}


// ─── Cancel Booking ───────────────────────────────────────
async function cancelBooking(bookingId, btnEl) {
    if (!confirm('Cancel this booking?')) return;

    btnEl.disabled = true;
    btnEl.innerHTML = '<span class="spinner" style="width:14px;height:14px;border-width:2px;margin:0;"></span>';

    try {
        const res = await fetch(`/api/admin/booking/${bookingId}/cancel`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
        });

        if (res.ok) {
            const row = btnEl.closest('tr');
            const statusCell = row.querySelector('td:nth-child(8)');
            statusCell.innerHTML = '<span class="badge badge-cancelled">cancelled</span>';
            row.dataset.status = 'cancelled';
            btnEl.parentElement.innerHTML = '<span style="font-size:0.8rem;color:var(--text-muted);">—</span>';

            showToast('Booking cancelled', 'info');
        } else {
            throw new Error('Failed');
        }
    } catch (err) {
        showToast('Failed to cancel booking', 'error');
        btnEl.disabled = false;
        btnEl.innerHTML = '<i data-lucide="x" style="width:12px;height:12px;"></i> Cancel';
        if (typeof lucide !== 'undefined') lucide.createIcons();
    }
}
