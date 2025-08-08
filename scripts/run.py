#!/usr/bin/env python3
"""Simple script to run the User Management System."""

import sys
import subprocess
from pathlib import Path

def main():
    """Run the User Management System."""
    # Add src to Python path
    project_root = Path(__file__).parent.parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
    
    print("🧬 Starting User Management System...")
    print("📚 API Documentation will be available at: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/health")
    print("🌐 Frontend: Open index_new.html in your browser")
    print("=" * 60)
    
    try:
        # Run the FastAPI application
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "user_management.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ], cwd=src_path, check=True)
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()