#!/usr/bin/env python3
"""
Complete build script for LGS XML Windows installer
Creates both PyInstaller EXE and Inno Setup installer
"""

import subprocess
import sys
import os
import shutil
import json
from pathlib import Path

def build_exe():
    """Build the application using PyInstaller"""
    print("🏗️  Building EXE with PyInstaller...")
    
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
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ PyInstaller build successful!")
        
        # Verify build
        exe_path = Path("dist") / "LGS XML" / "LGS XML.exe"
        if exe_path.exists():
            print(f"📦 Executable created: {exe_path}")
            return True
        else:
            print("❌ Executable not found after build")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ PyInstaller not found. Install with: pip install pyinstaller")
        return False

def prepare_distribution_config():
    """Create a clean config.json for distribution"""
    print("⚙️  Preparing distribution config...")
    
    try:
        # Load current config
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        # Clean it up for distribution (remove user-specific paths)
        if "output_dir" in config:
            # Set to default path that will work for any user
            config["output_dir"] = "{USERPROFILE}\\Documents\\Pohoda XML"
        
        # Save clean config
        with open("config_distribution.json", "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print("✅ Distribution config created")
        return True
        
    except Exception as e:
        print(f"⚠️  Could not prepare config: {e}")
        # Copy original as fallback
        try:
            shutil.copy("config.json", "config_distribution.json")
            return True
        except:
            return False

def build_installer():
    """Build Windows installer using Inno Setup"""
    print("📦 Building Windows installer...")
    
    # Check if Inno Setup is available
    inno_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        r"C:\Program Files\Inno Setup 5\ISCC.exe",
    ]
    
    iscc_exe = None
    for path in inno_paths:
        if Path(path).exists():
            iscc_exe = path
            break
    
    if not iscc_exe:
        print("❌ Inno Setup not found!")
        print("📥 Download from: https://jrsoftware.org/isdl.php")
        print("💡 Install Inno Setup and run this script again")
        return False
    
    try:
        # Build installer
        cmd = [iscc_exe, "installer_script.iss"]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("✅ Installer build successful!")
        
        # Check output
        installer_path = Path("dist/installer/LGS-XML-Setup-1.0.0.exe")
        if installer_path.exists():
            size_mb = installer_path.stat().st_size / (1024 * 1024)
            print(f"📦 Installer created: {installer_path}")
            print(f"📏 Size: {size_mb:.1f} MB")
            return True
        else:
            print("❌ Installer file not found after build")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Installer build failed: {e}")
        if e.stdout:
            print("Output:", e.stdout)
        if e.stderr:
            print("Error:", e.stderr)
        return False

def create_distribution_package():
    """Create complete distribution package"""
    print("📋 Creating distribution package...")
    
    dist_dir = Path("dist/distribution")
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    files_to_copy = [
        ("dist/installer/LGS-XML-Setup-1.0.0.exe", "LGS-XML-Setup-1.0.0.exe"),
        ("README_distribution.md", "Quick-Start.md"),
        ("config_distribution.json", "config.json"),
    ]
    
    copied = 0
    for src, dst in files_to_copy:
        src_path = Path(src)
        dst_path = dist_dir / dst
        
        if src_path.exists():
            shutil.copy2(src_path, dst_path)
            print(f"✅ Copied: {dst}")
            copied += 1
        else:
            print(f"⚠️  Missing: {src}")
    
    if copied > 0:
        print(f"📦 Distribution package ready in: {dist_dir}")
        print("\n🚀 Files for client:")
        for file in dist_dir.glob("*"):
            if file.is_file():
                size_mb = file.stat().st_size / (1024 * 1024)
                print(f"   📄 {file.name} ({size_mb:.1f} MB)")
        return True
    else:
        print("❌ No files copied to distribution package")
        return False

def main():
    """Main build process"""
    print("🚀 LGS XML - Complete Build Process")
    print("=" * 50)
    
    success_steps = 0
    total_steps = 5
    
    # Step 1: Build EXE
    if build_exe():
        success_steps += 1
    
    # Step 2: Prepare config
    if prepare_distribution_config():
        success_steps += 1
    
    # Step 3: Build installer
    if build_installer():
        success_steps += 1
    
    # Step 4: Create distribution package
    if create_distribution_package():
        success_steps += 1
    
    # Step 5: Summary
    print("\n" + "=" * 50)
    print(f"📊 Build Summary: {success_steps}/{total_steps} steps completed")
    
    if success_steps == total_steps:
        print("🎉 BUILD SUCCESSFUL!")
        print("\n📦 Ready for client deployment:")
        print("   📁 dist/distribution/LGS-XML-Setup-1.0.0.exe")
        print("   📄 dist/distribution/Quick-Start.md")
        print("   ⚙️  dist/distribution/config.json")
        print("\n💡 Next steps:")
        print("   1. Test installer on clean Windows machine")
        print("   2. Upload to SharePoint or client's preferred location")
        print("   3. Send Quick-Start.md to client")
        success_steps += 1
    else:
        print("❌ BUILD INCOMPLETE - check errors above")
        
        if not Path("dist/installer/LGS-XML-Setup-1.0.0.exe").exists():
            print("\n💡 If Inno Setup is missing:")
            print("   1. Download from: https://jrsoftware.org/isdl.php")
            print("   2. Install Inno Setup")
            print("   3. Run this script again")
    
    return success_steps == total_steps

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1)
