from app.database import db

class NewsArticle(db.Model):
    __tablename__ = "news_articles"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, index=True, nullable=False)
    
    summary = db.Column(db.Text)
    content = db.Column(db.Text)
    category = db.Column(db.String(100)) # e.g. Temple Updates, Festival Updates, Travel Updates
    
    # Location mapping
    location = db.Column(db.String(255))
    city = db.Column(db.String(100))
    
    # Source attribution
    source_name = db.Column(db.String(255))
    source_url = db.Column(db.String(500))
    
    # Dates
    published_at = db.Column(db.DateTime)
    collected_at = db.Column(db.DateTime, server_default=db.func.now())
    last_checked_at = db.Column(db.DateTime)
    
    image = db.Column(db.String(255))
    
    # SEO
    seo_title = db.Column(db.String(200))
    seo_description = db.Column(db.Text)
    canonical_url = db.Column(db.String(255))
    
    # Publishing State
    # DRAFT, REVIEW, PUBLISHED, UPDATED, ARCHIVED
    status = db.Column(db.String(20), default="DRAFT", index=True)
    is_featured = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f"<NewsArticle {self.title}>"
