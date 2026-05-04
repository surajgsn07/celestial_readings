/* ═══════════════════════════════════════════════════════════
   upi-payment.js — UPI payment proof submission
   ═══════════════════════════════════════════════════════════ */

(function() {
    const submitBtn = document.getElementById('submitProofBtn');
    const transactionInput = document.getElementById('transactionId');

    if (!submitBtn || !transactionInput) return;

    submitBtn.addEventListener('click', async () => {
        const transactionId = transactionInput.value.trim();
        const bookingId = submitBtn.dataset.bookingId;
        const whatsappNumber = submitBtn.dataset.whatsapp;
        const serviceName = submitBtn.dataset.service;
        const amount = submitBtn.dataset.amount;
        const customerName = submitBtn.dataset.customer;

        // Validate
        if (!transactionId) {
            showToast('Please enter your UPI Transaction ID / UTR', 'error');
            transactionInput.focus();
            return;
        }

        if (transactionId.length < 6) {
            showToast('Transaction ID seems too short. Please check and try again.', 'error');
            transactionInput.focus();
            return;
        }

        // Disable button
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner" style="width:18px;height:18px;border-width:2px;margin:0;"></span> Submitting...';

        try {
            const res = await fetch('/api/submit-payment-proof', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    booking_id: parseInt(bookingId),
                    transaction_id: transactionId,
                }),
            });

            const data = await res.json();

            if (res.ok) {
                // Build WhatsApp message
                const message = `Hi! I just booked *${serviceName}* (Booking #${bookingId}).\n\n`
                    + `💰 Amount: ₹${amount}\n`
                    + `🔖 Transaction ID: ${transactionId}\n`
                    + `👤 Name: ${customerName}\n\n`
                    + `Please verify my payment. Thank you! ✨`;

                const whatsappUrl = `https://wa.me/${whatsappNumber}?text=${encodeURIComponent(message)}`;

                // Redirect directly to WhatsApp
                window.location.href = whatsappUrl;
            } else {
                showToast(data.error || 'Failed to submit payment proof', 'error');
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i data-lucide="send" style="width:18px;height:18px;"></i> I Have Paid — Submit Proof';
                if (typeof lucide !== 'undefined') lucide.createIcons();
            }
        } catch (err) {
            showToast('Network error. Please try again.', 'error');
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i data-lucide="send" style="width:18px;height:18px;"></i> I Have Paid — Submit Proof';
            if (typeof lucide !== 'undefined') lucide.createIcons();
        }
    });

    // Allow Enter key to submit
    transactionInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            submitBtn.click();
        }
    });
})();
