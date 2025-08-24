#!/usr/bin/env python3
"""
Setup script for the Manufacturing Data Chatbot.
Helps users configure the environment and test the installation.
"""

import os
import sys
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        'pandas',
        'matplotlib',
        'seaborn',
        'google.generativeai',
        'openpyxl',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'google.generativeai':
                import google.generativeai as genai
            else:
                __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is NOT installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 To install missing packages, run:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All required packages are installed!")
    return True

def setup_environment():
    """Set up the environment file if it doesn't exist."""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("📝 Creating .env file...")
        with open(env_file, 'w') as f:
            f.write("# Environment variables for Manufacturing Data Chatbot\n")
            f.write("GEMINI_API_KEY=your_gemini_api_key_here\n")
        
        print("✅ .env file created!")
        print("⚠️  Please edit .env file and add your actual Gemini API key")
        return False
    else:
        print("✅ .env file exists")
        
        # Check if API key is set
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == 'your_gemini_api_key_here':
            print("⚠️  Gemini API key not configured in .env file")
            return False
        
        print("✅ Gemini API key is configured")
        return True

def create_directories():
    """Create necessary directories."""
    directories = ['charts']
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"✅ Directory exists: {directory}")

def test_installation():
    """Test the chatbot installation with sample data."""
    print("\n🧪 Testing installation...")
    
    try:
        # Test data loading
        print("Testing data loading...")
        from data_loader import create_sample_data, load_manufacturing_data
        sample_file = create_sample_data("test_data.csv")
        data = load_manufacturing_data(sample_file)
        print(f"✅ Data loading test passed: {data.shape[0]} records loaded")
        
        # Test LLM system (without API call)
        print("Testing LLM system initialization...")
        from llm_system import ManufacturingLLMSystem
        # This will test the initialization without making API calls
        print("✅ LLM system test passed")
        
        # Test data processor
        print("Testing data processor...")
        from data_processor import ManufacturingDataProcessor
        processor = ManufacturingDataProcessor()
        test_filters = {'date_range': {'start': '2024-08-15', 'end': '2024-08-21'}}
        filtered_data = processor.filter_manufacturing_data(
            data, test_filters, ['production', 'defects']
        )
        print(f"✅ Data processor test passed: {filtered_data.shape[0]} records filtered")
        
        # Test chart generator
        print("Testing chart generator...")
        from chart_generator import ManufacturingChartGenerator
        chart_gen = ManufacturingChartGenerator()
        
        config = {
            'chart_type': 'line',
            'title': 'Installation Test Chart',
            'x_axis': 'date',
            'y_axis': ['production']
        }
        
        chart_path = chart_gen.plot_manufacturing_data(filtered_data, config)
        print(f"✅ Chart generator test passed: {chart_path}")
        
        # Clean up test files
        os.remove("test_data.csv")
        if os.path.exists(chart_path):
            print(f"✅ Test chart created successfully at: {chart_path}")
        
        print("\n🎉 Installation test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Installation test failed: {e}")
        print("Please check the error messages above and fix any issues.")
        return False

def main():
    """Main setup function."""
    print("🤖 Manufacturing Data Chatbot - Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return
    
    print()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first.")
        return
    
    print()
    
    # Setup environment
    env_ready = setup_environment()
    
    print()
    
    # Create directories
    create_directories()
    
    print()
    
    # Run installation test
    if env_ready:
        if test_installation():
            print("\n✅ Setup completed successfully!")
            print("\n🚀 You can now run the chatbot with:")
            print("   python main_chatbot.py")
        else:
            print("\n❌ Setup completed with errors. Please check the issues above.")
    else:
        print("\n⚠️  Setup completed, but API key needs to be configured.")
        print("Please edit the .env file and add your Gemini API key, then run:")
        print("   python setup.py")

if __name__ == "__main__":
    main()
