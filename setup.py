#!/usr/bin/env python3
"""
Setup script for Q&A System (RAG Application)
This script helps you set up the project quickly.
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n📋 {description}")
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ Success!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(f"Output: {e.output}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_path = Path(".env")
    if not env_path.exists():
        print("\n📝 Creating .env file template...")
        env_content = """# Azure OpenAI Configuration (for LLM responses)
AZURE_OPENAI_API_BASE=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_API_VERSION=2024-06-01
AZURE_OPENAI_DEPLOYMENT_NAME=your-gpt-deployment-name

# Optional: OpenAI API (alternative to Hugging Face embeddings)
# OPENAI_API_KEY=your-openai-api-key-here
"""
        with open(env_path, 'w') as f:
            f.write(env_content)
        print("✅ Created .env file template")
        print("⚠️  Please edit .env file with your actual API credentials")
        return True
    else:
        print("✅ .env file already exists")
        return True

def main():
    print("🚀 Q&A System (RAG Application) Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Please upgrade Python.")
        return False
    
    print(f"✅ Python {sys.version} detected")
    
    # Create virtual environment
    if not Path(".venv").exists():
        if not run_command(f"{sys.executable} -m venv .venv", "Creating virtual environment"):
            return False
    else:
        print("✅ Virtual environment already exists")
    
    # Determine activation command
    if os.name == 'nt':  # Windows
        activate_cmd = ".venv\\Scripts\\activate"
        python_cmd = ".venv\\Scripts\\python"
    else:  # Unix/Linux/MacOS
        activate_cmd = "source .venv/bin/activate"
        python_cmd = ".venv/bin/python"
    
    # Install requirements
    if not run_command(f"{python_cmd} -m pip install --upgrade pip", "Upgrading pip"):
        return False
    
    if not run_command(f"{python_cmd} -m pip install -r requirements.txt", "Installing dependencies"):
        return False
    
    # Create .env file
    create_env_file()
    
    # Create necessary directories
    directories = [
        "src/backend/data/chunks",
        "src/backend/data/pdfs", 
        "src/backend/data/webs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    print("✅ Created data directories")
    
    print("\n🎉 Setup Complete!")
    print("\n📋 Next Steps:")
    print("1. Edit .env file with your Azure OpenAI credentials")
    print("2. Activate virtual environment:")
    print(f"   {activate_cmd}")
    print("3. Start the backend:")
    print("   cd src/backend/api && python main.py")
    print("4. Start the frontend (new terminal):")
    print("   cd src/frontend && streamlit run app.py")
    print("\n🌐 Then visit http://localhost:8501 to use the application!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
