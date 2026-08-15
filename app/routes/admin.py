from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from app.database import db

class SecureAdminIndexView(AdminIndexView):
    def is_accessible(self):
        from flask_login import current_user
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))
VERIFICATION_CHOICES = [
    ('DRAFT', 'Draft'),
    ('PENDING', 'Pending'),
    ('VERIFIED', 'Verified'),
    ('PUBLISHED', 'Published'),
    ('REJECTED', 'Rejected'),
]


def setup_admin(app):
    from app.models import (
        Temple, Place, Category, Hotel, Restaurant,
        Driver, FareRule, Ride,
        User, Document, Review, ClaimRequest,
        Event, FoodTrail, FoodTrailStop,
        SupportTicket, LocalSeller, FoodCategory, FoodItem,
        DiscoveredEntity, CollectorLog, NewsArticle
    )

    admin = Admin(app, name='Yatrik Admin', url='/admin-yatrik-secret', index_view=SecureAdminIndexView(url='/admin-yatrik-secret'))

    class YatrikModelView(ModelView):
        page_size = 50
        can_export = True

    class SecureModelView(YatrikModelView):
        def is_accessible(self):
            from flask_login import current_user
            return current_user.is_authenticated and current_user.is_admin

        def inaccessible_callback(self, name, **kwargs):
            from flask import redirect, url_for
            return redirect(url_for('auth.login'))

    class TempleView(SecureModelView):
        column_searchable_list = ['name', 'city']
        column_filters = ['verification_status', 'city']
        form_choices = {'verification_status': VERIFICATION_CHOICES}

    class PlaceView(SecureModelView):
        column_searchable_list = ['name', 'city']
        column_filters = ['verification_status', 'city']
        form_choices = {'verification_status': VERIFICATION_CHOICES}

    class HotelView(SecureModelView):
        column_searchable_list = ['name', 'city']
        column_filters = ['verification_status', 'city']
        form_choices = {'verification_status': VERIFICATION_CHOICES}

    class RestaurantView(SecureModelView):
        column_searchable_list = ['name', 'city', 'cuisine']
        column_filters = ['verification_status', 'city']
        form_choices = {'verification_status': VERIFICATION_CHOICES}

    class DriverView(SecureModelView):
        column_searchable_list = ['name', 'phone', 'vehicle_number']
        column_filters = ['status', 'verification_status']
        form_choices = {
            'status': [('OFFLINE', 'Offline'), ('ONLINE', 'Online'), ('BUSY', 'Busy')],
            'verification_status': [
                ('PENDING', 'Pending'), ('VERIFIED', 'Verified'),
                ('REJECTED', 'Rejected'), ('SUSPENDED', 'Suspended'),
            ]
        }

    class EventView(SecureModelView):
        column_searchable_list = ['title', 'city']
        column_filters = ['is_published', 'city']

    class SupportView(SecureModelView):
        column_searchable_list = ['subject', 'contact_email']
        column_filters = ['status', 'category']
        form_choices = {
            'status': [('OPEN', 'Open'), ('IN_PROGRESS', 'In Progress'),
                       ('RESOLVED', 'Resolved'), ('CLOSED', 'Closed')],
            'category': [
                ('VERIFICATION', 'Verification'), ('PROFILE', 'Profile'),
                ('TECHNICAL', 'Technical'), ('ACCOUNT', 'Account'),
                ('RIDE', 'Ride'), ('CUSTOMER_ISSUE', 'Customer Issue'), ('OTHER', 'Other'),
            ]
        }

    class LocalSellerView(SecureModelView):
        column_searchable_list = ['name', 'city']
        column_filters = ['verification_status', 'category']
        
    class DiscoveredEntityView(SecureModelView):
        column_searchable_list = ['name', 'city', 'source_url']
        column_filters = ['status', 'entity_type', 'city']
        form_choices = {
            'status': [('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected'), ('DUPLICATE', 'Duplicate')]
        }

    class NewsArticleView(SecureModelView):
        column_searchable_list = ['title', 'city', 'category']
        column_filters = ['status', 'city', 'category']
        form_choices = {
            'status': [('DRAFT', 'Draft'), ('REVIEW', 'Review'), ('PUBLISHED', 'Published'), ('UPDATED', 'Updated'), ('ARCHIVED', 'Archived')]
        }

    # ── Content ──────────────────────────────────────────────────────────────
    admin.add_view(TempleView(Temple, db.session, name="Temples", category="Content", endpoint="admin_temples"))
    admin.add_view(PlaceView(Place, db.session, name="Places", category="Content", endpoint="admin_places"))
    admin.add_view(HotelView(Hotel, db.session, name="Hotels", category="Content", endpoint="admin_hotels"))
    admin.add_view(RestaurantView(Restaurant, db.session, name="Restaurants", category="Content", endpoint="admin_restaurants"))
    admin.add_view(SecureModelView(Category, db.session, name="Categories", category="Content", endpoint="admin_categories"))
    admin.add_view(LocalSellerView(LocalSeller, db.session, name="Local Sellers", category="Content", endpoint="admin_local_sellers"))
    admin.add_view(SecureModelView(Review, db.session, name="Reviews", category="Content", endpoint="admin_reviews"))
    admin.add_view(SecureModelView(FoodCategory, db.session, name="Food Categories", category="Content", endpoint="admin_food_categories"))
    admin.add_view(SecureModelView(FoodItem, db.session, name="Food Items", category="Content", endpoint="admin_food_items"))
    admin.add_view(NewsArticleView(NewsArticle, db.session, name="News & Updates", category="Content", endpoint="admin_news"))

    # ── Collector ────────────────────────────────────────────────────────────
    admin.add_view(DiscoveredEntityView(DiscoveredEntity, db.session, name="Review Queue", category="Discovery", endpoint="admin_discovery_queue"))
    admin.add_view(SecureModelView(CollectorLog, db.session, name="Collector Logs", category="Discovery", endpoint="admin_collector_logs"))

    # ── Events & Trails ───────────────────────────────────────────────────────
    admin.add_view(EventView(Event, db.session, name="Events", category="Events", endpoint="admin_events"))
    admin.add_view(SecureModelView(FoodTrail, db.session, name="Food Trails", category="Events", endpoint="admin_food_trails"))
    admin.add_view(SecureModelView(FoodTrailStop, db.session, name="Trail Stops", category="Events", endpoint="admin_trail_stops"))

    # ── Mobility ──────────────────────────────────────────────────────────────
    admin.add_view(DriverView(Driver, db.session, name="Drivers", category="Mobility", endpoint="admin_drivers"))
    admin.add_view(SecureModelView(Ride, db.session, name="Rides", category="Mobility", endpoint="admin_rides"))
    admin.add_view(SecureModelView(FareRule, db.session, name="Fare Rules", category="Mobility", endpoint="admin_fare_rules"))

    # ── Auth & Trust ──────────────────────────────────────────────────────────
    admin.add_view(SecureModelView(User, db.session, name="Users", category="Auth", endpoint="admin_users"))
    admin.add_view(SecureModelView(Document, db.session, name="Documents", category="Auth", endpoint="admin_documents"))
    admin.add_view(SecureModelView(ClaimRequest, db.session, name="Claim Requests", category="Auth", endpoint="admin_claim_requests"))

    # ── Support ───────────────────────────────────────────────────────────────
    admin.add_view(SupportView(SupportTicket, db.session, name="Support Tickets", category="Support", endpoint="admin_support"))

    return admin
