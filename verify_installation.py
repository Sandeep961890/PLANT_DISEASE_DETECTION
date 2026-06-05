#!/usr/bin/env python3
"""
Installation Verification Script
Checks if all components are properly installed and configured.
"""

import os
import sys
import importlib
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    required = (3, 8)
    
    if version >= required:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} - Requires 3.8+")
        return False


def check_packages():
    """Check required packages"""
    print("\nChecking required packages...")
    
    packages = {
        'flask': 'Flask',
        'tensorflow': 'TensorFlow',
        'sklearn': 'scikit-learn',
        'cv2': 'OpenCV',
        'numpy': 'NumPy',
        'PIL': 'Pillow',
        'joblib': 'joblib',
        'requests': 'requests'
    }
    
    all_ok = True
    for module, name in packages.items():
        try:
            importlib.import_module(module)
            print(f"✅ {name:20} - OK")
        except ImportError:
            print(f"❌ {name:20} - NOT INSTALLED")
            all_ok = False
    
    return all_ok


def check_directories():
    """Check if required directories exist"""
    print("\nChecking directories...")
    
    required_dirs = [
        'outputs/banana',
        'outputs/corn',
        'outputs/sugarcane',
        'dataset',
        'templates',
        'static/css',
        'static/js'
    ]
    
    all_ok = True
    for dir_path in required_dirs:
        if os.path.isdir(dir_path):
            print(f"✅ {dir_path:30} - EXISTS")
        else:
            print(f"⚠️  {dir_path:30} - MISSING (will be created)")
            all_ok = True  # Not critical
    
    return all_ok


def check_models():
    """Check if trained models exist"""
    print("\nChecking trained models...")
    
    models = {
        'outputs/banana/banana_svm_model.pkl': 'Banana SVM Model',
        'outputs/banana/label_encoder.pkl': 'Banana Label Encoder',
        'outputs/corn/corn_svm_model.pkl': 'Corn SVM Model',
        'outputs/corn/label_encoder.pkl': 'Corn Label Encoder',
        'outputs/sugarcane/sugarcane_svm_model.pkl': 'Sugarcane SVM Model',
        'outputs/sugarcane/label_encoder.pkl': 'Sugarcane Label Encoder'
    }
    
    all_ok = True
    for model_path, name in models.items():
        if os.path.isfile(model_path):
            size = os.path.getsize(model_path) / (1024*1024)  # MB
            print(f"✅ {name:30} - OK ({size:.2f}MB)")
        else:
            print(f"❌ {name:30} - MISSING")
            all_ok = False
    
    return all_ok


def check_files():
    """Check if critical Python files exist"""
    print("\nChecking application files...")
    
    files = [
        'app.py',
        'config.py',
        'database.py',
        'feature_extractor.py',
        'predict_disease.py',
        'preprocess.py',
        'svm_classifier.py'
    ]
    
    all_ok = True
    for file_path in files:
        if os.path.isfile(file_path):
            print(f"✅ {file_path:30} - OK")
        else:
            print(f"❌ {file_path:30} - MISSING")
            all_ok = False
    
    return all_ok


def check_ports():
    """Check if required ports are available"""
    print("\nChecking ports...")
    
    import socket
    
    ports_to_check = {
        5000: 'Flask Application',
        11434: 'Ollama AI (optional)'
    }
    
    for port, name in ports_to_check.items():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result != 0:
            print(f"✅ {name:30} (Port {port}) - AVAILABLE")
        else:
            print(f"⚠️  {name:30} (Port {port}) - IN USE")


def test_imports():
    """Test if we can import main modules"""
    print("\nTesting module imports...")
    
    try:
        from feature_extractor import FeatureExtractor, build_model
        print("✅ feature_extractor - OK")
    except Exception as e:
        print(f"❌ feature_extractor - {str(e)[:50]}")
        return False
    
    try:
        from predict_disease import load_model, MODEL_CONFIG
        print("✅ predict_disease - OK")
    except Exception as e:
        print(f"❌ predict_disease - {str(e)[:50]}")
        return False
    
    try:
        from preprocess import preprocess_image, read_image_safe
        print("✅ preprocess - OK")
    except Exception as e:
        print(f"❌ preprocess - {str(e)[:50]}")
        return False
    
    try:
        from svm_classifier import train_and_save_svm
        print("✅ svm_classifier - OK")
    except Exception as e:
        print(f"❌ svm_classifier - {str(e)[:50]}")
        return False
    
    return True


def main():
    """Run all checks"""
    print_header("SMART AGRICULTURAL DISEASE DETECTION")
    print("Installation Verification\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Packages", check_packages),
        ("Directories", check_directories),
        ("Trained Models", check_models),
        ("Application Files", check_files),
        ("Port Availability", check_ports),
        ("Module Imports", test_imports)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error during check: {str(e)}")
            results.append((name, False))
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    total = len(results)
    passed = sum(1 for _, result in results if result)
    failed = total - passed
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if failed == 0:
        print("\n✅ All checks passed! Your installation is ready.")
        print("\nTo start the application, run:")
        print("  - Windows: run.bat")
        print("  - Linux/Mac: ./run.sh")
        print("  - Manual: python app.py")
        return 0
    else:
        print(f"\n⚠️  {failed} check(s) failed. Please review the issues above.")
        print("\nCommon fixes:")
        print("  - Install missing packages: pip install -r requirements.txt")
        print("  - Train models: python train_banana.py, etc.")
        print("  - Create directories: mkdir -p outputs/banana outputs/corn outputs/sugarcane")
        return 1


if __name__ == '__main__':
    sys.exit(main())
