import requests
from bs4 import BeautifulSoup
from app.models import Temple, DiscoveredEntity
from app.database import db

class BaseCollector:
    def __init__(self, source_url):
        self.source_url = source_url
        self.discoveries = []
        
    def fetch_page(self):
        try:
            # Respect user-agent
            headers = {'User-Agent': 'Yatrik-Collector-Bot/1.0'}
            response = requests.get(self.source_url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.text
            return None
        except Exception as e:
            print(f"Error fetching {self.source_url}: {e}")
            return None

    def check_duplicate(self, name, city):
        # Basic exact/like match for duplication detection
        existing = Temple.query.filter(
            db.and_(
                Temple.name.ilike(f"%{name}%"),
                Temple.city.ilike(f"{city}")
            )
        ).first()
        return existing

    def save_discovery(self, entity_type, name, city, extracted_data):
        existing = self.check_duplicate(name, city)
        
        # Don't create if already in pending queue to avoid spam
        pending = DiscoveredEntity.query.filter_by(name=name, city=city, status='PENDING').first()
        if pending:
            return
            
        discovery = DiscoveredEntity(
            source_url=self.source_url,
            entity_type=entity_type,
            name=name,
            city=city,
            extracted_data=extracted_data,
            confidence=0.85 if existing else 0.50,
            status='DUPLICATE' if existing else 'PENDING',
            duplicate_of_id=existing.id if existing else None
        )
        db.session.add(discovery)
        self.discoveries.append(discovery)
