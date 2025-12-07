import sys
from pathlib import Path
import os

# Add backend to path
sys.path.append('/backend')

from database import SessionLocal
from models import WaterObject

db = SessionLocal()
try:
    # Get a few objects with pdf_url
    objects = db.query(WaterObject).filter(WaterObject.pdf_url.isnot(None)).limit(5).all()
    for obj in objects:
        print(f"ID: {obj.id}, Name: {obj.name}, PDF URL: {obj.pdf_url}")
finally:
    db.close()
