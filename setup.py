#!/usr/bin/env python
"""
Setup script for the GenAI Labs API.
This script helps set up the development environment.
"""
import os
import sys
import subprocess
from pathlib import Path

def run_command(command: str, description: str):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"✅ {description} completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        sys.exit(1)

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def create_env_file():
    """Create .env file from template if it doesn't exist."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("🔄 Creating .env file from template...")
        env_file.write_text(env_example.read_text())
        print("✅ .env file created")
        print("⚠️  Please edit .env file with your actual configuration")
    else:
        print("ℹ️  .env file already exists")

def main():
    """Main setup function."""
    print("🚀 Setting up GenAI Labs API...")
    
    # Check Python version
    check_python_version()
    
    # Create virtual environment
    if not Path("venv").exists():
        run_command("python -m venv venv", "Creating virtual environment")
    else:
        print("ℹ️  Virtual environment already exists")
    
    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        python_exe = os.path.join("venv", "Scripts", "python.exe")
        pip_exe = os.path.join("venv", "Scripts", "pip.exe")
    else:  # macOS/Linux
        python_exe = os.path.join("venv", "bin", "python")
        pip_exe = os.path.join("venv", "bin", "pip")
    
    # Use the virtual environment's python/pip directly instead of activation
    run_command(f'"{python_exe}" -m pip install --upgrade pip', "Upgrading pip")
    run_command(f'"{pip_exe}" install -r requirements.txt', "Installing dependencies")
    
    # Create .env file
    create_env_file()
    
    # Create necessary directories
    dirs_to_create = ["chroma_db", "logs"]
    for dir_name in dirs_to_create:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✅ Created directory: {dir_name}")
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file with your OpenAI API key")
    print("2. Activate virtual environment:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("3. Run the application:")
    print("   python run.py")

if __name__ == "__main__":
    main()
