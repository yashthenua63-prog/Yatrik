
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
