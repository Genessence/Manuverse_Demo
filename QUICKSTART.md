# Universal Data Analysis Chatbot - Quick Start Guide

## 🚀 Super Quick Setup (3 minutes)

### Option 1: Web Interface (Recommended)

1. **Install & Configure**
   ```bash
   pip install -r requirements.txt
   python config.py
   ```

2. **Start the Application**
   ```bash
   python start_server.py
   ```

3. **Use the Web Interface**
   - Opens automatically at http://localhost:8080
   - Drag & drop your data file (CSV/Excel)
   - Start asking questions!

### Option 2: Command Line

1. **Setup**
   ```bash
   pip install -r requirements.txt
   python config.py
   ```

2. **Run with your data**
   ```bash
   python main_chatbot.py your_data.csv
   ```

## 🔑 Get Your API Key (One-time setup)

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Create API key
4. Run `python config.py` and paste your key

## 📊 What Data Can You Analyze?

**Any structured data in CSV or Excel format!**

Examples:
- 📈 **Sales Data**: Revenue, customers, products, regions
- 🏭 **Operations Data**: Production, quality, efficiency, costs
- 💰 **Financial Data**: Expenses, budgets, investments, transactions
- 👥 **HR Data**: Employees, performance, attendance, salaries  
- 🌐 **Web Analytics**: Traffic, conversions, user behavior
- 📋 **Survey Data**: Responses, ratings, demographics
- 🔬 **Research Data**: Experiments, measurements, observations

**No predefined format required** - the AI automatically detects:
- Date columns
- Numeric measures
- Categories
- Quality metrics
- Identifiers

## 💬 Example Questions for Any Dataset

### General Analysis
- "Show me the trend over time"
- "What are the top 10 items by value?"
- "Summarize the key metrics"
- "Show me the distribution of values"

### Comparisons
- "Compare performance between categories"
- "Which group has the highest values?"
- "Show differences between time periods"

### Patterns & Insights
- "Find correlations between variables"
- "Identify outliers or unusual values"
- "Show seasonal patterns"
- "What factors affect the main metric?"

### Business-Specific Examples

**For Sales Data:**
- "Which products are top performers?"
- "Show sales trends by region"
- "Compare this quarter to last quarter"

**For Operational Data:**
- "Show efficiency trends over time"
- "Which process has the most issues?"
- "Compare performance by shift/team"

**For Financial Data:**
- "Where are we spending the most?"
- "Show budget vs actual spending"
- "Track expense trends by category"

## 🌐 Web Interface Features

### Upload
- **Drag & Drop**: Simply drag your file onto the upload area
- **Auto-Detection**: Instantly analyzes your data structure
- **File Support**: CSV, Excel (.xlsx, .xls)

### Analysis
- **Natural Language**: Ask questions like you would to a human analyst
- **Real-time Results**: Get insights and charts immediately
- **Interactive**: Click example questions to get started

### Charts
- **Auto-Generated**: Appropriate chart types based on your query
- **High Quality**: Professional visualizations you can download
- **Context-Aware**: Charts that make sense for your data type

## 🔧 API Integration

For developers wanting to integrate the chatbot:

```python
import requests

# Upload data
files = {'file': open('data.csv', 'rb')}
upload_response = requests.post('http://localhost:8000/upload', files=files)
session_id = upload_response.json()['session_id']

# Query data
query = {
    'session_id': session_id,
    'query': 'Show me the trend over time'
}
response = requests.post('http://localhost:8000/query', json=query)
print(response.json()['response'])
```

## � Troubleshooting

**"Can't connect to server"**
- Run `python start_server.py`
- Check http://localhost:8080 opens

**"API key error"**  
- Run `python config.py` to set up your key
- Or edit `.env` file manually

**"No analysis generated"**
- Check your data has multiple columns
- Try more specific questions
- Ensure data file isn't corrupted

## 🎉 You're Ready!

1. ✅ **Upload any dataset** (CSV/Excel)
2. ✅ **Ask questions in plain English**
3. ✅ **Get AI-powered insights and charts**
4. ✅ **Discover patterns in your data**

The chatbot automatically understands your data structure and provides relevant analysis. No technical setup or data preparation required!
