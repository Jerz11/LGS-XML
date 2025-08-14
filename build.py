#!/usr/bin/env python3
"""
Build script for LGS XML application using PyInstaller
"""

import subprocess
import sys
import os
from pathlib import Path

def build_application():
    """Build the application using PyInstaller"""
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onedir", 
        "--windowed",
        "--name", "LGS XML",
        "main.py"
    ]
    
    # Add icon if available
    icon_path = Path("icon.ico")
    if icon_path.exists():
        cmd.insert(-1, "--icon")
        cmd.insert(-1, str(icon_path))
    
    print("Building LGS XML application...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        print(result.stdout)
        
        # Print location of built application
        dist_path = Path("dist") / "LGS XML"
        if dist_path.exists():
            print(f"\nApplication built in: {dist_path.absolute()}")
            print(f"Executable: {dist_path / 'LGS XML.exe'}")
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: PyInstaller not found. Install it with: pip install pyinstaller")
        sys.exit(1)

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if "--deps" in sys.argv:
        install_dependencies()
    
    build_application()
