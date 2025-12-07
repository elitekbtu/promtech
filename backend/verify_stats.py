import sys
from pathlib import Path
import os

# Add backend to path
sys.path.append('/backend')

from database import SessionLocal
from services.objects.service import WaterObjectService

db = SessionLocal()
try:
    counts = WaterObjectService.count_by_priority_level(db)
    print(f"Counts: {counts}")
finally:
    db.close()
