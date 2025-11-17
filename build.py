#!/usr/bin/env python
"""
Build script for Download App.
Creates platform-specific distributable packages.

Usage:
    python build.py          # Build for current platform
    python build.py --windows
    python build.py --macos
    python build.py --linux
"""
import sys
import subprocess
from pathlib import Path
import shutil
import argparse


def check_dependencies():
    """Check if required build tools are installed."""
    try:
        import PyInstaller
        print(f"✓ PyInstaller found: {PyInstaller.__version__}")
    except ImportError:
        print("✗ PyInstaller not found. Install with: pip install pyinstaller")
        sys.exit(1)


def build_windows():
    """Build Windows executable using PyInstaller."""
    print("\n" + "="*60)
    print("Building Windows executable...")
    print("="*60)
    
    # Run PyInstaller
    result = subprocess.run([
        sys.executable, "-m", "PyInstaller",
        "download_app.spec",
        "--distpath", "dist",
        "--buildpath", "build",
    ])
    
    if result.returncode == 0:
        print("\n✓ Windows build complete!")
        print(f"  Executable: dist/DownloadApp/DownloadApp.exe")
    else:
        print("\n✗ Build failed!")
        sys.exit(1)


def build_macos():
    """Build macOS app bundle."""
    print("\n" + "="*60)
    print("Building macOS app bundle...")
    print("="*60)
    
    if sys.platform != "darwin":
        print("✗ macOS build only supported on macOS")
        return
    
    # Run PyInstaller
    result = subprocess.run([
        sys.executable, "-m", "PyInstaller",
        "download_app.spec",
        "--distpath", "dist",
        "--buildpath", "build",
    ])
    
    if result.returncode == 0:
        print("\n✓ macOS build complete!")
        print(f"  App bundle: dist/DownloadApp.app")
    else:
        print("\n✗ Build failed!")
        sys.exit(1)


def build_linux():
    """Build Linux AppImage or archive."""
    print("\n" + "="*60)
    print("Building Linux executable...")
    print("="*60)
    
    # Run PyInstaller
    result = subprocess.run([
        sys.executable, "-m", "PyInstaller",
        "download_app.spec",
        "--distpath", "dist",
        "--buildpath", "build",
    ])
    
    if result.returncode == 0:
        print("\n✓ Linux build complete!")
        print(f"  Executable: dist/DownloadApp/DownloadApp")
        print("\n  To create AppImage, install: sudo apt install appimagetool")
    else:
        print("\n✗ Build failed!")
        sys.exit(1)


def clean():
    """Remove build artifacts."""
    print("Cleaning build artifacts...")
    for path in ["build", "dist", "__pycache__"]:
        if Path(path).exists():
            print(f"  Removing {path}/...")
            shutil.rmtree(path)
    print("✓ Cleanup complete")


def main():
    parser = argparse.ArgumentParser(
        description="Build Download App distributable packages"
    )
    parser.add_argument(
        "--windows", action="store_true",
        help="Build for Windows"
    )
    parser.add_argument(
        "--macos", action="store_true",
        help="Build for macOS"
    )
    parser.add_argument(
        "--linux", action="store_true",
        help="Build for Linux"
    )
    parser.add_argument(
        "--clean", action="store_true",
        help="Clean build artifacts"
    )
    
    args = parser.parse_args()
    
    check_dependencies()
    
    if args.clean:
        clean()
        return
    
    # Build for current platform if no platform specified
    if not (args.windows or args.macos or args.linux):
        if sys.platform == "win32":
            build_windows()
        elif sys.platform == "darwin":
            build_macos()
        else:
            build_linux()
    else:
        if args.windows:
            build_windows()
        if args.macos:
            build_macos()
        if args.linux:
            build_linux()
    
    print("\n" + "="*60)
    print("Build process complete!")
    print("="*60)


if __name__ == "__main__":
    main()
