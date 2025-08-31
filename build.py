#!/usr/bin/env python3
"""
Build script for the Code Review Application.

This script handles building the C++ performance modules and setting up the application.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def run_command(cmd, cwd=None, check=True):
    """Run a command and handle errors."""
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    try:
        result = subprocess.run(
            cmd if isinstance(cmd, list) else cmd.split(),
            cwd=cwd,
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        return False

def check_requirements():
    """Check if all build requirements are available."""
    print_header("Checking Build Requirements")
    
    requirements = {
        'python': ['python', '--version'],
        'cmake': ['cmake', '--version'],
        'c++_compiler': ['g++' if platform.system() != 'Windows' else 'cl', '--version'] if platform.system() != 'Windows' else ['cl'],
    }
    
    missing = []
    for name, cmd in requirements.items():
        print(f"Checking {name}...")
        if not run_command(cmd, check=False):
            missing.append(name)
            print(f"  ❌ {name} not found")
        else:
            print(f"  ✅ {name} available")
    
    if missing:
        print(f"\nMissing requirements: {', '.join(missing)}")
        print("\nPlease install:")
        if 'cmake' in missing:
            print("  - CMake: https://cmake.org/download/")
        if 'c++_compiler' in missing:
            if platform.system() == 'Windows':
                print("  - Visual Studio Build Tools or Visual Studio Community")
            else:
                print("  - GCC/Clang compiler (usually in build-essential package)")
        return False
    
    print("\n✅ All requirements satisfied!")
    return True

def install_python_dependencies():
    """Install Python dependencies."""
    print_header("Installing Python Dependencies")
    
    if not run_command([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt']):
        print("❌ Failed to install Python dependencies")
        return False
    
    print("✅ Python dependencies installed successfully!")
    return True

def build_cpp_module():
    """Build the C++ performance module."""
    print_header("Building C++ Performance Module")
    
    # Create build directory
    build_dir = Path('build')
    build_dir.mkdir(exist_ok=True)
    
    # Configure with CMake
    print("Configuring with CMake...")
    cmake_cmd = ['cmake', '..']
    if platform.system() == 'Windows':
        cmake_cmd.extend(['-G', 'Visual Studio 16 2019'])
    
    if not run_command(cmake_cmd, cwd=build_dir):
        print("❌ CMake configuration failed")
        return False
    
    # Build
    print("Building C++ module...")
    build_cmd = ['cmake', '--build', '.', '--config', 'Release']
    if not run_command(build_cmd, cwd=build_dir):
        print("❌ C++ module build failed")
        return False
    
    # Copy the built module to the project root
    if platform.system() == 'Windows':
        module_pattern = 'core_performance*.pyd'
        src_dir = build_dir / 'Release'
    else:
        module_pattern = 'core_performance*.so'
        src_dir = build_dir
    
    import glob
    built_modules = glob.glob(str(src_dir / module_pattern))
    
    if not built_modules:
        print(f"❌ No built modules found matching {module_pattern}")
        return False
    
    import shutil
    for module in built_modules:
        dest = Path(module).name
        shutil.copy2(module, dest)
        print(f"✅ Copied {module} to {dest}")
    
    print("✅ C++ performance module built successfully!")
    return True

def build_with_setup_py():
    """Alternative build method using setup.py."""
    print_header("Building C++ Module with setup.py (Fallback)")
    
    if not run_command([sys.executable, 'setup.py', 'build_ext', '--inplace']):
        print("❌ setup.py build failed")
        return False
    
    print("✅ C++ module built successfully with setup.py!")
    return True

def test_installation():
    """Test if the installation was successful."""
    print_header("Testing Installation")
    
    # Test Python imports
    test_imports = [
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'requests',
        'pybind11',
    ]
    
    for module in test_imports:
        try:
            __import__(module)
            print(f"✅ {module} import successful")
        except ImportError as e:
            print(f"❌ {module} import failed: {e}")
            return False
    
    # Test C++ module
    try:
        import core_performance
        streamer = core_performance.AdaptiveTextStreamer()
        processor = core_performance.FileProcessor()
        print("✅ C++ performance module loaded successfully")
    except ImportError:
        print("⚠️  C++ performance module not available (will use Python fallback)")
    except Exception as e:
        print(f"⚠️  C++ performance module error: {e}")
    
    print("\n✅ Installation test completed!")
    return True

def create_run_script():
    """Create a convenient run script."""
    print_header("Creating Run Scripts")
    
    # Windows batch file
    if platform.system() == 'Windows':
        run_script = """@echo off
cd /d "%~dp0"
python app.py %*
pause
"""
        with open('run.bat', 'w') as f:
            f.write(run_script)
        print("✅ Created run.bat")
    
    # Unix shell script
    run_script = """#!/bin/bash
cd "$(dirname "$0")"
python3 app.py "$@"
"""
    with open('run.sh', 'w') as f:
        f.write(run_script)
    
    # Make executable on Unix systems
    if platform.system() != 'Windows':
        os.chmod('run.sh', 0o755)
        print("✅ Created run.sh")
    
    print("Use 'python app.py' or the run scripts to start the application")

def main():
    """Main build process."""
    print_header("Code Review Assistant - Build Script")
    print(f"Platform: {platform.system()} {platform.machine()}")
    print(f"Python: {sys.version}")
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    steps = [
        ("Check Requirements", check_requirements),
        ("Install Python Dependencies", install_python_dependencies),
        ("Build C++ Module", build_cpp_module),
        ("Test Installation", test_installation),
        ("Create Run Scripts", create_run_script),
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            # Try fallback for C++ build
            if step_name == "Build C++ Module":
                print("Trying fallback build method...")
                if not build_with_setup_py():
                    print(f"❌ {step_name} failed completely")
                    print("\nThe application will still work but without C++ optimizations.")
                    # Continue with remaining steps
            elif step_name in ["Check Requirements", "Install Python Dependencies"]:
                print(f"❌ Critical step '{step_name}' failed. Cannot continue.")
                return 1
    
    print_header("Build Complete!")
    print("🎉 Code Review Assistant has been built successfully!")
    print("\nTo run the application:")
    print("  python app.py")
    if platform.system() != 'Windows':
        print("  ./run.sh")
    else:
        print("  run.bat")
    
    print("\nBefore running, make sure Ollama is installed and running:")
    print("  ollama pull qwen2.5-coder")
    print("  ollama run qwen2.5-coder")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())