import click
import os
import tempfile
try:
    import fcntl
except ImportError:
    fcntl = None

from flask.cli import with_appcontext
from app.database import db
from app.models import Temple

# ====================================================================
# TEMPLE DATA SEEDING
# ====================================================================

REQUIRED_TEMPLES = [
    # Vrindavan (existing 5 are skipped due to idempotency)
    {"name": "Banke Bihari Temple", "city": "Vrindavan", "slug": "banke-bihari-temple"},
    {"name": "Prem Mandir", "city": "Vrindavan", "slug": "prem-mandir"},
    {"name": "ISKCON Vrindavan", "city": "Vrindavan", "slug": "iskcon-vrindavan"},
    {"name": "Radha Raman Temple", "city": "Vrindavan", "slug": "radha-raman-temple"},
    {"name": "Nidhivan", "city": "Vrindavan", "slug": "nidhivan"},
    {"name": "Radha Vallabh Temple", "city": "Vrindavan", "slug": "radha-vallabh-temple"},
    {"name": "Madan Mohan Temple", "city": "Vrindavan", "slug": "madan-mohan-temple"},
    {"name": "Govind Dev Ji Temple", "city": "Vrindavan", "slug": "govind-dev-ji-temple"},
    {"name": "Gopinath Temple", "city": "Vrindavan", "slug": "gopinath-temple"},
    {"name": "Shahji Temple", "city": "Vrindavan", "slug": "shahji-temple"},
    {"name": "Radha Damodar Temple", "city": "Vrindavan", "slug": "radha-damodar-temple"},
    {"name": "Radha Gokulananda Temple", "city": "Vrindavan", "slug": "radha-gokulananda-temple"},
    {"name": "Seva Kunj", "city": "Vrindavan", "slug": "seva-kunj"},

    # Mathura
    {"name": "Krishna Janmabhoomi", "city": "Mathura", "slug": "krishna-janmabhoomi"},
    {"name": "Dwarkadhish Temple", "city": "Mathura", "slug": "dwarkadhish-temple"},
    {"name": "Vishram Ghat", "city": "Mathura", "slug": "vishram-ghat"},

    # Braj
    {"name": "Govardhan Hill", "city": "Govardhan", "slug": "govardhan-hill"},
    {"name": "Radha Rani Temple", "city": "Barsana", "slug": "radha-rani-temple-barsana"},
    {"name": "Gokul", "city": "Gokul", "slug": "gokul"},
]

@click.command("seed-temples")
@with_appcontext
def seed_temples_command():
    """Seeds missing production temples safely (idempotent)."""
    added = 0
    skipped = 0

    for t_data in REQUIRED_TEMPLES:
        existing = Temple.query.filter_by(slug=t_data['slug']).first()
        if existing:
            skipped += 1
            continue
        
        # Only add safe facts. Historical claims and coordinates must be added by Admin later.
        new_temple = Temple(
            name=t_data['name'],
            slug=t_data['slug'],
            city=t_data['city'],
            verification_status="PUBLISHED"
        )
        db.session.add(new_temple)
        added += 1

    db.session.commit()
    click.echo(f"Seeding complete. Added {added}, Skipped {skipped} (already exist).")


# ====================================================================
# COLLECTOR CLI
# ====================================================================

def acquire_lock(lock_name="collector.lock"):
    """Lightweight file-based lock to prevent concurrent cron execution."""
    lock_path = os.path.join(tempfile.gettempdir(), lock_name)
    try:
        lock_file = open(lock_path, 'w')
        if os.name != 'nt':
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return lock_file
    except IOError:
        return None

@click.command("collect")
@click.option("--news", is_flag=True, help="Run only the News Collector")
@click.option("--all", is_flag=True, help="Run all available collectors")
@with_appcontext
def collect_command(news, all):
    """Triggers background collection pipeline via Cron."""
    
    lock_file = acquire_lock("yatrik_collector.lock")
    if not lock_file:
        click.echo("Collector is already running. Aborting to prevent overlapping runs.")
        return

    try:
        if news or all:
            click.echo("Starting News Collector...")
            from app.collectors.news_collector import NewsCollector, NEWS_SOURCES
            if not NEWS_SOURCES:
                click.echo("No enabled news sources configured.")
                return
            
            for source in NEWS_SOURCES:
                if not source.get("enabled", False):
                    continue
                click.echo(f"Collecting from {source['name']}...")
                collector = NewsCollector(source_url=source['url'])
                collector.collect()
            click.echo("News collection finished.")
    finally:
        if os.name != 'nt':
            fcntl.flock(lock_file, fcntl.LOCK_UN)
        lock_file.close()

def register_cli_commands(app):
    app.cli.add_command(seed_temples_command)
    app.cli.add_command(collect_command)
