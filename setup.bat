@echo off
echo Manufacturing Data Chatbot - Windows Setup
echo ==========================================

echo.
echo 1. Installing required packages...
pip install pandas matplotlib seaborn google-generativeai openpyxl python-dotenv

echo.
echo 2. Setting up configuration...
python config.py

echo.
echo 3. Setup complete! You can now run the chatbot with:
echo    python main_chatbot.py
echo.
echo Or try the demo:
echo    python demo.py
echo.
pause
