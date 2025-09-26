#!/usr/bin/env python3
"""
Quick launcher for the Ergosign Dashboard
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit dashboard."""
    
    # Check if we're in the right directory
    if not os.path.exists('streamlit_dashboard.py'):
        print("❌ Error: streamlit_dashboard.py not found in current directory")
        print("Please run this script from the Ergosign-project folder")
        return
    
    print("🚀 Starting Ergosign Topic Gap Analysis Dashboard...")
    print("📊 Dashboard will open in your browser")
    print("🔄 Press Ctrl+C to stop the dashboard")
    print("-" * 50)
    
    try:
        # Launch Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "streamlit_dashboard.py",
            "--server.port=8501",
            "--server.headless=false"
        ])
    except KeyboardInterrupt:
        print("\n✅ Dashboard stopped")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")

if __name__ == "__main__":
    main()