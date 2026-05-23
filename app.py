import os
import logging
from datetime import datetime, date, timedelta
from flask import (
    Flask, render_template, request, jsonify, redirect, url_for, flash, session
)
from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user
)
from config import Config
from models import db, Admin, Service, Booking, ContactMessage

# ─── App Factory ───────────────────────────────────────────────
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "admin_login"


@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))


# ─── Seed Data ─────────────────────────────────────────────────
def seed_data():
    """Seed default admin and services if they don't exist."""
    try:
        # Create or update admin from environment variables
        admin_username = app.config["ADMIN_USERNAME"]
        admin_password = app.config["ADMIN_PASSWORD"]
        
        admin = Admin.query.filter_by(username=admin_username).first()
        if not admin:
            admin = Admin(username=admin_username)
            admin.set_password(admin_password)
            db.session.add(admin)
        else:
            # Update password if changed in .env
            admin.set_password(admin_password)

        # Create services only if none exist
        if Service.query.count() == 0:
            services = [
                Service(
                    name="Vedic Tarot Reading",
                    slug="vedic-tarot-reading",
                    description="Unlock the ancient wisdom of Vedic Tarot to gain deep insights into your life path, karmic patterns, and spiritual journey. This session combines traditional tarot symbolism with Vedic astrology principles for a truly transformative experience. Each card drawn reveals layers of meaning connected to your unique cosmic blueprint.",
                    short_description="Ancient Vedic wisdom meets tarot for deep life path insights",
                    duration=60,
                    price=1499.00,
                    icon="sparkles",
                    category="tarot",
                    display_order=1,
                ),
                Service(
                    name="Birth Chart Analysis",
                    slug="birth-chart-analysis",
                    description="A comprehensive analysis of your natal chart revealing your personality traits, life purpose, strengths, challenges, and the cosmic energies that shape your destiny. We'll explore your sun, moon, and rising signs along with planetary placements to paint a complete picture of your astrological DNA.",
                    short_description="Complete natal chart reading revealing your cosmic blueprint",
                    duration=90,
                    price=2499.00,
                    icon="sun",
                    category="astrology",
                    display_order=2,
                ),
                Service(
                    name="Relationship Guidance",
                    slug="relationship-guidance",
                    description="Explore the cosmic compatibility between you and your partner through synastry chart analysis. Understand the strengths, challenges, and karmic connections in your relationship. This session helps illuminate the deeper spiritual purpose of your bond and offers guidance for harmony.",
                    short_description="Synastry analysis for cosmic compatibility & harmony",
                    duration=60,
                    price=1999.00,
                    icon="heart",
                    category="astrology",
                    display_order=3,
                ),
                Service(
                    name="Tarot Reading",
                    slug="tarot-reading",
                    description="A classic intuitive tarot reading to answer your most pressing questions. Whether it's about love, career, finances, or personal growth — the cards will illuminate the path ahead. Each spread is custom-designed for your specific situation and delivered with compassionate clarity.",
                    short_description="Intuitive tarot guidance for life's pressing questions",
                    duration=45,
                    price=999.00,
                    icon="star",
                    category="tarot",
                    display_order=4,
                ),
                Service(
                    name="Custom Spiritual Session",
                    slug="custom-spiritual-session",
                    description="A personalized session tailored to your unique needs. Whether you seek a combination of tarot and astrology, a deep-dive into a specific life area, or ongoing spiritual mentorship — this session is crafted just for you. We'll discuss your goals beforehand to design the perfect experience.",
                    short_description="Bespoke session designed around your unique spiritual needs",
                    duration=120,
                    price=2999.00,
                    icon="wand-2",
                    category="custom",
                    display_order=5,
                ),
            ]
            db.session.add_all(services)

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error seeding data: {e}")
        # Don't fail the app startup if seeding fails


# ─── PUBLIC ROUTES ─────────────────────────────────────────────

@app.route("/")
def home():
    services = Service.query.filter_by(is_active=True).order_by(Service.display_order).limit(3).all()
    return render_template("index.html", services=services)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/services")
def services():
    all_services = Service.query.filter_by(is_active=True).order_by(Service.display_order).all()
    return render_template("services.html", services=all_services)


@app.route("/booking")
def booking():
    service_id = request.args.get("service_id", None)
    all_services = Service.query.filter_by(is_active=True).order_by(Service.display_order).all()
    selected_service = None
    if service_id:
        selected_service = Service.query.get(int(service_id))
    return render_template(
        "booking.html",
        services=all_services,
        selected_service=selected_service,
    )


@app.route("/contact")
def contact():
    return render_template("contact.html")


# ─── BOOKING API ───────────────────────────────────────────────

@app.route("/api/services", methods=["GET"])
def api_services():
    services = Service.query.filter_by(is_active=True).order_by(Service.display_order).all()
    return jsonify([s.to_dict() for s in services])


@app.route("/api/available-slots", methods=["GET"])
def available_slots():
    """Return available time slots for a given date."""
    date_str = request.args.get("date")
    service_id = request.args.get("service_id")

    if not date_str:
        return jsonify({"error": "Date is required"}), 400

    try:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    # Don't allow past dates
    if selected_date < date.today():
        return jsonify({"slots": []})

    # Generate time slots (10 AM to 7 PM)
    all_slots = []
    for hour in range(10, 19):
        slot_time = f"{hour:02d}:00"
        display_time = datetime.strptime(slot_time, "%H:%M").strftime("%I:%M %p")
        all_slots.append({"time": slot_time, "display": display_time})

    # Remove already booked slots
    booked = Booking.query.filter(
        Booking.booking_date == selected_date,
        Booking.status.in_(["pending", "awaiting_verification", "confirmed"]),
    ).all()
    booked_times = {b.time_slot for b in booked}

    available = [s for s in all_slots if s["time"] not in booked_times]
    return jsonify({"slots": available})


@app.route("/api/booking", methods=["POST"])
def create_booking():
    data = request.json
    required = ["service_id", "customer_name", "email", "phone", "booking_date", "time_slot"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    service = Service.query.get(data["service_id"])
    if not service:
        return jsonify({"error": "Service not found"}), 404

    try:
        booking_date = datetime.strptime(data["booking_date"], "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    # Check if slot is available
    existing = Booking.query.filter_by(
        booking_date=booking_date,
        time_slot=data["time_slot"],
    ).filter(
        Booking.status.in_(["confirmed", "awaiting_verification"])
    ).first()
    if existing:
        return jsonify({"error": "This time slot is no longer available"}), 409

    booking = Booking(
        service_id=service.id,
        customer_name=data["customer_name"],
        email=data["email"],
        phone=data["phone"],
        booking_date=booking_date,
        time_slot=data["time_slot"],
        notes=data.get("notes", ""),
        amount=service.price,
        status="pending",
        payment_status="unpaid",
        payment_method="upi",
    )
    db.session.add(booking)
    db.session.commit()

    return jsonify({
        "booking_id": booking.id,
        "amount": booking.amount,
        "service_name": service.name,
        "message": "Booking created, proceed to payment",
    }), 201


@app.route("/booking/confirm/<int:booking_id>")
def booking_confirm(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    return render_template(
        "booking_confirm.html",
        booking=booking,
        upi_id=app.config["UPI_ID"],
        upi_name=app.config["UPI_NAME"],
        whatsapp_number=app.config["WHATSAPP_NUMBER"],
    )


# ─── UPI PAYMENT API ─────────────────────────────────────────

@app.route("/api/submit-payment-proof", methods=["POST"])
def submit_payment_proof():
    """Customer submits their UPI transaction ID after paying."""
    data = request.json
    booking_id = data.get("booking_id")
    transaction_id = data.get("transaction_id", "").strip()

    if not booking_id:
        return jsonify({"error": "Booking ID is required"}), 400

    if not transaction_id:
        return jsonify({"error": "Transaction ID / UTR is required"}), 400

    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    if booking.payment_status == "paid":
        return jsonify({"error": "Payment already verified"}), 400

    booking.transaction_id = transaction_id
    booking.status = "awaiting_verification"
    booking.payment_status = "awaiting_verification"
    db.session.commit()

    app.logger.info(
        f"[PAYMENT-PROOF] Booking #{booking.id} — UTR: {transaction_id} — Awaiting admin verification"
    )

    return jsonify({
        "status": "success",
        "booking_id": booking.id,
        "message": "Payment proof submitted. We will verify and confirm your booking shortly.",
    })


@app.route("/payment/pending/<int:booking_id>")
def payment_pending(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    return render_template(
        "payment_pending.html",
        booking=booking,
        whatsapp_number=app.config["WHATSAPP_NUMBER"],
    )


@app.route("/payment/success/<int:booking_id>")
def payment_success(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    return render_template("payment_success.html", booking=booking)


@app.route("/payment/failure/<int:booking_id>")
def payment_failure(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    return render_template("payment_failure.html", booking=booking)


# ─── CONTACT API ──────────────────────────────────────────────

@app.route("/api/contact", methods=["POST"])
def submit_contact():
    data = request.json
    required = ["name", "email", "message"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    msg = ContactMessage(
        name=data["name"],
        email=data["email"],
        message=data["message"],
    )
    db.session.add(msg)
    db.session.commit()
    return jsonify({"message": "Thank you! We'll get back to you soon ✨"}), 201


# ─── CUSTOMER TRACKING ────────────────────────────────────────

@app.route("/track", methods=["GET", "POST"])
def track_booking():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        
        if not email or not phone:
            flash("Please provide both email and phone number.", "error")
            return redirect(url_for("track_booking"))
        
        # Normalize phone: strip +, spaces, dashes, then take last 10 digits
        phone_digits = ''.join(c for c in phone if c.isdigit())
        if len(phone_digits) >= 10:
            phone_normalized = phone_digits[-10:]  # Last 10 digits
        else:
            phone_normalized = phone_digits
            
        # Search bookings — match email AND last 10 digits of phone
        all_bookings = Booking.query.filter(
            Booking.email.ilike(email)
        ).order_by(Booking.created_at.desc()).all()
        
        # Filter by phone match (last 10 digits)
        bookings = []
        for b in all_bookings:
            b_phone = ''.join(c for c in (b.phone or '') if c.isdigit())
            if len(b_phone) >= 10:
                b_phone = b_phone[-10:]
            if b_phone == phone_normalized:
                bookings.append(b)
        
        if not bookings:
            flash("No bookings found with that email and phone combination.", "error")
            return redirect(url_for("track_booking"))
            
        return render_template("my_bookings.html", bookings=bookings, email=email, phone=phone)
        
    return render_template("track_booking.html")


# ─── ADMIN ROUTES ─────────────────────────────────────────────

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.check_password(password):
            login_user(admin)
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid credentials", "error")

    return render_template("admin/login.html")


@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(10).all()

    # Stats
    total_bookings = len(bookings)
    confirmed = sum(1 for b in bookings if b.status == "confirmed")
    completed = sum(1 for b in bookings if b.status == "completed")
    pending = sum(1 for b in bookings if b.status == "pending")
    awaiting = sum(1 for b in bookings if b.status == "awaiting_verification")
    total_revenue = sum(b.amount for b in bookings if b.payment_status == "paid")

    return render_template(
        "admin/dashboard.html",
        bookings=bookings,
        messages=messages,
        stats={
            "total": total_bookings,
            "confirmed": confirmed,
            "completed": completed,
            "pending": pending,
            "awaiting": awaiting,
            "revenue": total_revenue,
        },
    )


@app.route("/api/admin/booking/<int:booking_id>/verify-payment", methods=["POST"])
@login_required
def verify_payment(booking_id):
    """Admin one-click: verify a UPI payment and confirm the booking."""
    booking = Booking.query.get_or_404(booking_id)

    booking.payment_status = "paid"
    booking.status = "confirmed"
    booking.payment_verified_at = datetime.utcnow()
    booking.payment_verified_by = current_user.username
    db.session.commit()

    app.logger.info(
        f"[VERIFY-PAYMENT] ✅ Booking #{booking.id} verified by {current_user.username} — UTR: {booking.transaction_id}"
    )

    return jsonify({
        "message": "Payment verified and booking confirmed",
        "status": "confirmed",
        "payment_status": "paid",
    })


@app.route("/api/admin/booking/<int:booking_id>/complete", methods=["POST"])
@login_required
def mark_complete(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    booking.status = "completed"
    db.session.commit()
    return jsonify({"message": "Booking marked as completed", "status": "completed"})


@app.route("/api/admin/booking/<int:booking_id>/cancel", methods=["POST"])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    booking.status = "cancelled"
    db.session.commit()
    return jsonify({"message": "Booking cancelled", "status": "cancelled"})


@app.route("/admin/logout")
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for("home"))


# ─── INITIALIZATION ───────────────────────────────────────────

with app.app_context():
    db.create_all()
    seed_data()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
