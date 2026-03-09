# save as 'install_dependencies.py'

import subprocess
import sys
import os

def install_requirements():
    """Install all required packages"""
    
    print("Installing required packages...")
    
    # Upgrade pip first
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    # Install from requirements.txt
    if os.path.exists("requirements.txt"):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("\n✅ All packages installed successfully!")
    else:
        print("❌ requirements.txt not found!")
        return False
    
    # Verify installations
    print("\nVerifying installations...")
    packages = ["numpy", "cv2", "pywt", "PIL", "skimage", "matplotlib"]
    
    for package in packages:
        try:
            if package == "cv2":
                import cv2
                print(f"  ✓ OpenCV version: {cv2.__version__}")
            elif package == "pywt":
                import pywt
                print(f"  ✓ PyWavelets version: {pywt.__version__}")
            elif package == "PIL":
                from PIL import Image, ImageOps
                print(f"  ✓ Pillow is installed")
            elif package == "skimage":
                import skimage
                print(f"  ✓ scikit-image version: {skimage.__version__}")
            else:
                module = __import__(package)
                print(f"  ✓ {package} is installed")
        except ImportError as e:
            print(f"  ✗ {package} - NOT FOUND!")
    
    return True

if __name__ == "__main__":
    install_requirements()