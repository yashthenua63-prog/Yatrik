from .base import BaseCollector
from app.models.news import NewsArticle
from app.models.collector import DiscoveredEntity
from app.database import db

# ==========================================
# NEWS SOURCES CONFIGURATION
# Add legitimate public sources here.
# DO NOT add unsupported/fake sources.
# ==========================================
NEWS_SOURCES = [
    # Example structure (Disabled until verified):
    # {
    #     "name": "UP Tourism Mathura",
    #     "url": "https://uptourism.gov.in/en/mathura",
    #     "type": "Tourism Department",
    #     "location": "Mathura",
    #     "enabled": False,
    #     "rate_limit": 1.0,  # seconds
    #     "timeout": 10       # seconds
    # }
]

class NewsCollector(BaseCollector):
    def check_duplicate(self, title, city):
        existing = NewsArticle.query.filter(
            db.and_(
                NewsArticle.title.ilike(f"%{title}%"),
                NewsArticle.city.ilike(f"{city}")
            )
        ).first()
        return existing

    def save_discovery(self, entity_type, title, city, extracted_data):
        existing = self.check_duplicate(title, city)
        
        # Don't create if already in pending queue to avoid spam
        pending = DiscoveredEntity.query.filter_by(name=title, city=city, status='PENDING').first()
        if pending:
            return
            
        # Freshness Check (If it exists, but data differs, flag as Potential Update)
        is_update = False
        if existing:
            # Here we can add logic to compare extracted_data against existing.content
            # For simplicity, if we hit the same URL/title but it's re-scraped, we flag it.
            is_update = True
            
        discovery = DiscoveredEntity(
            source_url=self.source_url,
            entity_type=entity_type,
            name=title, # We map title to name
            city=city,
            extracted_data=extracted_data,
            confidence=0.85 if existing else 0.50,
            status='DUPLICATE' if is_update else 'PENDING',
            duplicate_of_id=existing.id if existing else None
        )
        db.session.add(discovery)
        self.discoveries.append(discovery)
        
    def collect(self):
        # Example collection logic
        html = self.fetch_page()
        if not html:
            return False
            
        # Stub: Beautiful soup logic to parse news
        # self.save_discovery("NewsArticle", "Temple Timing Changed", "Vrindavan", {"summary": "New timings are 7:30 AM"})
        db.session.commit()
        return True
