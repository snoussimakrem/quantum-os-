import sys
import os
from pathlib import Path

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

# Change to project root so .env is found
os.chdir(os.path.dirname(__file__))

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "quantum_os.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
