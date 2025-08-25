

import os
import sys
import subprocess
import webbrowser
from pathlib import Path
import time
import threading

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        'fastapi',
        'uvicorn',
        'pandas',
        # 'google.generativeai'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_').replace('.', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing required packages: {', '.join(missing)}")
        print("Install them with: pip install -r requirements.txt")
        return False
    
    return True

def check_api_key():
    """Check if Gemini API key is configured."""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == 'your_gemini_api_key_here':
        print("⚠️  Warning: Gemini API key not configured!")
        print("The chatbot will work with limited functionality.")
        print("Configure your API key in the .env file or run: python config.py")
        return False
    
    return True

def create_directories():
    """Create necessary directories."""
    dirs = ['sessions', 'charts']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)

def start_api_server():
    """Start the FastAPI server."""
    print("🚀 Starting API server...")
    
    try:
        import uvicorn
        uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=False, log_level="info")
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

def serve_web_interface():
    """Serve the React web interface directly from frontend directory."""
    import http.server
    import socketserver
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return
    
    # Check if frontend is built
    build_dir = frontend_dir / "build"
    if not build_dir.exists():
        print("❌ Frontend build directory not found. Please run 'npm run build' in the frontend directory first.")
        return
    
    # Create a custom handler for React routing
    class ReactHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            # Handle React Router - serve index.html for all routes
            if not self.path.startswith('/static/') and not self.path.startswith('/api/'):
                self.path = '/index.html'
            return super().do_GET()
    
    os.chdir("frontend/build")
    
    try:
        with socketserver.TCPServer(("", 8080), ReactHandler) as httpd:
            print("🌐 React Web interface available at: http://localhost:8080")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Web server stopped")
    except Exception as e:
        print(f"❌ Error starting web server: {e}")

def open_browser():
    """Open the web browser after a short delay."""
    time.sleep(3)  # Wait for servers to start
    try:
        webbrowser.open("http://localhost:8080")
    except Exception as e:
        print(f"Could not open browser automatically: {e}")
        print("Please open http://localhost:8080 in your browser")

def main():
    """Main startup function."""
    print("🤖 Universal Data Analysis Chatbot")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check API key
    api_configured = check_api_key()
    
    # Create directories
    create_directories()
    
    print("\n📊 Starting Universal Data Analysis Chatbot...")
    print("API Server: http://localhost:8000")
    print("React Frontend: http://localhost:8080")
    print("\nPress Ctrl+C to stop")
    print("=" * 50)
    
    # Start browser in a separate thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start web server in a separate thread
    web_thread = threading.Thread(target=serve_web_interface)
    web_thread.daemon = True
    web_thread.start()
    
    # Start API server (this will block)
    try:
        start_api_server()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")

if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--api-only":
            # Run only API server
            if check_dependencies():
                create_directories()
                start_api_server()
        elif sys.argv[1] == "--web-only":
            # Run only web server
            serve_web_interface()
        elif sys.argv[1] == "--help":
            print("""
Universal Data Analysis Chatbot - Startup Options:

python start_server.py              # Start both API and web interface
python start_server.py --api-only   # Start only API server
python start_server.py --web-only   # Start only web interface
python start_server.py --help       # Show this help

Alternative ways to run:
python api.py                       # Direct API server start
python main_chatbot.py              # Command-line chatbot interface
""")
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for available options")
    else:
        main()
