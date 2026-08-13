from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, current_app
from flask_login import login_required, current_user
from app.models import Hotel, Restaurant, Driver, Document, FoodCategory, FoodItem, ClaimRequest
from app.database import db
from werkzeug.utils import secure_filename
import os
import uuid

partner_bp = Blueprint('partner', __name__, url_prefix='/partner')

ALLOWED_DOC_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
MAX_DOC_SIZE_MB = 5


def _allowed_doc(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_DOC_EXTENSIONS


def _save_private_document(file, user_id, doc_type):
    """Save a file to private storage outside static/. Returns stored filename."""
    ext = file.filename.rsplit('.', 1)[-1].lower()
    unique_name = f"user_{user_id}_{doc_type}_{uuid.uuid4().hex}.{ext}"
    upload_folder = current_app.config.get('PRIVATE_UPLOADS_PATH',
                                           os.path.join(current_app.root_path, 'private_uploads'))
    os.makedirs(upload_folder, exist_ok=True)
    file.save(os.path.join(upload_folder, unique_name))
    return unique_name


def _calc_completion(obj, required_fields):
    """Return % profile completion based on which fields are non-empty."""
    filled = sum(1 for f in required_fields if getattr(obj, f, None))
    return int(filled / len(required_fields) * 100) if required_fields else 0


@partner_bp.route('/driver/dashboard')
@login_required
def driver_dashboard():
    if current_user.is_admin:
        return redirect('/admin-yatrik-secret')
    if not current_user.is_driver:
        abort(403)

    driver = Driver.query.filter_by(user_id=current_user.id).first()
    driver_fields = ['name', 'phone', 'vehicle_type', 'vehicle_number', 'service_area']
    driver_completion = _calc_completion(driver, driver_fields) if driver else 0

    return render_template('pages/partner/driver_dashboard.html',
                           driver=driver,
                           driver_completion=driver_completion)

@partner_bp.route('/hotel/dashboard')
@login_required
def hotel_dashboard():
    if current_user.is_admin:
        return redirect('/admin-yatrik-secret')
    if not current_user.is_hotel_partner:
        abort(403)

    hotels = Hotel.query.filter_by(owner_id=current_user.id).all()
    hotel_fields = ['name', 'description', 'address', 'phone', 'official_website']
    hotel_completions = {h.id: _calc_completion(h, hotel_fields) for h in hotels}

    return render_template('pages/partner/hotel_dashboard.html',
                           hotels=hotels,
                           hotel_completions=hotel_completions)

@partner_bp.route('/restaurant/dashboard')
@login_required
def restaurant_dashboard():
    if current_user.is_admin:
        return redirect('/admin-yatrik-secret')
    if not current_user.is_restaurant_partner:
        abort(403)

    restaurants = Restaurant.query.filter_by(owner_id=current_user.id).all()
    restaurant_fields = ['name', 'description', 'cuisine', 'timings', 'address', 'phone']
    restaurant_completions = {r.id: _calc_completion(r, restaurant_fields) for r in restaurants}

    return render_template('pages/partner/restaurant_dashboard.html',
                           restaurants=restaurants,
                           restaurant_completions=restaurant_completions)


# ── Hotel Onboard ─────────────────────────────────────────────────────────────

@partner_bp.route('/onboard/hotel', methods=['GET', 'POST'])
@login_required
def onboard_hotel():
    if not current_user.is_hotel_partner:
        abort(403)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Property name is required.', 'warning')
            return render_template('pages/partner/onboard_hotel.html')

        slug_base = name.lower().replace(' ', '-')
        # Ensure unique slug
        slug = slug_base
        counter = 1
        while Hotel.query.filter_by(slug=slug).first():
            slug = f"{slug_base}-{counter}"
            counter += 1

        hotel = Hotel(
            owner_id=current_user.id,
            name=name,
            slug=slug,
            city=request.form.get('city', 'Vrindavan').strip(),
            address=request.form.get('address', '').strip(),
            phone=request.form.get('phone', '').strip(),
            official_website=request.form.get('website', '').strip(),
            description=request.form.get('description', '').strip(),
            amenities=request.form.get('amenities', '').strip(),
            price_range=request.form.get('price_range', '').strip(),
            verification_status='PENDING'
        )
        db.session.add(hotel)
        db.session.commit()

        flash('Property submitted for verification. Our team will review it shortly.', 'success')
        return redirect(url_for('partner.hotel_dashboard'))

    return render_template('pages/partner/onboard_hotel.html')


# ── Hotel Edit ────────────────────────────────────────────────────────────────

@partner_bp.route('/hotel/<int:hotel_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_hotel(hotel_id):
    hotel = Hotel.query.get_or_404(hotel_id)
    if hotel.owner_id != current_user.id and not current_user.is_admin:
        abort(403)

    if request.method == 'POST':
        hotel.name = request.form.get('name', hotel.name).strip()
        hotel.city = request.form.get('city', hotel.city).strip()
        hotel.address = request.form.get('address', hotel.address or '').strip()
        hotel.phone = request.form.get('phone', hotel.phone or '').strip()
        hotel.official_website = request.form.get('website', hotel.official_website or '').strip()
        hotel.booking_url = request.form.get('booking_url', hotel.booking_url or '').strip()
        hotel.description = request.form.get('description', hotel.description or '').strip()
        hotel.amenities = request.form.get('amenities', hotel.amenities or '').strip()
        hotel.price_range = request.form.get('price_range', hotel.price_range or '').strip()
        db.session.commit()
        flash('Property details updated.', 'success')
        return redirect(url_for('partner.hotel_dashboard'))

    return render_template('pages/partner/edit_hotel.html', hotel=hotel)


# ── Restaurant Onboard ────────────────────────────────────────────────────────

@partner_bp.route('/onboard/restaurant', methods=['GET', 'POST'])
@login_required
def onboard_restaurant():
    if not current_user.is_restaurant_partner:
        abort(403)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Restaurant name is required.', 'warning')
            return render_template('pages/partner/onboard_restaurant.html')

        slug_base = name.lower().replace(' ', '-')
        slug = slug_base
        counter = 1
        while Restaurant.query.filter_by(slug=slug).first():
            slug = f"{slug_base}-{counter}"
            counter += 1

        restaurant = Restaurant(
            owner_id=current_user.id,
            name=name,
            slug=slug,
            cuisine=request.form.get('cuisine', '').strip(),
            timings=request.form.get('timings', '').strip(),
            city=request.form.get('city', 'Vrindavan').strip(),
            address=request.form.get('address', '').strip(),
            phone=request.form.get('phone', '').strip(),
            website=request.form.get('website', '').strip(),
            description=request.form.get('description', '').strip(),
            price_range=request.form.get('price_range', '').strip(),
            verification_status='PENDING'
        )
        db.session.add(restaurant)
        db.session.commit()

        flash('Restaurant submitted for verification.', 'success')
        return redirect(url_for('partner.restaurant_dashboard'))

    return render_template('pages/partner/onboard_restaurant.html')


# ── Restaurant Edit ───────────────────────────────────────────────────────────

@partner_bp.route('/restaurant/<int:restaurant_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_restaurant(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    if restaurant.owner_id != current_user.id and not current_user.is_admin:
        abort(403)

    if request.method == 'POST':
        restaurant.name = request.form.get('name', restaurant.name).strip()
        restaurant.cuisine = request.form.get('cuisine', restaurant.cuisine or '').strip()
        restaurant.timings = request.form.get('timings', restaurant.timings or '').strip()
        restaurant.city = request.form.get('city', restaurant.city).strip()
        restaurant.address = request.form.get('address', restaurant.address or '').strip()
        restaurant.phone = request.form.get('phone', restaurant.phone or '').strip()
        restaurant.website = request.form.get('website', restaurant.website or '').strip()
        restaurant.description = request.form.get('description', restaurant.description or '').strip()
        restaurant.price_range = request.form.get('price_range', restaurant.price_range or '').strip()
        db.session.commit()
        flash('Restaurant details updated.', 'success')
        return redirect(url_for('partner.restaurant_dashboard'))

    return render_template('pages/partner/edit_restaurant.html', restaurant=restaurant)


# ── Driver Onboard ────────────────────────────────────────────────────────────

@partner_bp.route('/onboard/driver', methods=['GET', 'POST'])
@login_required
def onboard_driver():
    if not current_user.is_driver:
        abort(403)
    if Driver.query.filter_by(user_id=current_user.id).first():
        flash('You already have a driver profile.', 'info')
        return redirect(url_for('partner.driver_dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        vehicle_type = request.form.get('vehicle_type', 'E-Rickshaw').strip()
        vehicle_number = request.form.get('vehicle_number', '').strip().upper()

        if not all([name, phone, vehicle_number]):
            flash('Name, phone and vehicle number are required.', 'warning')
            return render_template('pages/partner/onboard_driver.html')

        if Driver.query.filter_by(phone=phone).first():
            flash('A driver with this phone number already exists.', 'warning')
            return render_template('pages/partner/onboard_driver.html')

        if Driver.query.filter_by(vehicle_number=vehicle_number).first():
            flash('A driver with this vehicle number already exists.', 'warning')
            return render_template('pages/partner/onboard_driver.html')

        driver = Driver(
            user_id=current_user.id,
            name=name,
            phone=phone,
            vehicle_type=vehicle_type,
            vehicle_number=vehicle_number,
            service_area=request.form.get('service_area', 'Vrindavan').strip(),
            status='OFFLINE',
            verification_status='PENDING'
        )
        db.session.add(driver)
        db.session.flush()  # Get driver id before commit

        # Handle secure document upload
        license_file = request.files.get('license_document')
        if license_file and license_file.filename:
            if not _allowed_doc(license_file.filename):
                flash('Only PDF, JPG, and PNG files are accepted.', 'warning')
                db.session.rollback()
                return render_template('pages/partner/onboard_driver.html')

            stored_name = _save_private_document(license_file, current_user.id, 'license')
            doc = Document(
                user_id=current_user.id,
                document_type='ID_PROOF',
                file_path=stored_name,
                status='PENDING'
            )
            db.session.add(doc)

        db.session.commit()
        flash('Driver profile submitted for verification. We will review your documents shortly.', 'success')
        return redirect(url_for('partner.driver_dashboard'))

    return render_template('pages/partner/onboard_driver.html')


# ── Driver Toggle Status ──────────────────────────────────────────────────────

@partner_bp.route('/driver/toggle-status', methods=['POST'])
@login_required
def toggle_driver_status():
    driver = Driver.query.filter_by(user_id=current_user.id).first_or_404()
    if driver.verification_status != 'VERIFIED':
        flash('Only verified drivers can change their status.', 'warning')
        return redirect(url_for('partner.driver_dashboard'))

    driver.status = 'ONLINE' if driver.status == 'OFFLINE' else 'OFFLINE'
    db.session.commit()
    flash(f'Status updated to {driver.status}.', 'success')
    return redirect(url_for('partner.driver_dashboard'))

# ── Menu Management ────────────────────────────────────────────────────────

@partner_bp.route('/restaurant/<int:restaurant_id>/categories', methods=['POST'])
@login_required
def add_food_category(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    if restaurant.owner_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    name = request.form.get('name', '').strip()
    if name:
        category = FoodCategory(restaurant_id=restaurant.id, name=name, description=request.form.get('description', '').strip())
        db.session.add(category)
        db.session.commit()
        flash('Category added.', 'success')
    return redirect(url_for('partner.edit_restaurant', restaurant_id=restaurant.id))

@partner_bp.route('/restaurant/<int:restaurant_id>/items', methods=['POST'])
@login_required
def add_food_item(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    if restaurant.owner_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    category_id = request.form.get('category_id')
    category = FoodCategory.query.get_or_404(category_id)
    if category.restaurant_id != restaurant.id:
        abort(403)
    
    name = request.form.get('name', '').strip()
    price = request.form.get('price', type=float)
    if name and price is not None:
        item = FoodItem(
            category_id=category.id,
            name=name,
            description=request.form.get('description', '').strip(),
            price=price,
            is_veg=request.form.get('is_veg') == '1'
        )
        db.session.add(item)
        db.session.commit()
        flash('Food item added.', 'success')
    return redirect(url_for('partner.edit_restaurant', restaurant_id=restaurant.id))

@partner_bp.route('/restaurant/<int:restaurant_id>/items/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_food_item(restaurant_id, item_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    if restaurant.owner_id != current_user.id and not current_user.is_admin:
        abort(403)
        
    item = FoodItem.query.get_or_404(item_id)
    if item.category.restaurant_id != restaurant.id:
        abort(403)
        
    db.session.delete(item)
    db.session.commit()
    flash('Food item deleted.', 'success')
    return redirect(url_for('partner.edit_restaurant', restaurant_id=restaurant.id))

# ── Claim Listing ────────────────────────────────────────────────────────

@partner_bp.route('/claim', methods=['GET', 'POST'])
@login_required
def claim_listing():
    if request.method == 'POST':
        entity_type = request.form.get('entity_type', '').upper()
        entity_id = request.form.get('entity_id', type=int)
        message = request.form.get('message', '').strip()
        contact = request.form.get('contact_number', '').strip()
        
        if not entity_type or not entity_id:
            flash('Invalid listing to claim.', 'warning')
            return redirect(url_for('main.index'))
            
        claim = ClaimRequest(
            user_id=current_user.id,
            entity_type=entity_type,
            entity_id=entity_id,
            message=message,
            contact_number=contact
        )
        db.session.add(claim)
        db.session.commit()
        flash('Claim request submitted successfully. We will contact you soon.', 'success')
        return redirect(url_for('main.index'))
        
    return render_template('pages/partner/claim.html')
