import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from main import app

print("Registered Routes:")
for route in app.routes:
    if hasattr(route, "path") and "priorities" in route.path:
        print(f"{route.methods} {route.path}")
