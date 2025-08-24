"""
Configuration utility for Manufacturing Data Chatbot.
Helps users set up their Gemini API key and test the configuration.
"""

import os
import getpass
from pathlib import Path

def get_api_key_instructions():
    """Display instructions for obtaining a Gemini API key."""
    print("""
🔑 How to Get Your Gemini API Key:

1. Go to https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key
5. Keep it secure and don't share it publicly

📝 Note: You may need to enable the Generative Language API in your Google Cloud Console.
""")

def setup_api_key():
    """Interactive setup for API key."""
    env_file = Path(".env")
    
    print("🔧 Setting up your Gemini API Key")
    print("=" * 40)
    
    # Check if .env exists
    current_key = None
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('GEMINI_API_KEY='):
                    current_key = line.split('=', 1)[1].strip()
                    break
    
    if current_key and current_key != 'your_gemini_api_key_here':
        print(f"✅ API key is already configured: {current_key[:8]}...")
        
        choice = input("\nWould you like to update it? (y/N): ").lower()
        if choice not in ['y', 'yes']:
            return current_key
    
    # Get new API key
    print("\n" + "="*50)
    get_api_key_instructions()
    print("="*50)
    
    while True:
        api_key = getpass.getpass("🔑 Enter your Gemini API Key (input hidden): ").strip()
        
        if not api_key:
            print("❌ API key cannot be empty!")
            continue
        
        if len(api_key) < 20:  # Basic validation
            print("❌ API key seems too short. Please check and try again.")
            continue
        
        # Confirm the key
        print(f"✅ API key entered: {api_key[:8]}...")
        confirm = input("Is this correct? (Y/n): ").lower()
        if confirm in ['', 'y', 'yes']:
            break
    
    # Save to .env file
    env_content = f"# Environment variables for Manufacturing Data Chatbot\nGEMINI_API_KEY={api_key}\n"
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"✅ API key saved to {env_file}")
    return api_key

def test_api_connection(api_key):
    """Test the API connection."""
    print("\n🧪 Testing API Connection...")
    
    try:
        import google.generativeai as genai
        
        # Configure the API
        genai.configure(api_key=api_key)
        
        # Test with a simple request
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content("Say 'API connection successful'")
        
        if response and response.text:
            print("✅ API connection successful!")
            print(f"   Response: {response.text.strip()}")
            return True
        else:
            print("❌ API connection failed: No response received")
            return False
            
    except ImportError:
        print("❌ google-generativeai package not installed")
        print("   Run: pip install google-generativeai")
        return False
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False

def main():
    """Main configuration function."""
    print("🤖 Manufacturing Data Chatbot - Configuration")
    print("=" * 60)
    
    # Setup API key
    api_key = setup_api_key()
    
    if api_key:
        # Test the connection
        if test_api_connection(api_key):
            print("\n🎉 Configuration completed successfully!")
            print("\n🚀 You can now run the chatbot:")
            print("   python main_chatbot.py")
            print("\n📚 Or see examples:")
            print("   python demo.py --examples")
        else:
            print("\n⚠️  Configuration saved but API test failed.")
            print("Please check your API key and try again.")
    else:
        print("\n❌ Configuration cancelled.")

if __name__ == "__main__":
    main()
