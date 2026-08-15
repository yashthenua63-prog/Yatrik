import requests
import socket
import ipaddress
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from app.models import Temple, DiscoveredEntity
from app.database import db

def is_safe_url(url):
    """
    Validates that the URL scheme is safe and its resolved IP is public.
    Prevents SSRF targeting localhost, private subnets, or metadata endpoints.
    """
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        return False
        
    hostname = parsed.hostname
    if not hostname:
        return False
        
    try:
        # Resolve hostname to IPv4/IPv6
        ip_str = socket.gethostbyname(hostname)
        ip = ipaddress.ip_address(ip_str)
        
        # Block private, loopback, and cloud metadata (169.254.x.x)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast:
            return False
            
        return True
    except (socket.gaierror, ValueError):
        # DNS resolution failed or invalid IP
        return False

class BaseCollector:
    def __init__(self, source_url):
        self.source_url = source_url
        self.discoveries = []
        
    def fetch_page(self):
        try:
            headers = {'User-Agent': 'Yatrik-Collector-Bot/1.0'}
            
            # Manual redirect following to validate each hop
            current_url = self.source_url
            for _ in range(3):
                if not is_safe_url(current_url):
                    print(f"SSRF Blocked: URL resolved to a private/unsafe IP -> {current_url}")
                    return None
                    
                response = requests.get(current_url, headers=headers, timeout=10, allow_redirects=False)
                
                if response.status_code in (301, 302, 303, 307, 308):
                    current_url = response.headers.get('Location')
                    if not current_url:
                        break
                    
                    # Handle relative redirects
                    if not current_url.startswith('http'):
                        from urllib.parse import urljoin
                        current_url = urljoin(response.url, current_url)
                    continue
                    
                if response.status_code == 200:
                    return response.text
                break
                
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
